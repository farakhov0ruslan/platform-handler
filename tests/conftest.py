from unittest.mock import AsyncMock
from unittest.mock import MagicMock

import pytest

from notification_registry import NotificationType
from tests.utils.factories import AnalyticsPayloadFactory
from tests.utils.factories import DeliveryFailedPayloadFactory
from tests.utils.factories import LinkedInDisconnectedPayloadFactory
from tests.utils.factories import ResetPasswordPayloadFactory
from tests.utils.messages import build_message


@pytest.fixture
def delivery_failed_payload():
    return DeliveryFailedPayloadFactory.build()


@pytest.fixture
def reset_password_payload():
    return ResetPasswordPayloadFactory.build()


@pytest.fixture
def analytics_payload():
    return AnalyticsPayloadFactory.build()


@pytest.fixture
def linkedin_disconnected_payload():
    return LinkedInDisconnectedPayloadFactory.build()


@pytest.fixture
def delivery_failed_message(delivery_failed_payload):
    return build_message(delivery_failed_payload, NotificationType.DELIVERY_FAILED)


@pytest.fixture
def reset_password_message(reset_password_payload):
    return build_message(reset_password_payload, NotificationType.RESET_PASSWORD)


@pytest.fixture
def analytics_message(analytics_payload):
    return build_message(analytics_payload, NotificationType.ANALYTICS)


@pytest.fixture
def mock_crud(mocker):
    crud = MagicMock()
    crud.create = AsyncMock(return_value=None)
    crud.update_body_and_status = AsyncMock(return_value=None)
    crud.session = MagicMock()
    crud.session.commit = AsyncMock(return_value=None)
    return crud


@pytest.fixture
def mock_repo(mock_crud):
    from platform_handler.ioc import NotificationRepository
    return NotificationRepository(notifications=mock_crud)


@pytest.fixture
def patched_ioc(mocker, mock_repo):
    """Patch IOC_CONTAINER so process_platform_message uses mock_repo."""
    ioc_mock = AsyncMock()
    ioc_mock.get = AsyncMock(return_value=mock_repo)

    ctx_mock = AsyncMock()
    ctx_mock.__aenter__ = AsyncMock(return_value=ioc_mock)
    ctx_mock.__aexit__ = AsyncMock(return_value=False)

    mocker.patch("platform_handler.processor.IOC_CONTAINER", return_value=ctx_mock)
    return ioc_mock
