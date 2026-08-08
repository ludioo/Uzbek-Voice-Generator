from src.models.generation import GenerationResult

ERROR_MESSAGES = {
    "empty_text": "Text must not be empty.",
    "invalid_filename": (
        "Filename is invalid. Use a simple name like hello.mp3 (no folders)."
    ),
    "voice_not_found": "Selected voice is not available in config.",
    "config_error": "Voice configuration could not be loaded.",
    "save_permission": "Unable to save the audio file. Check folder permissions.",
    "network_unavailable": (
        "Network unavailable. Check your connection and try again."
    ),
    "tts_failure": (
        "Speech generation failed. Check your network connection and try again."
    ),
}


def message_for(result: GenerationResult) -> str:
    if result.error_kind and result.error_kind in ERROR_MESSAGES:
        return ERROR_MESSAGES[result.error_kind]
    if result.error_message:
        return result.error_message
    return "Generation failed."
