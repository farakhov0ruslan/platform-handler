"""
Integration test: LocalNotificationClient → serialize → process_platform_message → mock DB.

Does not require RabbitMQ or PostgreSQL — IOC_CONTAINER is patched to a mock repo.
"""
from notification_registry import LocalNotificationClient
from notification_registry import NotificationChannel
from notification_registry import NotificationType
from notification_registry import serialize_message
from platform_handler.processor import process_platform_message


class TestPlatformPipeline:
    def test_delivery_failed_persisted_via_processor(
        self, delivery_failed_payload, mock_crud, patched_ioc
    ):
        from notification_registry import NotificationMessage
        from notification_registry import NotificationMetadata
        from notification_registry import NotificationPriority
        from uuid import uuid4

        message = NotificationMessage(
            metadata=NotificationMetadata(
                notification_id=uuid4(),
                notification_type=NotificationType.DELIVERY_FAILED,
                channel=NotificationChannel.PLATFORM,
                priority=NotificationPriority.NORMAL,
            ),
            payload=delivery_failed_payload,
        )
        body = serialize_message(message)

        process_platform_message(body)

        mock_crud.create.assert_awaited_once()
        notification = mock_crud.create.call_args.kwargs["obj_in"]
        assert notification.body is not None
        assert delivery_failed_payload.original_channel.title() in notification.body

    def test_non_delivery_failed_message_updates_existing_record(
        self, analytics_payload, mock_crud, patched_ioc
    ):
        from notification_registry import NotificationMessage
        from notification_registry import NotificationMetadata
        from notification_registry import NotificationPriority
        from uuid import uuid4

        message = NotificationMessage(
            metadata=NotificationMetadata(
                notification_id=uuid4(),
                notification_type=NotificationType.ANALYTICS,
                channel=NotificationChannel.PLATFORM,
                priority=NotificationPriority.NORMAL,
            ),
            payload=analytics_payload,
        )
        body = serialize_message(message)

        process_platform_message(body)

        mock_crud.create.assert_not_awaited()
        mock_crud.update_body_and_status.assert_awaited_once()
