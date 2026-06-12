from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressState:
    """Small, UI-independent description of a running operation."""

    title: str = 'Загрузка'
    message: Optional[str] = None
    detail: Optional[str] = None
    current: Optional[int] = None
    total: Optional[int] = None
    blocking: bool = False

    @property
    def is_determinate(self):
        return self.current is not None and self.total is not None

    @property
    def remaining(self):
        if not self.is_determinate:
            return None
        return max(self.total - self.current, 0)

    @property
    def percent(self):
        if not self.is_determinate:
            return None
        if self.total <= 0:
            return 100 if self.current >= self.total else 0
        return max(0, min(100, int(self.current * 100 / self.total)))
