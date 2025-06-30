import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

class OrderForm(StatesGroup):
    choosing_delivery = State()
    full_name = State()
    phone = State()
    city = State()
    address = State()
    comment = State()

@dp.message(F.text == "/start")
async def start(message: Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
        [KeyboardButton(text="Каталог")],
        [KeyboardButton(text="Поиск по артикулу")],
        [KeyboardButton(text="Поддержка")],
        [KeyboardButton(text="Подписка на новинки")]
    ])
    await message.answer("Привет! Я помогу выбрать и заказать аккумуляторный инструмент 🔧", reply_markup=kb)

@dp.message(F.text == "Каталог")
async def show_catalog(message: Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="DEWALT DCD791B", callback_data="order_DCD791B")]
    ])
    await message.answer("Выберите товар:", reply_markup=markup)

@dp.callback_query(F.data.startswith("order_"))
async def order_product(callback: CallbackQuery, state: FSMContext):
    article = callback.data.split("_")[1]
    await state.update_data(article=article)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Самовывоз (Н.Новгород)", callback_data="pickup")],
        [InlineKeyboardButton(text="Доставка СДЭК", callback_data="cdek")]
    ])
    await callback.message.answer(f"Вы выбрали товар {article}. Как хотите получить заказ?", reply_markup=kb)
    await state.set_state(OrderForm.choosing_delivery)

@dp.callback_query(F.data == "pickup")
async def pickup_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await bot.send_message("@dewalt_nino", f"📦 Заявка на самовывоз\nАртикул: {data['article']}\nTelegram: @{callback.from_user.username}")
    await callback.message.answer("Заявка отправлена. Мы с вами свяжемся!")
    await state.clear()

@dp.callback_query(F.data == "cdek")
async def cdek_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ФИО полностью:")
    await state.set_state(OrderForm.full_name)

@dp.message(OrderForm.full_name)
async def get_full_name(message: Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(OrderForm.phone)

@dp.message(OrderForm.phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.answer("Город доставки:")
    await state.set_state(OrderForm.city)

@dp.message(OrderForm.city)
async def get_city(message: Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.answer("Адрес пункта выдачи СДЭК:")
    await state.set_state(OrderForm.address)

@dp.message(OrderForm.address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("Комментарий (необязательно):")
    await state.set_state(OrderForm.comment)

@dp.message(OrderForm.comment)
async def complete_order(message: Message, state: FSMContext):
    await state.update_data(comment=message.text)
    data = await state.get_data()
    text = (
        f"📦 Заявка на доставку СДЭК\n"
        f"Артикул: {data['article']}\n"
        f"ФИО: {data['full_name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Город: {data['city']}\n"
        f"ПВЗ: {data['address']}\n"
        f"Комментарий: {data['comment']}\n"
        f"Telegram: @{message.from_user.username}"
    )
    await bot.send_message("@dewalt_nino", text)
    await message.answer("Заявка принята, ожидайте связи ✉️")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())"
