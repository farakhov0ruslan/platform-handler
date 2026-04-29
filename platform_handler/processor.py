import asyncio
import threading
from uuid import UUID

import dishka
from notification_registry import NotificationChannel
from notification_registry import NotificationType
from notification_registry import PlatformChannelProcessor
from notification_registry import deserialize_message
from utils_library.Logging.log import get_logger

from platform_handler.infrastructure.enums import NotificationStatus
from platform_handler.infrastructure.models import NotificationTable
from platform_handler.ioc import IOC_CONTAINER
from platform_handler.ioc import NotificationRepository

LOGGER = get_logger(__name__)

# Single persistent event loop shared across all RabbitMQ consumer callbacks.
# asyncpg connection pools are bound to the loop they were created on — reusing
# one loop avoids "Future attached to a different loop" errors.
_loop = asyncio.new_event_loop()
_loop_thread = threading.Thread(target=_loop.run_forever, daemon=True, name="platform-async")
_loop_thread.start()


def _run(coro):
    return asyncio.run_coroutine_threadsafe(coro, _loop).result()


def process_platform_message(body: bytes) -> None:
    message = deserialize_message(body)
    LOGGER.info(
        f"Processing platform notification: type={message.metadata.notification_type}, "
        f"id={message.metadata.notification_id}"
    )

    processed = PlatformChannelProcessor.process(message)
    if processed is None:
        LOGGER.warning(
            f"No platform processor for type={message.metadata.notification_type}, skipping"
        )
        return

    if message.metadata.notification_type == NotificationType.DELIVERY_FAILED:
        _run(_insert(message, processed))
    else:
        _run(_update(message, processed))

    LOGGER.info(
        f"Platform notification persisted: id={message.metadata.notification_id}, "
        f"recipient_id={processed.recipient}"
    )


async def _update(message, processed) -> None:
    """Update the existing PENDING record created by notification-service with rendered body."""
    async with IOC_CONTAINER(scope=dishka.Scope.REQUEST) as ioc:
        repo = await ioc.get(NotificationRepository)
        await repo.notifications.update_body_and_status(
            notification_id=message.metadata.notification_id,
            body=processed.body,
        )
        await repo.notifications.session.commit()


async def _insert(message, processed) -> None:
    """Insert a new record for DELIVERY_FAILED — it has a fresh UUID not yet in the DB."""
    notification = NotificationTable(
        id=message.metadata.notification_id,
        recipient_id=UUID(processed.recipient),
        recipient_address=processed.recipient,
        notification_type=message.metadata.notification_type.value,
        channel=NotificationChannel.PLATFORM.value,
        priority=message.metadata.priority,
        status=NotificationStatus.SENT,
        body=processed.body,
    )
    async with IOC_CONTAINER(scope=dishka.Scope.REQUEST) as ioc:
        repo = await ioc.get(NotificationRepository)
        await repo.notifications.create(obj_in=notification)
        await repo.notifications.session.commit()
