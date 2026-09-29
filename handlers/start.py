from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="🚗 Продать автомобиль",
        callback_data="create_ad"
    )

    builder.button(
        text="ℹ️ Как это работает",
        callback_data="how_it_works"
    )

    builder.adjust(1)

    await message.answer(
        "🚗 ДОСКА ОБЪЯВЛЕНИЙ АВТО\n\n"
        "Разместите объявление о продаже автомобиля "
        "и покажите его потенциальным покупателям.\n\n"
        "💰 Стоимость публикации — 100 ₽.\n"
        "📅 Срок размещения — 10 дней.",
        reply_markup=builder.as_markup()
    )


@router.callback_query(F.data == "how_it_works")
async def how_it_works_handler(callback: CallbackQuery):
    await callback.message.answer(
        "📋 Как это работает:\n\n"
        "1. Заполняете информацию об автомобиле.\n"
        "2. Добавляете фотографии.\n"
        "3. Проверяете объявление.\n"
        "4. Нажимаете «Оплатить 100 ₽».\n"
        "5. Сейчас используется тестовая заглушка оплаты.\n"
        "6. Объявление отправляется на модерацию.\n"
        "7. После одобрения публикуется в канале.\n"
        "8. Через 10 дней объявление снимается."
    )

    await callback.answer()