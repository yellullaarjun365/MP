from pathlib import Path
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from faster_whisper import WhisperModel

from app.services.voice_normalization import (
    normalize_voice_transcript,
)


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


MODEL_NAME = "tiny"

print("Loading Whisper model...")

whisper_model = WhisperModel(
    MODEL_NAME,
    device="cpu",
    compute_type="int8",
)

print("Whisper model loaded.")


ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg",
    ".flac",
}


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
):
    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        suffix = ".webm"

    try:
        audio_bytes = await file.read()

        if not audio_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty audio file.",
            )

        if len(audio_bytes) > 15 * 1024 * 1024:
            raise HTTPException(
                status_code=413,
                detail=(
                    "Audio file is too large. "
                    "Maximum size is 15 MB."
                ),
            )

        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:

            temp_file.write(audio_bytes)
            temp_path = Path(
                temp_file.name
            )

        try:
            segments, info = whisper_model.transcribe(
                str(temp_path),
                language="en",
                beam_size=1,
                vad_filter=True,
            )

            parts = []

            for segment in segments:
                segment_text = segment.text.strip()

                if segment_text:
                    parts.append(segment_text)

            raw_transcript = " ".join(
                parts
            ).strip()

        finally:
            temp_path.unlink(
                missing_ok=True
            )

        if not raw_transcript:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Could not detect speech "
                    "in the audio."
                ),
            )

        normalized_transcript = (
            normalize_voice_transcript(
                raw_transcript
            )
        )

        return {
            "text": normalized_transcript,
            "raw_text": raw_transcript,
            "language": info.language,
            "language_probability": (
                info.language_probability
            ),
            "model": MODEL_NAME,
            "normalized": (
                normalized_transcript
                != raw_transcript
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {exc}",
        ) from exc
