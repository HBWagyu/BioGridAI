"""Simple hash-chained event log. Farmer-owned audit trail."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from backend.app.models.domain import EventRecord


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class HashChain:
    def __init__(self) -> None:
        self.events: list[EventRecord] = []

    def append(self, actor: str, event_type: str, details: str) -> EventRecord:
        prev = self.events[-1].hash if self.events else "GENESIS"
        payload = json.dumps(
            {"actor": actor, "event_type": event_type, "details": details},
            sort_keys=True,
        )
        payload_sha = _sha(payload)
        ts = datetime.now(timezone.utc)
        digest = _sha(f"{prev}|{ts.isoformat()}|{payload_sha}")
        rec = EventRecord(
            seq=len(self.events) + 1,
            timestamp=ts,
            actor=actor,
            event_type=event_type,
            details=details,
            prev_hash=prev,
            payload_sha256=payload_sha,
            hash=digest,
        )
        self.events.append(rec)
        return rec

    def verify(self) -> tuple[bool, str]:
        prev = "GENESIS"
        for ev in self.events:
            if ev.prev_hash != prev:
                return False, f"Break at seq {ev.seq}: prev_hash mismatch"
            payload = json.dumps(
                {"actor": ev.actor, "event_type": ev.event_type, "details": ev.details},
                sort_keys=True,
            )
            if _sha(payload) != ev.payload_sha256:
                return False, f"Break at seq {ev.seq}: payload hash mismatch"
            expect = _sha(f"{ev.prev_hash}|{ev.timestamp.isoformat()}|{ev.payload_sha256}")
            if expect != ev.hash:
                return False, f"Break at seq {ev.seq}: block hash mismatch"
            prev = ev.hash
        return True, f"OK — {len(self.events)} events"
