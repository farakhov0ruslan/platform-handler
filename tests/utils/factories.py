from datetime import UTC
from datetime import datetime
from uuid import uuid4

from polyfactory.factories.pydantic_factory import ModelFactory

from notification_registry import AnalyticsPayload
from notification_registry import DeliveryFailedPayload
from notification_registry import LinkedInDisconnectedPayload
from notification_registry import ResetPasswordPayload


class DeliveryFailedPayloadFactory(ModelFactory[DeliveryFailedPayload]):
    user_id = uuid4()
    original_channel = "email"
    original_type = "reset_password"
    error_message = "SMTP connection refused"
    retry_count = 5
    failed_at = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)


class ResetPasswordPayloadFactory(ModelFactory[ResetPasswordPayload]):
    reset_url = "https://example.com/reset?token=abc"
    expires_at = datetime(2026, 1, 2, 0, 0, 0, tzinfo=UTC)
    user_name = "Test User"
    user_ip = "127.0.0.1"
    user_agent = "test/1.0"


class AnalyticsPayloadFactory(ModelFactory[AnalyticsPayload]):
    report_type = "weekly"
    period_start = datetime(2026, 1, 1, tzinfo=UTC)
    period_end = datetime(2026, 1, 7, tzinfo=UTC)
    total_leads = 100
    active_campaigns = 5
    engagement_rate = 42.5
    report_url = "https://example.com/reports/1"


class LinkedInDisconnectedPayloadFactory(ModelFactory[LinkedInDisconnectedPayload]):
    reconnect_url = "https://example.com/linkedin/reconnect"
    disconnected_at = datetime(2026, 1, 1, tzinfo=UTC)
    reason = "session_expired"
    affected_campaigns = 3
    active_sequences = 2
