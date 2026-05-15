import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class HealingRecord:
    """Audit record for one healed locator."""

    element_name: str
    failed_strategy: str
    failed_value: str
    healed_strategy: str
    healed_value: str
    confidence: float
    reason: str
    created_at: str


class HealingStore:
    """Persists healing decisions as JSON Lines for auditability and reporting."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(
        self,
        *,
        element_name: str,
        failed_strategy: str,
        failed_value: str,
        healed_strategy: str,
        healed_value: str,
        confidence: float,
        reason: str,
    ) -> HealingRecord:
        """Write a healing event and return the record."""

        record = HealingRecord(
            element_name=element_name,
            failed_strategy=failed_strategy,
            failed_value=failed_value,
            healed_strategy=healed_strategy,
            healed_value=healed_value,
            confidence=confidence,
            reason=reason,
            created_at=datetime.now(UTC).isoformat(),
        )
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(asdict(record)) + "\n")
        return record

    def read_all(self) -> list[HealingRecord]:
        """Read all recorded healing events."""

        if not self.path.exists():
            return []
        records = []
        with self.path.open(encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    records.append(HealingRecord(**json.loads(line)))
        return records
