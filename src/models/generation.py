from dataclasses import dataclass


@dataclass
class GenerationRequest:
    text: str
    gender: str
    filename: str


@dataclass
class GenerationResult:
    success: bool
    output_path: str | None = None
    error_message: str | None = None
    error_kind: str | None = None
