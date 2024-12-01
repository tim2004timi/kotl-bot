import asyncpg
from aiogram import Dispatcher, Router, F
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from exceptions import UsernameOccupied
from keyboards import (
    menu_inline_keyboard,
    choose_role_inline_keyboard,
    choose_total_info_inline_keyboard,
)
from service import (
    check_occupied_username,
    register_user,
    get_info_clients,
    get_info_services,
    get_info_branches,
    get_info_parts,
    get_view_orders,
    get_report_orders,
    search_client,
    get_clients,
    get_branches,
    get_services,
    create_appointment,
)
from utils import edit_message

router = Router()


class RegisterState(StatesGroup):
    username = State()
    password = State()
    role = State()


class SearchClientState(StatesGroup):
    string = State()


class CreateAppointmentState(StatesGroup):
    client_id = State()
    branch_id = State()
    service_id = State()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"<b>Добро пожаловать, {message.from_user.username}!</b>\n\n"
        f"В этом боте можете управлять СУБД для авто/мото салонов",
        reply_markup=menu_inline_keyboard,
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(
        f"<b>Меню</b>\n\nВыберите нужную функцию и нажмите на кнопку",
        reply_markup=menu_inline_keyboard,
    )


@router.callback_query(F.data == "menu")
async def menu_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        f"<b>Меню</b>\n\nВыберите нужную функцию и нажмите на кнопку",
        reply_markup=menu_inline_keyboard,
    )


@router.callback_query(F.data == "register_user")
@edit_message
async def register_user_callback(
    _: CallbackQuery,
    state: FSMContext,
) -> tuple[str, InlineKeyboardMarkup | None]:
    await state.set_state(RegisterState.username)
    return "🔖 Введите username:", None


@router.message(RegisterState.username)
async def register_user_username_state(message: Message, state: FSMContext):
    username = message.text.strip()

    try:
        await check_occupied_username(username)
    except UsernameOccupied:
        await message.answer(
            f"🚫 Данный username уже занят. Используйте другой username",
        )
        return

    await state.update_data(username=username)
    await message.answer("🔖 Введите пароль:")
    await state.set_state(RegisterState.password)


@router.message(RegisterState.password)
async def register_user_password_state(message: Message, state: FSMContext):
    password = message.text.strip()

    await state.update_data(password=password)
    await message.answer("🔖 Выберите роль", reply_markup=choose_role_inline_keyboard)
    await state.set_state(RegisterState.role)


@router.callback_query(F.data.in_(["admin", "analyst", "manager", "master"]))
@edit_message
async def register_user_role_state(callback: CallbackQuery, state: FSMContext):
    role = callback.data.strip()
    await state.update_data(role=role)
    data = await state.get_data()

    try:
        await register_user(data)
    except Exception as e:
        await callback.message.answer(
            f"🚫 Ошибка {e}",
        )
        return

    await state.clear()
    await callback.answer()
    await callback.message.answer(
        "✅ Пользователь успешно зарегистрирован", reply_markup=menu_inline_keyboard
    )


@router.callback_query(F.data == "total_info")
@edit_message
async def total_info_callback(_: CallbackQuery):
    return (
        "Выберите информацию, которую хотите просмотреть",
        choose_total_info_inline_keyboard,
    )
    # await callback.message.answer(
    #     "Выберите информацию, которую хотите просмотреть",
    #     reply_markup=choose_total_info_inline_keyboard,
    # )


@router.callback_query(F.data == "info_clients")
@edit_message
async def info_clients_callback(callback: CallbackQuery):
    await callback.answer()
    answer = await get_info_clients()
    return answer, choose_total_info_inline_keyboard


@router.callback_query(F.data == "info_services")
@edit_message
async def info_services_callback(callback: CallbackQuery):
    await callback.answer()
    answer = await get_info_services()
    return answer, choose_total_info_inline_keyboard


@router.callback_query(F.data == "info_branches")
@edit_message
async def info_branches_callback(callback: CallbackQuery):
    await callback.answer()
    answer = await get_info_branches()
    return answer, choose_total_info_inline_keyboard


@router.callback_query(F.data == "info_parts")
@edit_message
async def info_parts_callback(callback: CallbackQuery):
    await callback.answer()
    answer = await get_info_parts()
    return answer, choose_total_info_inline_keyboard


@router.callback_query(F.data == "view_orders")
async def view_orders_callback(callback: CallbackQuery):
    await callback.answer()
    answers = await get_view_orders()
    for i in range(len(answers)):
        if i + 1 == len(answers):
            await callback.message.answer(answers[i], reply_markup=menu_inline_keyboard)
        else:
            await callback.message.answer(answers[i])


@router.callback_query(F.data == "report_orders")
@edit_message
async def report_orders_callback(callback: CallbackQuery):
    await callback.answer()
    answer = await get_report_orders()
    return answer, menu_inline_keyboard


@router.callback_query(F.data == "create_appointment")
async def create_appointment_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    clients = await get_clients()
    await callback.message.answer(clients)
    await callback.message.answer("Напишите id клиента")
    await state.set_state(CreateAppointmentState.client_id)


@router.message(CreateAppointmentState.client_id)
async def create_appointment_client_id_state(message: Message, state: FSMContext):
    id_ = message.text.strip()

    await state.update_data(service_id=id_)
    await state.update_data(client_id=id_)
    branches = await get_branches()
    await message.answer(branches)
    await message.answer("Напишите id филиала")
    await state.set_state(CreateAppointmentState.branch_id)


@router.message(CreateAppointmentState.branch_id)
async def create_appointment_branch_id_state(message: Message, state: FSMContext):
    id_ = message.text.strip()

    await state.update_data(branch_id=id_)
    data = await state.get_data()
    await create_appointment(data)

    await message.answer("✅ Заявка успешно создана", reply_markup=menu_inline_keyboard)
    await state.clear()


@router.callback_query(F.data == "search_client")
@edit_message
async def search_client_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SearchClientState.string)
    return "🔖 Введите строку для поиска", None


@router.message(SearchClientState.string)
async def search_client_state(message: Message, state: FSMContext):
    string = message.text.strip()

    answer = await search_client(string)
    await state.clear()
    await message.answer(answer, reply_markup=menu_inline_keyboard)


def register_handlers(dp: Dispatcher):
    dp.include_router(router)
