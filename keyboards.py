from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔓 Регистрация пользователей", callback_data="register_user"
            ),
            InlineKeyboardButton(
                text="📊 Общая информация", callback_data="total_info"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📩 Просмотр заказов", callback_data="view_orders"
            ),
            InlineKeyboardButton(
                text="📈 Отчет по заказам", callback_data="report_orders"
            ),
        ],
        [
            InlineKeyboardButton(
                text="✏️ Создание заявки", callback_data="create_appointment"
            ),
            InlineKeyboardButton(
                text="🔍 Поиск клиента", callback_data="search_client"
            ),
        ],
    ]
)

choose_role_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔓 Админ", callback_data="admin"),
            InlineKeyboardButton(text="📊 Аналитик", callback_data="analyst"),
        ],
        [
            InlineKeyboardButton(text="📩 Менеджер", callback_data="manager"),
            InlineKeyboardButton(text="🔨 Мастер", callback_data="master"),
        ],
        [
            InlineKeyboardButton(text="Меню", callback_data="menu"),
        ],
    ]
)
choose_total_info_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👨‍💼 Клиенты", callback_data="info_clients"),
            InlineKeyboardButton(
                text="🔨 Популярные услуги", callback_data="info_services"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💰 Доход филиалов", callback_data="info_branches"
            ),
            InlineKeyboardButton(
                text="📉 Заканчивающиеся детали", callback_data="info_parts"
            ),
        ],
        [
            InlineKeyboardButton(text="Меню", callback_data="menu"),
        ],
    ]
)
