from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import update
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from utils_library.AlchemyRepository import crud

from platform_handler.infrastructure.enums import NotificationStatus
from platform_handler.infrastructure.models import NotificationTable


class CRUDNotification(
    crud.CRUDBaseCreate[NotificationTable],
    crud.CRUDBaseSelect[NotificationTable],
    crud.CRUDBaseDelete[NotificationTable],
    crud.CRUDBaseUpdate[NotificationTable],
):
    def __init__(self, model: type[NotificationTable], session: AsyncSession):
        crud.CRUDBaseCreate.__init__(self, model, session)
        crud.CRUDBaseSelect.__init__(self, model, session)
        crud.CRUDBaseDelete.__init__(self, model, session)
        crud.CRUDBaseUpdate.__init__(self, model, session)

    async def get(self, *, id: UUID, ignore_deleted: bool = True) -> Optional[NotificationTable]:
        stmt = select(NotificationTable).where(NotificationTable.id == id)
        results = await self.get_multi(query=stmt, limit=1, ignore_deleted=ignore_deleted)
        return results[0] if results else None

    async def update_body_and_status(self, notification_id: UUID, body: str) -> None:
        stmt = (
            update(NotificationTable)
            .where(NotificationTable.id == notification_id)
            .values(body=body, status=NotificationStatus.SENT, sent_at=datetime.utcnow())
        )
        await self.session.execute(stmt)
