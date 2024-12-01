import datetime
from typing import Any

import asyncpg

from database import dsn
from exceptions import UsernameOccupied
from utils import hash_password


async def check_occupied_username(username: str):
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch("SELECT username FROM users WHERE username = $1", username)
    if len(rows) >= 1:
        raise UsernameOccupied


async def register_user(data: dict[str, Any]):
    conn = await asyncpg.connect(dsn=dsn)
    user = {
        "username": data["username"],
        "password": hash_password(data["password"]),
        "role": data["role"],
    }
    await conn.execute(
        """INSERT INTO users (username, password, role) 
    VALUES ($1, $2, $3)""",
        user["username"],
        user["password"],
        user["role"],
    )


async def get_info_clients() -> str:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
    WITH total_services AS (
    SELECT
        o.client_id,
        SUM(s.price) AS services_total
    FROM orders o
    JOIN order_services os ON o.id = os.order_id
    JOIN services s ON os.service_id = s.id
    GROUP BY o.client_id
    ),
    total_parts AS (
        SELECT
            o.client_id,
            SUM(p.price * op.quantity) AS parts_total
        FROM orders o
        JOIN order_parts op ON o.id = op.order_id
        JOIN parts p ON op.part_id = p.id
        GROUP BY o.client_id
    )
    SELECT
        c.id,
        c.full_name,
        c.status,
        COALESCE(ts.services_total, 0) + COALESCE(tp.parts_total, 0) AS total_spent
    FROM clients c
    LEFT JOIN total_services ts ON c.id = ts.client_id
    LEFT JOIN total_parts tp ON c.id = tp.client_id
    ORDER BY total_spent DESC;
    """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Список клиентов с их статусом и общей суммой потраченных денег</b>\n\n"
    for row in rows:
        full_name = row["full_name"]
        status = row["status"]
        total_spent = row["total_spent"]
        answer += f"{full_name} ({status}) - {total_spent} ₽\n"

    return answer


async def get_info_services():
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
    SELECT
        s.name,
        COUNT(*) AS service_count
    FROM order_services os
    JOIN services s ON os.service_id = s.id
    GROUP BY s.name
    ORDER BY service_count DESC
    LIMIT 10;
    """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Топ-10 самых популярных услуг</b>\n\n"
    for row in rows:
        name = row["name"]
        count = row["service_count"]
        answer += f"{name} - {count} раз\n"

    return answer


async def get_info_branches():
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        WITH service_income AS (
            SELECT
                o.branch_id,
                SUM(s.price) AS total_service_income
            FROM orders o
            JOIN order_services os ON o.id = os.order_id
            JOIN services s ON os.service_id = s.id
            GROUP BY o.branch_id
            ),
        part_income AS (
            SELECT
                o.branch_id,
                SUM(p.price * op.quantity) AS total_part_income
            FROM orders o
            JOIN order_parts op ON o.id = op.order_id
            JOIN parts p ON op.part_id = p.id
            GROUP BY o.branch_id
            )
        SELECT
            b.id,
            b.city,
            b.address,
            COALESCE(si.total_service_income, 0) + COALESCE(pi.total_part_income, 0) AS total_income
        FROM branches b
        LEFT JOIN service_income si ON b.id = si.branch_id
        LEFT JOIN part_income pi ON b.id = pi.branch_id
        ORDER BY total_income DESC;
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Общий доход, сгенерированный каждым филиалом</b>\n\n"
    for row in rows:
        city = row["city"]
        address = row["address"]
        total_income = row["total_income"]
        answer += f"{city} ({address}) - {total_income} ₽\n"

    return answer


async def get_info_parts():
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT
        p.id,
        p.name,
        p.stock_quantity
        FROM parts p
        WHERE p.stock_quantity <= 5
        ORDER BY p.stock_quantity ASC;
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Список запчастей с низким остатком на складе</b>\n\n"
    for row in rows:
        name = row["name"]
        stock_quantity = row["stock_quantity"]
        answer += f"{name} - {stock_quantity} шт.\n"

    return answer


async def get_view_orders() -> list[str]:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT
        o.id AS order_id,
        c.full_name AS client_name,
        b.city AS branch_city,
        b.address AS branch_address,
        o.created_at,
        o.completed_at
        FROM orders o
        JOIN clients c ON o.client_id = c.id
        JOIN branches b ON o.branch_id = b.id
        ORDER BY o.created_at DESC;
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Список заказов</b>\n\n"
    count = 0
    answers = []
    for row in rows:
        client_name = row["client_name"]
        branch_city = row["branch_city"]
        branch_address = row["branch_address"]
        created_at = row["created_at"]
        completed = "Завершен" if row["completed_at"] else "В процессе"
        answer += (
            f"{client_name} - {created_at} ({completed})\n"
            f"{branch_city} {branch_address}\n\n"
        )
        count += 1
        if count >= 20:
            answers.append(answer)
            answer = ""
            count = 0
    if answer:
        answers.append(answer)
    return answers


async def get_report_orders():
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT
        o.completed_at::DATE AS order_date,
        COUNT(o.id) AS total_orders,
        COALESCE(SUM(s.price), 0) AS total_services_income,
        COALESCE(SUM(p.price * op.quantity), 0) AS total_parts_income,
        COALESCE(SUM(s.price), 0) + COALESCE(SUM(p.price * op.quantity), 0) AS total_income
        FROM orders o
        LEFT JOIN order_services os ON o.id = os.order_id
        LEFT JOIN services s ON os.service_id = s.id
        LEFT JOIN order_parts op ON o.id = op.order_id
        LEFT JOIN parts p ON op.part_id = p.id
        WHERE o.completed_at IS NOT NULL
        GROUP BY o.completed_at::DATE
        ORDER BY order_date DESC;
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Отчет по заказам</b>\n\n"
    for row in rows:
        date = row["order_date"]
        total_orders = row["total_orders"]
        total_services_income = row["total_services_income"]
        total_parts_income = row["total_parts_income"]
        total_income = row["total_income"]
        answer += (
            f"{date} - {total_orders} заказов - {total_income} ₽\n"
            f"Услуги: {total_services_income} ₽ | Запчасти: {total_parts_income} ₽\n\n"
        )

    return answer


async def search_client(string: str) -> str:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT
        id,
        full_name,
        phone,
        email,
        status,
        bonus_points
        FROM clients
        WHERE full_name ILIKE '%' || $1 || '%' OR phone ILIKE '%' || $1 || '%';
        """,
        string,
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Совпадения</b>\n\n"
    for row in rows:
        full_name = row["full_name"]
        phone = row["phone"]
        email = row["email"]
        status = row["status"]
        answer += f"{full_name} ({status})\n" f"{email} {phone}\n\n"

    return answer


async def get_clients() -> str:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT id, full_name FROM clients
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Клиенты</b>\n\n"
    for row in rows:
        id_ = row["id"]
        full_name = row["full_name"]

        answer += f"{id_}) {full_name}\n"

    return answer


async def get_branches() -> str:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT id, city, address FROM branches
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Филиалы</b>\n\n"
    for row in rows:
        id_ = row["id"]
        city = row["city"]
        address = row["address"]

        answer += f"{id_}) {city} {address}\n"

    return answer


async def get_services() -> str:
    conn = await asyncpg.connect(dsn=dsn)
    rows = await conn.fetch(
        """
        SELECT id, name FROM services
        """
    )

    if len(rows) == 0:
        return "Пусто"

    answer = "<b>Услуги</b>\n\n"
    for row in rows:
        id_ = row["id"]
        name = row["name"]

        answer += f"{id_}) {name}\n"

    return answer


async def create_appointment(data: dict[str, str]):
    client_id = int(data["client_id"])
    branch_id = int(data["branch_id"])
    service_id = int(data["service_id"])
    date = datetime.datetime.utcnow()

    conn = await asyncpg.connect(dsn=dsn)
    await conn.execute(
        """
        INSERT INTO service_appointments (client_id, branch_id, service_id, appointment_date)
        VALUES ($1, $2, $3, $4);
        """,
        client_id,
        branch_id,
        service_id,
        date,
    )
