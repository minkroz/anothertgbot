
import asyncio
import random
import json
from pathlib import Path
from typing import Dict
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Конфигурация бота
BOT_TOKEN = "BOT_TOKEN"
ADMIN_ID = Айди админа в тг
REPORT_CHAT_ID = ADMIN_ID
DB_FILE = Path("users_db.json")

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Класс для работы с базой данных
class Database:
    def __init__(self):
        self.users: Dict[int, Dict[str, float]] = {}
        self.limited_spins_used = 0
        self.load()

    def load(self):
        try:
            if DB_FILE.exists():
                with open(DB_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.users = {int(k): v for k, v in data.get('users', {}).items()}
                    self.limited_spins_used = data.get('limited_spins_used', 0)
        except Exception as e:
            print(f"Ошибка загрузки базы: {e}")

    def save(self):
        try:
            with open(DB_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    'users': self.users,
                    'limited_spins_used': self.limited_spins_used
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения базы: {e}")

    def get_user(self, user_id: int) -> Dict[str, float]:
        if user_id not in self.users:
            self.users[user_id] = {"diamonds": 0.0, "special_spins": 0}
            self.save()
        return self.users[user_id]

# Инициализация базы данных
db = Database()

# Награды для рулеток (остаются без изменений)
COMMON_REWARDS = [
    ("Ничего", 0.6),
    ("0.5 алмаза", 0.25),
    ("Desk Calendar", 0.1),
    ("Homemade Cake", 0.04),
    ("1 алмаз", 0.01)
]

ADVANCED_REWARDS = [
    ("Ничего", 0.5),
    ("Desk Calendar", 0.2),
    ("1 алмаз", 0.1),
    ("Homemade Cake", 0.1),
    ("Lunar Snake", 0.1)
]

ELITE_REWARDS = [
    ("Ничего", 0.4),
    ("Homemade Cake", 0.35),
    ("Lunar Snake", 0.15),
    ("Party Sparkler", 0.09),
    ("2 алмаза", 0.01)
]

LIMITED_REWARDS = [
    ("Ничего", 0.40),
    ("Candy Cane", 0.15),
    ("Snow Globe", 0.15),
    ("Hex Pot", 0.15),
    ("Santa Hat", 0.15)
]

PREMIUM_REWARDS = [
    ("Ничего", 0.25),
    ("2 алмаза", 0.35),
    ("Love Potion", 0.2),
    ("Jack-in-the-box Model Amogus", 0.1),
    ("4 алмаза", 0.09),
    ("vintage cigar", 0.01)
]

# Клавиатуры (остаются без изменений)
def get_spin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Обычная (0.25 алмаза)")],
            [KeyboardButton(text="Продвинутая (0.5 алмаза)")],
            [KeyboardButton(text="Элитная (1 алмаз)")],
            [KeyboardButton(text="Лимитированная (0.6 алмаза)")],
            [KeyboardButton(text="Премиальная (2 алмаза)")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

def get_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/balance"), KeyboardButton(text="/spin")],
            [KeyboardButton(text="/topup")]
        ],
        resize_keyboard=True
    )

# Вспомогательные функции
def spin_roulette(rewards):
    rand = random.random()
    cumulative = 0
    for prize, prob in rewards:
        cumulative += prob
        if rand < cumulative:
            return prize
    return rewards[-1][0]

async def send_spin_report(user_id: int, spin_type: str, prize: str, cost: float):
    user = db.get_user(user_id)
    report = (
        f"🎰 Отчет о прокрутке\n"
        f"Пользователь: {user_id}\n"
        f"Тип рулетки: {spin_type}\n"
        f"Потрачено: {cost} алмазов\n"
        f"Выигрыш: {prize}\n"
        f"Баланс: {user['diamonds']} алмазов"
    )
    await bot.send_message(REPORT_CHAT_ID, report)

# Обработчики команд
@dp.message(Command("start"))
async def start(message: types.Message):
    db.get_user(message.from_user.id)
    await message.answer(
        "🎰 Добро пожаловать в бота с рулетками!\n"
        "/balance - ваш баланс\n"
        "/spin - крутить рулетки\n"
        "/topup - прайс на алмазы",
        reply_markup=get_main_keyboard()
    )

@dp.message(Command("balance"))
async def balance(message: types.Message):
    user = db.get_user(message.from_user.id)
    await message.answer(
        f"💎 Ваш баланс:\n"
        f"Алмазы: {user['diamonds']}\n"
        f"Специальные прокрутки: {user['special_spins']}"
    )

@dp.message(Command("spin"))
async def spin_menu(message: types.Message):
    await message.answer(
        "Выберите рулетку:\n"
        "Список рулеток: Обычная- стоимость 0,25 алмаза, шансы: ничего-60%, 0,5 алмаза-25%, desk calendar-10%, homemade cake-4%, 1 алмаз- 1%.\n"
    "Продвинутая- стоимость 0,5 алмаза, шансы: ничего-50%, desk calendar-20%, 1 алмаз- 10%, homemade cake-10%, lunar snake-10%.\n"
    "Элитная- стоимость 1 алмаз, шансы: ничего-40%, homemade cake-35%, lunar snake-15%, party sparkler-9%, 2 алмаза-1%.\n"
    "Лимитированная(только 5 прокрутов на всех)- стоимость 0,6 алмаза, шансы: ничего-40%, candy cane-15%, snow globe-15%, hex pot-15%, santa hat-15%.\n"
    "Премиальная- стоимость 2 алмаза, шансы: ничего-25%, 2 алмаза-35%,  love potion-20%, jack-in-the-box model amogus-10%, 4 алмаза-9%, vintage cigar-1%.",
        reply_markup=get_spin_keyboard()
    )

@dp.message(lambda message: message.text == "Назад")
async def back_to_menu(message: types.Message):
    await message.answer("Главное меню:", reply_markup=get_main_keyboard())

@dp.message(lambda message: message.text.startswith((
    "Обычная", "Продвинутая", "Элитная", "Лимитированная", "Премиальная"
)))
async def handle_spin(message: types.Message):
    user = db.get_user(message.from_user.id)
    spin_text = message.text
    
    # Определяем тип рулетки
    if spin_text.startswith("Обычная"):
        spin_type = "Обычная"
        cost = 0.25
        rewards = COMMON_REWARDS
    elif spin_text.startswith("Продвинутая"):
        spin_type = "Продвинутая"
        cost = 0.5
        rewards = ADVANCED_REWARDS
    elif spin_text.startswith("Элитная"):
        spin_type = "Элитная"
        cost = 1.0
        rewards = ELITE_REWARDS
    elif spin_text.startswith("Лимитированная"):
        spin_type = "Лимитированная"
        cost = 0.6
        rewards = LIMITED_REWARDS
        if db.limited_spins_used >= 5:
            await message.answer("Лимитированная рулетка исчерпала все 5 прокруток!")
            return
    elif spin_text.startswith("Премиальная"):
        spin_type = "Премиальная"
        cost = 2.0
        rewards = PREMIUM_REWARDS
    
    # Проверка баланса
    if user["diamonds"] < cost:
        await message.answer("Недостаточно алмазов!", reply_markup=get_spin_keyboard())
        return
    
    # Проверка лимита для лимитированной рулетки
    if spin_type == "Лимитированная" and db.limited_spins_used >= 5:
        await message.answer("Лимитированная рулетка исчерпала все 5 прокруток!")
        return
    
    # Спин
    user["diamonds"] -= cost
    prize = spin_roulette(rewards)
    
    # Обработка выигрыша
    if "алмаз" in prize:
        amount = float(prize.split()[0])
        user["diamonds"] += amount
        prize_text = f"Вы выиграли {amount} алмазов!"
    else:
        prize_text = f"Вы выиграли: {prize}"
    
    # Увеличиваем счетчик лимитированных прокруток
    if spin_type == "Лимитированная":
        db.limited_spins_used += 1
    
    # Сохраняем изменения
    db.save()
    
    # Отправляем результат
    await message.answer(
        f"🎯 Результат ({spin_type}):\n{prize_text}\n"
        f"Осталось алмазов: {user['diamonds']:.2f}",
        reply_markup=get_spin_keyboard()
    )
    
    # Отчет админу
    await send_spin_report(message.from_user.id, spin_type, prize, cost)

@dp.message(Command("add_diamonds"))
async def add_diamonds(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда только для администратора")
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 3:
            raise ValueError("Неверный формат команды")
        
        user_id = int(parts[1])
        amount = float(parts[2])
        
        user = db.get_user(user_id)
        user["diamonds"] += amount
        db.save()
        
        await message.answer(
            f"✅ Пользователю {user_id} выдано {amount} алмазов\n"
            f"Новый баланс: {user['diamonds']} алмазов"
        )
        
        try:
            await bot.send_message(
                user_id,
                f"🎉 Вам начислено {amount} алмазов!\n"
                f"Новый баланс: {user['diamonds']} алмазов"
            )
        except:
            pass
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}\nИспользование: /add_diamonds user_id amount")

@dp.message(Command("reset_limited"))
async def reset_limited(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда только для администратора")
        return
    
    db.limited_spins_used = 0
    db.save()
    await message.answer("✅ Счетчик лимитированных прокруток сброшен")

@dp.message(Command("call"))
async def call_command(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("Эта команда только для администратора")
        return
    
    text_to_send = message.text.replace('/call', '').strip()
    if not text_to_send:
        await message.answer("Использование: /call ваш текст сообщения")
        return
    
    await message.answer(f"⏳ Начинаю рассылку сообщения для {len(db.users)} пользователей...")
    
    success_count = 0
    fail_count = 0
    
    for user_id in db.users.keys():
        try:
            await bot.send_message(user_id, text_to_send)
            success_count += 1
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")
            fail_count += 1
        await asyncio.sleep(0.1)
    
    await message.answer(
        f"✅ Рассылка завершена:\n"
        f"Успешно отправлено: {success_count}\n"
        f"Не удалось отправить: {fail_count}"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
