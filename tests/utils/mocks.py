from pytest_mock import MockerFixture


def patched_publisher(mocker: MockerFixture):
    """Patch platform_handler.client.RabbitPublisher to a MagicMock usable as context manager."""
    publisher = mocker.MagicMock()
    publisher.__enter__ = mocker.Mock(return_value=publisher)
    publisher.__exit__ = mocker.Mock(return_value=False)
    mocker.patch("platform_handler.client.RabbitPublisher", return_value=publisher)
    return publisher
