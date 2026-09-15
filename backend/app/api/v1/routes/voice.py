from pathlib import Path
import tempfile
from threading import Lock

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from faster_whisper import WhisperModel

from app.schemas.voice import (
    VoiceTranscriptionResponse,
)
from app.services.voice_normalization import (
    normalize_voice_transcript,
)


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


# Multilingual model.
# base is a better starting point than tiny for
# Telugu while remaining practical on CPU.
MODEL_NAME = "base"

_whisper_model = None
_whisper_lock = Lock()


def get_whisper_model() -> WhisperModel:

    global _whisper_model

    if _whisper_model is None:

        with _whisper_lock:

            if _whisper_model is None:

                print(
                    f"Loading Whisper {MODEL_NAME} model..."
                )

                _whisper_model = WhisperModel(
                    MODEL_NAME,
                    device="cpu",
                    compute_type="int8",
                )

                print(
                    f"Whisper {MODEL_NAME} model loaded."
                )

    return _whisper_model


ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg",
    ".flac",
}


LANGUAGE_MAP = {
    "auto": None,
    "en": "en",
    "te": "te",
}


@router.post(
    "/transcribe",
    response_model=VoiceTranscriptionResponse,
)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("auto"),
):
    language = language.lower().strip()

    if language not in LANGUAGE_MAP:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported language. "
                "Use auto, en, or te."
            ),
        )

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

            forced_language = (
                LANGUAGE_MAP[language]
            )

            model = get_whisper_model()

            segments, info = (
                model.transcribe(
                    str(temp_path),
                    language=forced_language,

                    # More accurate than beam_size=1.
                    beam_size=5,

                    vad_filter=True,

                    # Helps prevent previous segments
                    # from contaminating recognition.
                    condition_on_previous_text=False,
                )
            )

            parts = []

            for segment in segments:

                segment_text = (
                    segment.text.strip()
                )

                if segment_text:
                    parts.append(
                        segment_text
                    )

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

        detected_language = (
            info.language
            or language
            or "unknown"
        )

        normalized_transcript = (
            normalize_voice_transcript(
                raw_transcript,
                language=detected_language,
            )
        )

        return VoiceTranscriptionResponse(
            text=normalized_transcript,
            raw_text=raw_transcript,
            language=detected_language,
            language_probability=(
                info.language_probability
            ),
            model=MODEL_NAME,
            normalized=(
                normalized_transcript
                != raw_transcript
            ),
        )

    except HTTPException:
        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {exc}",
        ) from exc
