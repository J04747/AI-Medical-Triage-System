from __future__ import annotations
from dataclasses import dataclass
from presidio_analyzer import Pattern, PatternRecognizer

class SingaporeICRecognizer(PatternRecognizer):
    """Recognizer for Singapore NRIC/FIN numbers."""
    
    PATTERNS = [
        Pattern("singapore_ic", r"[STFG]\d{7}[A-Z]", 0.8),
    ]
    CONTEXT = ["ic", "nric", "fin", "identification", "singapore", "nric:"]

    def __init__(self, **kwargs) -> None:
        super().__init__(
            supported_entity="PERSON",
            patterns=self.PATTERNS,
            context=self.CONTEXT,
            supported_language="en",
            **kwargs,
        )

@dataclass
class SingaporeICPlugin:
    name: str = "singapore-ic"
    version: str = "0.1.0"

    def get_recognizers(self) -> list[PatternRecognizer]:
        return [SingaporeICRecognizer()]

plugin = SingaporeICPlugin()
