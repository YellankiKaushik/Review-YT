import hashlib
import json
from dataclasses import asdict, dataclass, field


class Failure(Exception):
    def __init__(self, code, message, status=502):
        self.code, self.message, self.status = code, message, status
        super().__init__(message)


@dataclass(frozen=True)
class Evidence:
    video: dict
    comments: list[str]
    captions: str | None = None
    notices: list[str] = field(default_factory=list)

    def dump(self):
        return asdict(self)

    def signature(self):
        return hashlib.sha256(
            json.dumps(self.dump(), sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest()
