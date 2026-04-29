import pytest

from notification_registry import NotificationType
from notification_registry import serialize_message
from platform_handler.infrastructure.enums import NotificationStatus
from platform_handler.infrastructure.models import NotificationTable
from platform_handler.processor import process_platform_message
from tests.utils.factories import AnalyticsPayloadFactory
from tests.utils.messages import build_message


class TestProcessPlatformMessage:
    def test_persists_delivery_failed_to_db(
        self, delivery_failed_message, mock_crud, patched_ioc
    ):
        body = serialize_message(delivery_failed_message)

        process_platform_message(body)

        mock_crud.create.assert_awaited_once()

    def test_updates_existing_platform_notification(self, analytics_payload, mock_crud, patched_ioc):
        analytics_message = build_message(analytics_payload, NotificationType.ANALYTICS)
        body = serialize_message(analytics_message)

        process_platform_message(body)

        mock_crud.create.assert_not_awaited()
        mock_crud.update_body_and_status.assert_awaited_once()

    def test_recipient_id_from_payload_user_id(
        self, delivery_failed_payload, delivery_failed_message, mock_crud, patched_ioc
    ):
        from uuid import UUID
        body = serialize_message(delivery_failed_message)

        process_platform_message(body)

        notification: NotificationTable = mock_crud.create.call_args.kwargs["obj_in"]
        assert notification.recipient_id == UUID(str(delivery_failed_payload.user_id))

    def test_status_is_sent(self, delivery_failed_message, mock_crud, patched_ioc):
        body = serialize_message(delivery_failed_message)

        process_platform_message(body)

        notification: NotificationTable = mock_crud.create.call_args.kwargs["obj_in"]
        assert notification.status == NotificationStatus.SENT

    def test_channel_is_platform(self, delivery_failed_message, mock_crud, patched_ioc):
        from notification_registry import NotificationChannel
        body = serialize_message(delivery_failed_message)

        process_platform_message(body)

        notification: NotificationTable = mock_crud.create.call_args.kwargs["obj_in"]
        assert notification.channel == NotificationChannel.PLATFORM

    def test_db_failure_propagates(
        self, delivery_failed_message, mock_crud, patched_ioc
    ):
        mock_crud.create.side_effect = RuntimeError("DB down")
        body = serialize_message(delivery_failed_message)

        with pytest.raises(RuntimeError, match="DB down"):
            process_platform_message(body)

    def test_notification_id_from_metadata(
        self, delivery_failed_message, mock_crud, patched_ioc
    ):
        body = serialize_message(delivery_failed_message)

        process_platform_message(body)

        notification: NotificationTable = mock_crud.create.call_args.kwargs["obj_in"]
        assert notification.id == delivery_failed_message.metadata.notification_id
