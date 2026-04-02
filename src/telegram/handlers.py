import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from sqlmodel import select
from src.db.models import TelegramDraft, DraftStatus
from src.db.session import get_session
from src.dispatcher.dispatcher import MessageDispatcher

logger = logging.getLogger(__name__)
router = Router()


class EditState(StatesGroup):
    waiting_for_text = State()


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
    await state.update_data(draft_id=draft_id)
    await state.set_state(EditState.waiting_for_text)
    await callback.message.reply("Scrivi il nuovo testo del messaggio:")
    await callback.answer()


@router.message(EditState.waiting_for_text)
async def on_edit_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
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
    # TODO: implement FSM wizard for trader registration
    await message.reply("Wizard add_trader – da implementare (F3-05).")


@router.message(Command("list_traders"))
async def cmd_list_traders(message: Message) -> None:
    # TODO: query DB and list active traders
    await message.reply("Lista traders – da implementare (F3-05).")
