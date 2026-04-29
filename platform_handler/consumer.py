from notification_registry import ChannelHandlerSettings
from notification_registry import NotificationChannel
from notification_registry import NotificationConsumer
from notification_registry import create_channel_consumer
from utils_library.RabbitMQ.publisher import RabbitPublisher
from utils_library.RabbitMQ.rabbitmq import RabbitMQConfig

from platform_handler.config import PLATFORM_HANDLER_CONFIG
from platform_handler.processor import process_platform_message


def create_consumer(
    rabbitmq_config: RabbitMQConfig,
    publisher: RabbitPublisher,
) -> NotificationConsumer:
    settings = ChannelHandlerSettings(
        channel=NotificationChannel.PLATFORM,
        max_retries=PLATFORM_HANDLER_CONFIG.max_retries,
        retry_delay=PLATFORM_HANDLER_CONFIG.retry_delay,
        failed_error_message="Platform notification persist failed after all retries",
    )
    return create_channel_consumer(
        settings=settings,
        on_message=process_platform_message,
        publisher=publisher,
        rabbitmq_config=rabbitmq_config,
    )
