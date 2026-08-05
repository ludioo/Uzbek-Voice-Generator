from dataclasses import dataclass


@dataclass
class Voice:
    id: str
    name: str
    gender: str
    language: str
