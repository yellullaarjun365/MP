from pathlib import Path
import os
import shutil
import subprocess
import tempfile
from threading import Lock

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from faster_whisper import WhisperModel

from app.schemas.voice import VoiceTranscriptionResponse
from app.services.voice_normalization import normalize_voice_transcript


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


# ------------------------------------------------
# Whisper configuration
# ------------------------------------------------

MODEL_NAME = "base"

_whisper_model = None
_whisper_lock = Lock()


def get_whisper_model() -> WhisperModel:
    global _whisper_model

    if _whisper_model is None:
        with _whisper_lock:
            if _whisper_model is None:
                print(f"Loading Whisper {MODEL_NAME} model...")

                _whisper_model = WhisperModel(
                    MODEL_NAME,
                    device="cpu",
                    compute_type="int8",
                )

                print(f"Whisper {MODEL_NAME} model loaded.")

    return _whisper_model


# ------------------------------------------------
# Supported audio formats
# ------------------------------------------------

ALLOWED_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".webm",
    ".ogg",
    ".flac",
}


MIME_SUFFIX_MAP = {
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".m4a",
    "audio/x-m4a": ".m4a",
    "audio/flac": ".flac",
}


LANGUAGE_MAP = {
    "auto": None,
    "en": "en",
    "te": "te",
}


# ------------------------------------------------
# FFmpeg resolver
# ------------------------------------------------

def resolve_ffmpeg() -> str:
    configured = os.getenv("FFMPEG_BIN")

    if configured:
        configured_path = Path(configured)

        if configured_path.is_file():
            return str(configured_path)

    discovered = shutil.which("ffmpeg")

    if discovered:
        return discovered

    local_appdata = os.getenv("LOCALAPPDATA")

    if local_appdata:
        winget_root = (
            Path(local_appdata)
            / "Microsoft"
            / "WinGet"
            / "Packages"
        )

        if winget_root.exists():
            candidates = sorted(
                winget_root.glob(
                    "Gyan.FFmpeg_*/ffmpeg-*/bin/ffmpeg.exe"
                )
            )

            if candidates:
                return str(candidates[-1])

    raise RuntimeError(
        "FFmpeg executable could not be found. "
        "Set FFMPEG_BIN to the full path of ffmpeg.exe."
    )


# ------------------------------------------------
# Audio conversion
# ------------------------------------------------

def convert_audio_to_wav(source_path: Path, wav_path: Path) -> None:
    ffmpeg = resolve_ffmpeg()

    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(source_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(wav_path),
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        timeout=45,
    )

    if completed.returncode != 0:
        stderr = (
            completed.stderr
            or "unknown FFmpeg error"
        ).strip()

        raise RuntimeError(
            "FFmpeg audio conversion failed: "
            + stderr[-2000:]
        )

    if not wav_path.exists():
        raise RuntimeError(
            "FFmpeg reported success, but WAV output was not created."
        )

    if wav_path.stat().st_size < 100:
        raise RuntimeError(
            "FFmpeg created an unexpectedly small WAV file."
        )


# ------------------------------------------------
# Transcription endpoint
# ------------------------------------------------

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
            detail="Unsupported language. Use auto, en, or te.",
        )

    audio_bytes = await file.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Empty audio file.",
        )

    if len(audio_bytes) > 15 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="Audio file is too large. Maximum size is 15 MB.",
        )

    filename_suffix = Path(file.filename or "").suffix.lower()

    mime_type = (
        file.content_type
        or ""
    ).lower().split(";")[0].strip()

    suffix = filename_suffix

    if suffix not in ALLOWED_EXTENSIONS:
        suffix = MIME_SUFFIX_MAP.get(
            mime_type,
            ".webm",
        )

    source_path = None
    wav_path = None

    try:
        # Save browser audio
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False,
        ) as temp_file:
            temp_file.write(audio_bytes)
            source_path = Path(temp_file.name)

        # Temporary normalized WAV
        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as wav_file:
            wav_path = Path(wav_file.name)

        print("Voice upload:", file.filename)
        print("Content-Type:", file.content_type)
        print("Audio bytes:", len(audio_bytes))
        print("Source:", source_path)

        # Normalize all browser audio
        convert_audio_to_wav(
            source_path,
            wav_path,
        )

        print("Normalized WAV:", wav_path)
        print("WAV size:", wav_path.stat().st_size)

        # Whisper
        forced_language = LANGUAGE_MAP[language]

        model = get_whisper_model()

        segments, info = model.transcribe(
            str(wav_path),
            language=forced_language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
        )

        parts = []

        for segment in segments:
            segment_text = segment.text.strip()

            if segment_text:
                parts.append(segment_text)

        raw_transcript = " ".join(parts).strip()

        print("Raw transcript:", raw_transcript)

        if not raw_transcript:
            raise HTTPException(
                status_code=422,
                detail="Could not detect speech in the audio.",
            )

        detected_language = (
            info.language
            or language
            or "unknown"
        )

        normalized_transcript = normalize_voice_transcript(
            raw_transcript,
            language=detected_language,
        )

        return VoiceTranscriptionResponse(
            text=normalized_transcript,
            raw_text=raw_transcript,
            language=detected_language,
            language_probability=info.language_probability,
            model=MODEL_NAME,
            normalized=(normalized_transcript != raw_transcript),
        )

    except HTTPException:
        raise

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=500,
            detail="Audio conversion timed out while processing the recording.",
        )

    except Exception as exc:
        print("VOICE TRANSCRIPTION ERROR:", repr(exc))

        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {exc}",
        ) from exc

    finally:
        if source_path is not None:
            try:
                source_path.unlink(missing_ok=True)
            except Exception:
                pass

        if wav_path is not None:
            try:
                wav_path.unlink(missing_ok=True)
            except Exception:
                pass
