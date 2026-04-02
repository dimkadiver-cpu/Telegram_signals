from src.db.models import TraderTemplate
from src.db.session import get_session
from src.events.types import EventType
from sqlmodel import select


class TemplateStore:
    """Loads trader-specific templates from DB."""

    async def get_template(self, trader_id: int, event_type: EventType) -> str | None:
        async for session in get_session():
            query = (
                select(TraderTemplate)
                .where(TraderTemplate.trader_id == trader_id)
                .where(TraderTemplate.event_type == event_type.value)
            )
            result = await session.execute(query)
            template = result.scalar_one_or_none()
            return template.template_text if template else None
        return None
