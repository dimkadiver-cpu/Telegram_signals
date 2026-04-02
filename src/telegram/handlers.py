import logging
from datetime import datetime, timezone
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

_EDIT_TIMEOUT_SECONDS = 300  # 5 minutes
from sqlmodel import select
from src.db.models import TelegramDraft, DraftStatus, Trader
from src.db.session import get_session
from src.dispatcher.dispatcher import MessageDispatcher
from src.exchange.listener_manager import ListenerManager

logger = logging.getLogger(__name__)
router = Router()


class EditState(StatesGroup):
    waiting_for_text = State()


class AddTraderState(StatesGroup):
    waiting_for_name = State()
    waiting_for_api_key = State()
    waiting_for_api_secret = State()
    waiting_for_review_chat_id = State()
    waiting_for_channel_id = State()


@router.callback_query(lambda c: c.data and c.data.startswith("approve:"))
async def on_approve(callback: CallbackQuery, dispatcher: MessageDispatcher) -> None:
    draft_id = int(callback.data.split(":")[1])
    async for session in get_session():
        draft = await session.get(TelegramDraft, draft_id)
        if not draft or draft.status != DraftStatus.PENDING:
            await callback.answer("Bozza non trovata o già processata.")
            return
        draft.status = DraftStatus.APPROVED
        await session.commit()
        await dispatcher.dispatch(draft)
    await callback.message.delete()
    await callback.answer("Messaggio inviato!")


@router.callback_query(lambda c: c.data and c.data.startswith("edit:"))
async def on_edit(callback: CallbackQuery, state: FSMContext) -> None:
    draft_id = int(callback.data.split(":")[1])
    await state.update_data(
        draft_id=draft_id,
        edit_started_at=datetime.now(tz=timezone.utc).timestamp(),
    )
    await state.set_state(EditState.waiting_for_text)
    await callback.message.reply(
        f"Scrivi il nuovo testo del messaggio (timeout {_EDIT_TIMEOUT_SECONDS // 60} min):"
    )
    await callback.answer()


@router.message(EditState.waiting_for_text)
async def on_edit_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()

    # Auto-reset if timeout has elapsed
    started_at = data.get("edit_started_at", 0)
    elapsed = datetime.now(tz=timezone.utc).timestamp() - started_at
    if elapsed > _EDIT_TIMEOUT_SECONDS:
        await state.clear()
        await message.reply(
            "Sessione di modifica scaduta. Usa il pulsante Modifica per ricominciare."
        )
        return

    draft_id = data.get("draft_id")
    async for session in get_session():
        draft = await session.get(TelegramDraft, draft_id)
        if draft:
            draft.message_text = message.text
            await session.commit()
    await state.clear()
    await message.reply("Bozza aggiornata. Usa /approva per inviarla.")


@router.callback_query(lambda c: c.data and c.data.startswith("delete:"))
async def on_delete(callback: CallbackQuery) -> None:
    draft_id = int(callback.data.split(":")[1])
    async for session in get_session():
        draft = await session.get(TelegramDraft, draft_id)
        if draft:
            draft.status = DraftStatus.REJECTED
            await session.commit()
    await callback.message.delete()
    await callback.answer("Bozza eliminata.")


@router.message(Command("add_trader"))
async def cmd_add_trader(message: Message, state: FSMContext) -> None:
    await state.set_state(AddTraderState.waiting_for_name)
    await message.reply("Inserisci nome trader:")


@router.message(AddTraderState.waiting_for_name)
async def add_trader_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AddTraderState.waiting_for_api_key)
    await message.reply("Inserisci Binance API key:")


@router.message(AddTraderState.waiting_for_api_key)
async def add_trader_api_key(message: Message, state: FSMContext) -> None:
    await state.update_data(binance_api_key=message.text.strip())
    await state.set_state(AddTraderState.waiting_for_api_secret)
    await message.reply("Inserisci Binance API secret:")


@router.message(AddTraderState.waiting_for_api_secret)
async def add_trader_api_secret(message: Message, state: FSMContext) -> None:
    await state.update_data(binance_api_secret=message.text.strip())
    await state.set_state(AddTraderState.waiting_for_review_chat_id)
    await message.reply("Inserisci Telegram review chat id:")


@router.message(AddTraderState.waiting_for_review_chat_id)
async def add_trader_review_chat(message: Message, state: FSMContext) -> None:
    await state.update_data(telegram_review_chat_id=message.text.strip())
    await state.set_state(AddTraderState.waiting_for_channel_id)
    await message.reply("Inserisci Telegram channel id di output:")


@router.message(AddTraderState.waiting_for_channel_id)
async def add_trader_channel(
    message: Message,
    state: FSMContext,
    listener_manager: ListenerManager,
) -> None:
    data = await state.get_data()
    channel_id = message.text.strip()

    async for session in get_session():
        trader = Trader(
            name=data["name"],
            binance_api_key=data["binance_api_key"],
            binance_api_secret=data["binance_api_secret"],
            telegram_review_chat_id=data["telegram_review_chat_id"],
            telegram_channel_id=channel_id,
            is_active=True,
        )
        session.add(trader)
        await session.commit()
        await session.refresh(trader)

    await listener_manager.add_trader(trader)
    await state.clear()
    await message.reply(f"Trader creato: id={trader.id}, nome={trader.name}")


@router.message(Command("list_traders"))
async def cmd_list_traders(message: Message) -> None:
    async for session in get_session():
        result = await session.execute(select(Trader).order_by(Trader.id))
        traders = result.scalars().all()
    if not traders:
        await message.reply("Nessun trader registrato.")
        return

    lines = ["Traders registrati:"]
    for trader in traders:
        status = "active" if trader.is_active else "inactive"
        lines.append(
            f"- id={trader.id} | {trader.name} | review={trader.telegram_review_chat_id} | "
            f"channel={trader.telegram_channel_id} | {status}"
        )
    await message.reply("\n".join(lines))
