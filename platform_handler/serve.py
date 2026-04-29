import os
import signal
from pathlib import Path


import fire
from notification_registry import NotificationChannel
from prometheus_client import start_http_server
from utils_library.Logging.log import configure_logger
from utils_library.Logging.log import get_logger
from utils_library.RabbitMQ.correct_consumer import ThreadedRabbitConsumer
from utils_library.RabbitMQ.publisher import RabbitPublisher
from utils_library.RabbitMQ.rabbitmq import RABBIT_MQ_CONFIG

from platform_handler.config import PLATFORM_HANDLER_CONFIG
from platform_handler.consumer import create_consumer

LOGGER = get_logger(__name__)


def serve() -> None:
    LOGGER.info("Starting platform-handler")
    LOGGER.info(f"Prometheus metrics on :{PLATFORM_HANDLER_CONFIG.metrics_port}")
    start_http_server(PLATFORM_HANDLER_CONFIG.metrics_port)
    LOGGER.info(f"Prometheus metrics on :{PLATFORM_HANDLER_CONFIG.metrics_port}")

    with RabbitPublisher(RABBIT_MQ_CONFIG) as publisher:
        consumer = create_consumer(RABBIT_MQ_CONFIG, publisher)
        threaded = ThreadedRabbitConsumer(consumer)

        def _shutdown(signum, _frame) -> None:
            LOGGER.info(f"Received signal {signum}, shutting down gracefully...")
            threaded.stop()

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

        LOGGER.info(
            f"Platform handler started, listening on {NotificationChannel.PLATFORM.queue_name}"
        )
        threaded.start()
        threaded.join()

        if threaded._consumer.stopped:
            LOGGER.error(
                "Consumer thread exited due to an error — check logs above for details"
            )

    LOGGER.info("Platform handler stopped")


if __name__ == "__main__":  # pragma: no cover
    configure_logger("platform_handler", "INFO", json_logger=True)
    configure_logger(__name__, "INFO", json_logger=True)
    configure_logger("notification_registry", "INFO", json_logger=True)
    configure_logger("utils_library", "INFO", json_logger=True)
    fire.Fire(serve)
