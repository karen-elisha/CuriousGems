"""
Event Engine for the VeriGem Financial Digital Twin.

Provides a full event-sourcing backbone:

    - **Immutable events**  — frozen dataclasses that can never be mutated
      once recorded.
    - **Event history**     — append-only, ordered log of every state change
      with efficient lookup by entity, type, and time range.
    - **Event replay**      — deterministic re-application of events against
      a snapshot to reconstruct any point-in-time state.
    - **Timeline generation** — chronological event sequences for any entity
      with optional filtering and windowing.
    - **Snapshot creation**  — full and incremental snapshots of cumulative
      event state for fast replay starting points.

Design principles
-----------------
* Events are the *single source of truth* for all mutations.
* The engine is deliberately **in-memory only**, consistent with the rest of
  the VeriGem core (no database, no persistence layer).
* All public state is exposed via typed dataclasses — no raw dicts.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum, unique
from typing import Any, Callable, Optional, Sequence

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Event categories
# ---------------------------------------------------------------------------

@unique
class EventCategory(Enum):
    """High-level classification of events."""

    # Entity lifecycle
    ENTITY_CREATED = "ENTITY_CREATED"
    ENTITY_UPDATED = "ENTITY_UPDATED"
    ENTITY_DELETED = "ENTITY_DELETED"

    # Financial operations
    PO_RAISED = "PO_RAISED"
    PO_APPROVED = "PO_APPROVED"
    PO_CANCELLED = "PO_CANCELLED"
    INVOICE_SUBMITTED = "INVOICE_SUBMITTED"
    INVOICE_VERIFIED = "INVOICE_VERIFIED"
    INVOICE_DISPUTED = "INVOICE_DISPUTED"
    PAYMENT_INITIATED = "PAYMENT_INITIATED"
    PAYMENT_COMPLETED = "PAYMENT_COMPLETED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    PAYMENT_REVERSED = "PAYMENT_REVERSED"

    # Compliance & audit
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    AUDIT_ACTION = "AUDIT_ACTION"
    VENDOR_STATUS_CHANGED = "VENDOR_STATUS_CHANGED"
    EMPLOYEE_STATUS_CHANGED = "EMPLOYEE_STATUS_CHANGED"

    # System / meta
    SNAPSHOT_CREATED = "SNAPSHOT_CREATED"
    REPLAY_STARTED = "REPLAY_STARTED"
    REPLAY_COMPLETED = "REPLAY_COMPLETED"


# ---------------------------------------------------------------------------
# Immutable Event
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Event:
    """
    An immutable, self-describing event in the financial ecosystem.

    Once created, no field can be modified.  The ``event_hash`` is a
    content-addressable fingerprint computed at creation time to guarantee
    integrity across replays.

    Attributes
    ----------
    event_id : str
        Globally unique identifier (UUID-4).
    timestamp : datetime
        Exact time the event was recorded.
    category : EventCategory
        High-level event classification.
    entity_type : str
        The domain entity type affected (e.g. ``"vendor"``, ``"transaction"``).
    entity_id : str
        ID of the affected entity.
    actor_id : str
        ID of the user / system component that triggered the event.
    payload : dict
        Arbitrary key-value data describing the change.  For updates this
        typically contains ``before`` and ``after`` sub-dicts.
    metadata : dict
        Optional context (IP address, device, source module, …).
    parent_event_id : str | None
        If this event is a consequence of another, the parent's ID.
    event_hash : str
        SHA-256 of the canonical content, computed at construction time.
    sequence_number : int
        Monotonically increasing position within the global event log.
    """

    event_id: str
    timestamp: datetime
    category: EventCategory
    entity_type: str
    entity_id: str
    actor_id: str
    payload: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)
    parent_event_id: Optional[str] = None
    event_hash: str = ""
    sequence_number: int = 0


def _compute_event_hash(event: Event) -> str:
    """
    Compute a deterministic SHA-256 hash over the semantic content of
    *event* (excludes the hash and sequence number themselves).
    """
    canonical = json.dumps(
        {
            "event_id": event.event_id,
            "timestamp": event.timestamp.isoformat(),
            "category": event.category.value,
            "entity_type": event.entity_type,
            "entity_id": event.entity_id,
            "actor_id": event.actor_id,
            "payload": event.payload,
            "metadata": event.metadata,
            "parent_event_id": event.parent_event_id,
        },
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Snapshot
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Snapshot:
    """
    A frozen point-in-time capture of the cumulative event state.

    Snapshots are used as efficient starting points for replay — instead
    of replaying from event #0, the engine can resume from the nearest
    snapshot and replay only the delta.

    Attributes
    ----------
    snapshot_id : str
        Unique identifier for this snapshot.
    created_at : datetime
        When the snapshot was taken.
    last_sequence_number : int
        The sequence number of the most recent event included.
    last_event_id : str
        The event ID of the most recent event included.
    entity_states : dict[str, dict[str, dict]]
        Nested mapping ``{entity_type: {entity_id: state_dict}}``.
    event_count : int
        Total number of events that contributed to this snapshot.
    snapshot_hash : str
        SHA-256 over the canonical snapshot content.
    label : str
        Human-readable label (e.g. ``"full-20260718T1030"``).
    """

    snapshot_id: str
    created_at: datetime
    last_sequence_number: int
    last_event_id: str
    entity_states: dict = field(default_factory=dict)
    event_count: int = 0
    snapshot_hash: str = ""
    label: str = ""


# ---------------------------------------------------------------------------
# Timeline Entry
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TimelineEntry:
    """
    A lightweight, presentation-ready record within a generated timeline.
    """

    event_id: str
    timestamp: datetime
    category: str
    entity_type: str
    entity_id: str
    actor_id: str
    summary: str
    sequence_number: int


# ---------------------------------------------------------------------------
# Event Engine
# ---------------------------------------------------------------------------

class EventEngine:
    """
    Core event-sourcing engine for the VeriGem Financial Digital Twin.

    Lifecycle::

        engine = EventEngine()

        # Record events
        evt = engine.record(
            category=EventCategory.PO_RAISED,
            entity_type="purchase_order",
            entity_id="PO-50001",
            actor_id="EMP-20001",
            payload={"amount_inr": "250000.00", "vendor_id": "VEN-100234"},
        )

        # Query history
        po_events = engine.get_entity_history("PO-50001")

        # Generate a timeline
        timeline = engine.generate_timeline(entity_id="VEN-100234")

        # Take a snapshot
        snap = engine.create_snapshot(label="before-fy-close")

        # Replay from snapshot
        state = engine.replay(from_snapshot=snap, up_to_sequence=150)
    """

    def __init__(self) -> None:
        # Append-only ordered event log
        self._events: list[Event] = []

        # Fast-lookup indices
        self._by_entity: dict[str, list[int]] = defaultdict(list)
        self._by_category: dict[EventCategory, list[int]] = defaultdict(list)
        self._by_actor: dict[str, list[int]] = defaultdict(list)
        self._by_id: dict[str, int] = {}

        # Snapshot store
        self._snapshots: list[Snapshot] = []

        # Monotonic counter
        self._sequence_counter: int = 0

        # Event handlers (subscribers)
        self._handlers: dict[EventCategory, list[Callable[[Event], None]]] = defaultdict(list)

        # Cumulative entity state (built from events)
        self._entity_states: dict[str, dict[str, dict]] = defaultdict(dict)

        logger.info("EventEngine initialised.")

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def event_count(self) -> int:
        """Total number of recorded events."""
        return len(self._events)

    @property
    def snapshot_count(self) -> int:
        """Total number of stored snapshots."""
        return len(self._snapshots)

    @property
    def current_sequence(self) -> int:
        """Current sequence counter value."""
        return self._sequence_counter

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record(
        self,
        *,
        category: EventCategory,
        entity_type: str,
        entity_id: str,
        actor_id: str,
        payload: Optional[dict] = None,
        metadata: Optional[dict] = None,
        parent_event_id: Optional[str] = None,
    ) -> Event:
        """
        Create and append an immutable event to the log.

        Returns the fully populated ``Event`` with its computed hash and
        sequence number.
        """
        self._sequence_counter += 1

        event = Event(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            category=category,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            payload=payload or {},
            metadata=metadata or {},
            parent_event_id=parent_event_id,
            sequence_number=self._sequence_counter,
        )

        # Compute content-addressable hash (requires object.__setattr__
        # because the dataclass is frozen).
        object.__setattr__(event, "event_hash", _compute_event_hash(event))

        # Append to the log
        idx = len(self._events)
        self._events.append(event)

        # Update indices
        self._by_entity[entity_id].append(idx)
        self._by_category[category].append(idx)
        self._by_actor[actor_id].append(idx)
        self._by_id[event.event_id] = idx

        # Update cumulative entity state
        self._apply_event_to_state(event)

        # Notify subscribers
        for handler in self._handlers.get(category, []):
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "Handler %s failed for event %s",
                    handler.__name__,
                    event.event_id,
                )

        logger.debug(
            "Recorded event #%d  %s  %s/%s",
            event.sequence_number,
            event.category.value,
            event.entity_type,
            event.entity_id,
        )
        return event

    # ------------------------------------------------------------------
    # Event subscriptions
    # ------------------------------------------------------------------

    def subscribe(
        self,
        category: EventCategory,
        handler: Callable[[Event], None],
    ) -> None:
        """
        Register a handler to be called whenever an event of *category*
        is recorded.
        """
        self._handlers[category].append(handler)
        logger.debug(
            "Subscribed %s to %s", handler.__name__, category.value
        )

    def unsubscribe(
        self,
        category: EventCategory,
        handler: Callable[[Event], None],
    ) -> None:
        """Remove a previously registered handler."""
        handlers = self._handlers.get(category, [])
        if handler in handlers:
            handlers.remove(handler)

    # ------------------------------------------------------------------
    # Event history (querying)
    # ------------------------------------------------------------------

    def get_event(self, event_id: str) -> Event:
        """Retrieve a single event by ID."""
        idx = self._by_id.get(event_id)
        if idx is None:
            raise KeyError(f"Event '{event_id}' not found.")
        return self._events[idx]

    def get_entity_history(
        self,
        entity_id: str,
        *,
        category: Optional[EventCategory] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[Event]:
        """
        Return chronologically ordered events for *entity_id*.

        Supports optional filtering by category and time window.
        """
        indices = self._by_entity.get(entity_id, [])
        events = [self._events[i] for i in indices]

        if category is not None:
            events = [e for e in events if e.category == category]
        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if until is not None:
            events = [e for e in events if e.timestamp <= until]

        events.sort(key=lambda e: e.sequence_number)

        if limit is not None:
            events = events[:limit]

        return events

    def get_events_by_category(
        self,
        category: EventCategory,
        *,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[Event]:
        """Return all events of a given category, optionally windowed."""
        indices = self._by_category.get(category, [])
        events = [self._events[i] for i in indices]

        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if until is not None:
            events = [e for e in events if e.timestamp <= until]

        events.sort(key=lambda e: e.sequence_number)

        if limit is not None:
            events = events[:limit]

        return events

    def get_events_by_actor(
        self,
        actor_id: str,
        *,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> list[Event]:
        """Return all events triggered by *actor_id*."""
        indices = self._by_actor.get(actor_id, [])
        events = [self._events[i] for i in indices]

        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if until is not None:
            events = [e for e in events if e.timestamp <= until]

        events.sort(key=lambda e: e.sequence_number)
        return events

    def get_all_events(
        self,
        *,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> list[Event]:
        """Return the full event log, optionally time-windowed."""
        events = list(self._events)

        if since is not None:
            events = [e for e in events if e.timestamp >= since]
        if until is not None:
            events = [e for e in events if e.timestamp <= until]

        return events

    # ------------------------------------------------------------------
    # Timeline generation
    # ------------------------------------------------------------------

    def generate_timeline(
        self,
        *,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        actor_id: Optional[str] = None,
        categories: Optional[Sequence[EventCategory]] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: Optional[int] = None,
    ) -> list[TimelineEntry]:
        """
        Generate a presentation-ready timeline of events.

        Supports filtering by entity, entity type, actor, categories, and
        time window.  Results are always sorted chronologically.

        Returns a list of lightweight ``TimelineEntry`` objects suitable
        for display or serialisation.
        """
        # Start from the broadest applicable index
        if entity_id is not None:
            indices = self._by_entity.get(entity_id, [])
            candidates = [self._events[i] for i in indices]
        elif actor_id is not None:
            indices = self._by_actor.get(actor_id, [])
            candidates = [self._events[i] for i in indices]
        else:
            candidates = list(self._events)

        # Apply filters
        if entity_type is not None:
            candidates = [e for e in candidates if e.entity_type == entity_type]
        if categories is not None:
            cat_set = set(categories)
            candidates = [e for e in candidates if e.category in cat_set]
        if since is not None:
            candidates = [e for e in candidates if e.timestamp >= since]
        if until is not None:
            candidates = [e for e in candidates if e.timestamp <= until]

        # Sort chronologically
        candidates.sort(key=lambda e: e.sequence_number)

        if limit is not None:
            candidates = candidates[:limit]

        # Convert to TimelineEntry
        timeline: list[TimelineEntry] = []
        for evt in candidates:
            summary = self._summarise_event(evt)
            timeline.append(
                TimelineEntry(
                    event_id=evt.event_id,
                    timestamp=evt.timestamp,
                    category=evt.category.value,
                    entity_type=evt.entity_type,
                    entity_id=evt.entity_id,
                    actor_id=evt.actor_id,
                    summary=summary,
                    sequence_number=evt.sequence_number,
                )
            )

        return timeline

    # ------------------------------------------------------------------
    # Snapshot creation
    # ------------------------------------------------------------------

    def create_snapshot(
        self,
        *,
        label: Optional[str] = None,
    ) -> Snapshot:
        """
        Capture the current cumulative entity state as an immutable snapshot.

        The snapshot includes:
        * A deep copy of every entity state built from event application.
        * The sequence number of the last event included.
        * A SHA-256 integrity hash over the snapshot content.
        """
        if not self._events:
            raise ValueError("Cannot create a snapshot — no events recorded.")

        last_event = self._events[-1]
        now = datetime.now()
        auto_label = label or f"snapshot-{now.strftime('%Y%m%dT%H%M%S')}"

        # Deep-copy state to guarantee immutability
        frozen_state = copy.deepcopy(dict(self._entity_states))

        # Compute snapshot hash
        canonical = json.dumps(
            {
                "last_sequence": last_event.sequence_number,
                "last_event_id": last_event.event_id,
                "entity_states": frozen_state,
            },
            sort_keys=True,
            default=str,
        )
        snap_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

        snapshot = Snapshot(
            snapshot_id=str(uuid.uuid4()),
            created_at=now,
            last_sequence_number=last_event.sequence_number,
            last_event_id=last_event.event_id,
            entity_states=frozen_state,
            event_count=len(self._events),
            snapshot_hash=snap_hash,
            label=auto_label,
        )

        self._snapshots.append(snapshot)

        # Record a meta-event for the snapshot
        self.record(
            category=EventCategory.SNAPSHOT_CREATED,
            entity_type="snapshot",
            entity_id=snapshot.snapshot_id,
            actor_id="SYSTEM",
            payload={
                "label": snapshot.label,
                "last_sequence_number": snapshot.last_sequence_number,
                "event_count": snapshot.event_count,
                "snapshot_hash": snapshot.snapshot_hash,
            },
        )

        logger.info(
            "Snapshot '%s' created at sequence #%d  (%d events, hash=%s…)",
            snapshot.label,
            snapshot.last_sequence_number,
            snapshot.event_count,
            snapshot.snapshot_hash[:12],
        )
        return snapshot

    def get_snapshot(self, snapshot_id: str) -> Snapshot:
        """Retrieve a snapshot by ID."""
        for snap in self._snapshots:
            if snap.snapshot_id == snapshot_id:
                return snap
        raise KeyError(f"Snapshot '{snapshot_id}' not found.")

    def get_latest_snapshot(self) -> Optional[Snapshot]:
        """Return the most recently created snapshot, or None."""
        return self._snapshots[-1] if self._snapshots else None

    def list_snapshots(self) -> list[Snapshot]:
        """Return all snapshots in creation order."""
        return list(self._snapshots)

    # ------------------------------------------------------------------
    # Event replay
    # ------------------------------------------------------------------

    def replay(
        self,
        *,
        from_snapshot: Optional[Snapshot] = None,
        up_to_sequence: Optional[int] = None,
        up_to_timestamp: Optional[datetime] = None,
        entity_id: Optional[str] = None,
    ) -> dict[str, dict[str, dict]]:
        """
        Replay events to reconstruct entity state at a point in time.

        Parameters
        ----------
        from_snapshot : Snapshot, optional
            Start from this snapshot's state rather than from scratch.
        up_to_sequence : int, optional
            Stop replaying after this sequence number (inclusive).
        up_to_timestamp : datetime, optional
            Stop replaying after this timestamp (inclusive).
        entity_id : str, optional
            Replay only events for a single entity.

        Returns
        -------
        dict[str, dict[str, dict]]
            Reconstructed entity state:
            ``{entity_type: {entity_id: state_dict}}``.
        """
        # Initialise state from snapshot or empty
        if from_snapshot is not None:
            state: dict[str, dict[str, dict]] = copy.deepcopy(
                from_snapshot.entity_states
            )
            start_after = from_snapshot.last_sequence_number
        else:
            state = defaultdict(dict)
            start_after = 0

        # Determine which events to replay
        if entity_id is not None:
            indices = self._by_entity.get(entity_id, [])
            events_to_replay = [self._events[i] for i in indices]
        else:
            events_to_replay = list(self._events)

        # Filter to the replay window
        events_to_replay = [
            e for e in events_to_replay
            if e.sequence_number > start_after
        ]

        if up_to_sequence is not None:
            events_to_replay = [
                e for e in events_to_replay
                if e.sequence_number <= up_to_sequence
            ]

        if up_to_timestamp is not None:
            events_to_replay = [
                e for e in events_to_replay
                if e.timestamp <= up_to_timestamp
            ]

        # Sort by sequence number for deterministic replay
        events_to_replay.sort(key=lambda e: e.sequence_number)

        # Record a meta-event for replay start
        replay_event = self.record(
            category=EventCategory.REPLAY_STARTED,
            entity_type="replay",
            entity_id=entity_id or "ALL",
            actor_id="SYSTEM",
            payload={
                "from_snapshot": (
                    from_snapshot.snapshot_id if from_snapshot else None
                ),
                "start_after_sequence": start_after,
                "up_to_sequence": up_to_sequence,
                "up_to_timestamp": (
                    up_to_timestamp.isoformat() if up_to_timestamp else None
                ),
                "events_to_replay_count": len(events_to_replay),
            },
        )

        # Apply events
        replayed_count = 0
        for event in events_to_replay:
            self._apply_event_to_state_dict(event, state)
            replayed_count += 1

        # Record replay completion
        self.record(
            category=EventCategory.REPLAY_COMPLETED,
            entity_type="replay",
            entity_id=entity_id or "ALL",
            actor_id="SYSTEM",
            payload={
                "replayed_event_count": replayed_count,
                "resulting_entity_types": list(state.keys()),
                "resulting_entity_count": sum(
                    len(v) for v in state.values()
                ),
            },
            parent_event_id=replay_event.event_id,
        )

        logger.info(
            "Replay complete — %d events applied, %d entity types, %d entities.",
            replayed_count,
            len(state),
            sum(len(v) for v in state.values()),
        )

        return dict(state)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _apply_event_to_state(self, event: Event) -> None:
        """Apply an event to the engine's cumulative entity state."""
        self._apply_event_to_state_dict(event, self._entity_states)

    @staticmethod
    def _apply_event_to_state_dict(
        event: Event,
        state: dict[str, dict[str, dict]],
    ) -> None:
        """
        Apply a single event to an arbitrary state dictionary.

        Used by both live recording and replay.
        """
        et = event.entity_type
        eid = event.entity_id

        if et not in state:
            state[et] = {}

        if event.category == EventCategory.ENTITY_DELETED:
            state[et].pop(eid, None)
            return

        # Initialise if new
        if eid not in state[et]:
            state[et][eid] = {}

        current = state[et][eid]

        # Merge payload (shallow) — "after" sub-dict takes priority if present
        if "after" in event.payload:
            current.update(event.payload["after"])
        else:
            current.update(event.payload)

        # Always stamp latest event metadata
        current["_last_event_id"] = event.event_id
        current["_last_event_seq"] = event.sequence_number
        current["_last_event_ts"] = event.timestamp.isoformat()

    @staticmethod
    def _summarise_event(event: Event) -> str:
        """
        Build a concise human-readable summary string for a timeline entry.
        """
        parts = [event.category.value.replace("_", " ").title()]

        # Add entity reference
        parts.append(f"on {event.entity_type}/{event.entity_id}")

        # Add actor
        if event.actor_id != "SYSTEM":
            parts.append(f"by {event.actor_id}")

        # Add key payload details (up to 3)
        highlight_keys = [
            k for k in event.payload
            if k not in ("before", "after") and not k.startswith("_")
        ]
        for key in highlight_keys[:3]:
            val = event.payload[key]
            parts.append(f"{key}={val}")

        return "  —  ".join(parts)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Return diagnostic information about the event engine."""
        return {
            "total_events": len(self._events),
            "current_sequence": self._sequence_counter,
            "unique_entities_tracked": sum(
                len(v) for v in self._entity_states.values()
            ),
            "entity_types_tracked": list(self._entity_states.keys()),
            "snapshot_count": len(self._snapshots),
            "categories_seen": sorted(
                cat.value for cat in self._by_category.keys()
            ),
            "subscriber_count": sum(
                len(h) for h in self._handlers.values()
            ),
        }

    def verify_integrity(self) -> list[dict[str, Any]]:
        """
        Verify the integrity of the entire event log.

        Returns a list of integrity errors (empty = healthy).
        """
        errors: list[dict[str, Any]] = []

        prev_seq = 0
        for idx, event in enumerate(self._events):
            # Sequence monotonicity
            if event.sequence_number <= prev_seq:
                errors.append({
                    "type": "SEQUENCE_ORDER",
                    "index": idx,
                    "event_id": event.event_id,
                    "detail": (
                        f"Sequence {event.sequence_number} is not greater "
                        f"than previous {prev_seq}"
                    ),
                })
            prev_seq = event.sequence_number

            # Hash verification
            expected_hash = _compute_event_hash(event)
            if event.event_hash != expected_hash:
                errors.append({
                    "type": "HASH_MISMATCH",
                    "index": idx,
                    "event_id": event.event_id,
                    "detail": (
                        f"Expected hash {expected_hash[:16]}…, "
                        f"got {event.event_hash[:16]}…"
                    ),
                })

            # Parent reference validity
            if event.parent_event_id and event.parent_event_id not in self._by_id:
                errors.append({
                    "type": "ORPHAN_PARENT",
                    "index": idx,
                    "event_id": event.event_id,
                    "detail": (
                        f"Parent event {event.parent_event_id} not found in log"
                    ),
                })

        if errors:
            logger.warning(
                "Integrity check found %d error(s).", len(errors)
            )
        else:
            logger.info("Integrity check passed — %d events verified.", len(self._events))

        return errors
