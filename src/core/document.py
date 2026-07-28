from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.content)

    def __repr__(self) -> str:
        preview = self.content[:80].replace("\n", " ")
        return f"Document(content='{preview}...', metadata={self.metadata})"