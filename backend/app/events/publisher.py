import json
import logging
import os
from datetime import datetime, timezone

from google.cloud import pubsub_v1

from app.config import settings

logger = logging.getLogger(__name__)

# WHY MODULE-LEVEL CLIENT NOT PER-REQUEST CLIENT:
# Creating a PublisherClient opens a gRPC connection. Creating one per request
# would open and close hundreds of connections per second — expensive and slow.
# A single module-level client reuses one connection pool for the lifetime of
# the process. This is the standard pattern for GCP clients in web servers.
_publisher: pubsub_v1.PublisherClient | None = None


def get_publisher() -> pubsub_v1.PublisherClient:
    global _publisher
    if _publisher is None:
        _publisher = pubsub_v1.PublisherClient()
        # When PUBSUB_EMULATOR_HOST env var is set, the SDK automatically
        # points to the local emulator. No code change needed for GCP vs local.
    return _publisher


def _topic_path() -> str:
    return get_publisher().topic_path(settings.pubsub_project_id, settings.pubsub_topic)


async def publish_event(
    event_type: str,
    payload: dict,
    user_id: str | None = None,
) -> None:
    """
    Publishes a single event to Pub/Sub.

    WHY FIRE-AND-FORGET (no await on the future):
    Publishing to Pub/Sub is fast (~5ms). Waiting for the ack on every
    request adds latency for the user. We log failures but don't block.
    For financial events (payments), use the outbox pattern instead of
    this function — those must never be lost.

    FUTURE: replace with outbox pattern for critical events.
    The outbox pattern writes events to the DB in the same transaction as
    the business data, then a worker publishes them. Guarantees no event
    is lost even if Pub/Sub is temporarily unavailable.
    """
    event = {
        "event_type": event_type,
        "user_id": user_id,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        future = get_publisher().publish(
            _topic_path(),
            data=json.dumps(event).encode("utf-8"),
            event_type=event_type,
            # Attributes (key-value strings) allow Pub/Sub subscriptions to
            # filter messages without decoding the payload. A subscription
            # can say "only deliver messages where event_type=match_created".
        )
        future.add_done_callback(lambda f: _handle_publish_result(f, event_type))
    except Exception:
        logger.exception("Failed to publish event %s", event_type)


def _handle_publish_result(future, event_type: str) -> None:
    try:
        message_id = future.result()
        logger.debug("Published %s as message %s", event_type, message_id)
    except Exception:
        logger.exception("Pub/Sub delivery failed for event %s", event_type)
