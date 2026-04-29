from dataclasses import dataclass
from dataclasses import field

from utils_library.Configuration.meta_config import AbstractMetaConfig


@dataclass
class NotificationDatabaseConfiguration(AbstractMetaConfig):
    db_host: str = field(
        default="127.0.0.1",
        metadata={"docs": "HOST", "required": False},
    )
    db_port: int = field(
        default=5432,
        metadata={"docs": "PORT", "required": False},
    )
    db_user: str = field(
        default="postgres",
        metadata={"docs": "db user", "required": False, "hidden": True},
    )
    db_pwd: str = field(
        default="postgres",
        metadata={"docs": "db pwd", "required": False, "hidden": True},
    )
    db_name: str = field(
        default="notification_db",
        metadata={"docs": "database name", "required": False},
    )


@dataclass
class PlatformHandlerConfig(AbstractMetaConfig):
    max_retries: int = field(
        default=5,
        metadata={"docs": "Max retry attempts before DELIVERY_FAILED", "required": False},
    )
    retry_delay: float = field(
        default=2.0,
        metadata={"docs": "Delay between retries in seconds", "required": False},
    )
    metrics_port: int = field(
        default=9090,
        metadata={"docs": "Prometheus metrics port", "required": False},
    )


NOTIFICATION_DATABASE = NotificationDatabaseConfiguration()
PLATFORM_HANDLER_CONFIG = PlatformHandlerConfig()