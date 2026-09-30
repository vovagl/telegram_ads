import json

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import ADMIN_ID, YOOKASSA_PROVIDER_TOKEN

from database import (
    create_ad,
    update_ad,
    get_ad,
    mark_paid,
)


router = Router()


class AdForm(StatesGroup):
    brand = State()
    model = State()
    year = State()
    mileage = State()
    gearbox = State()
    engine = State()
    price = State()
    city = State()
    description = State()
    contact = State()
    photos = State()


@router.callback_query(F.data == "create_ad")
async def create_ad_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    ad_id = create_ad(callback.from_user.id)

    await state.update_data(
        ad_id=ad_id,
        photos=[]
    )

    await state.set_state(AdForm.brand)

    await callback.message.answer(
        f"🚗 Объявление №{ad_id}\n\n"
        "Введите марку автомобиля.\n\n"
        "Например: BMW"
    )

    await callback.answer()


@router.message(AdForm.brand)
async def brand_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        brand=message.text
    )

    await message.answer(
        "Введите модель автомобиля.\n\n"
        "Например: X5"
    )

    await state.set_state(AdForm.model)


@router.message(AdForm.model)
async def model_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        model=message.text
    )

    await message.answer(
        "Введите год выпуска.\n\n"
        "Например: 2020"
    )

    await state.set_state(AdForm.year)


@router.message(AdForm.year)
async def year_handler(
    message: Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "❌ Введите год цифрами.\n\n"
            "Например: 2020"
        )
        return

    year = int(message.text)

    if year < 1950 or year > 2030:
        await message.answer(
            "❌ Укажите реальный год выпуска."
        )
        return

    await state.update_data(
        year=year
    )

    await message.answer(
        "Введите пробег в километрах.\n\n"
        "Например: 85000"
    )

    await state.set_state(AdForm.mileage)


@router.message(AdForm.mileage)
async def mileage_handler(
    message: Message,
    state: FSMContext
):
    if not message.text.isdigit():
        await message.answer(
            "❌ Введите пробег цифрами.\n\n"
            "Например: 85000"
        )
        return

    await state.update_data(
        mileage=int(message.text)
    )

    await message.answer(
        "Какая коробка передач?\n\n"
        "Например: автомат"
    )

    await state.set_state(AdForm.gearbox)


@router.message(AdForm.gearbox)
async def gearbox_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        gearbox=message.text
    )

    await message.answer(
        "Какой двигатель?\n\n"
        "Например: бензин 2.0"
    )

    await state.set_state(AdForm.engine)


@router.message(AdForm.engine)
async def engine_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        engine=message.text
    )

    await message.answer(
        "Укажите цену автомобиля.\n\n"
        "Например: 15000 €"
    )

    await state.set_state(AdForm.price)


@router.message(AdForm.price)
async def price_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        price=message.text
    )

    await message.answer(
        "В каком городе находится автомобиль?\n\n"
        "Например: Рига"
    )

    await state.set_state(AdForm.city)


@router.message(AdForm.city)
async def city_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        city=message.text
    )

    await message.answer(
        "Напишите описание автомобиля.\n\n"
        "Расскажите о состоянии, комплектации, "
        "обслуживании и других важных деталях."
    )

    await state.set_state(AdForm.description)


@router.message(AdForm.description)
async def description_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        description=message.text
    )

    await message.answer(
        "Укажите контактный телефон."
    )

    await state.set_state(AdForm.contact)


@router.message(AdForm.contact)
async def contact_handler(
    message: Message,
    state: FSMContext
):
    await state.update_data(
        contact=message.text
    )

    await message.answer(
        "📸 Теперь отправьте фотографии автомобиля.\n\n"
        "Можно отправить до 10 фотографий.\n"
        "После загрузки нажмите «Готово»."
    )

    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Готово",
        callback_data="photos_done"
    )

    await message.answer(
        "Когда закончите загрузку фотографий:",
        reply_markup=builder.as_markup()
    )

    await state.set_state(AdForm.photos)


@router.message(AdForm.photos, F.photo)
async def photo_handler(
    message: Message,
    state: FSMContext
):
    data = await state.get_data()

    photos = data.get("photos", [])

    if len(photos) >= 10:
        await message.answer(
            "⚠️ Максимум 10 фотографий.\n"
            "Нажмите «Готово»."
        )
        return

    photo_id = message.photo[-1].file_id

    photos.append(photo_id)

    await state.update_data(
        photos=photos
    )

    await message.answer(
        f"📸 Фото добавлено.\n"
        f"Загружено: {len(photos)}/10"
    )


@router.message(AdForm.photos)
async def wrong_photo_handler(
    message: Message
):
    await message.answer(
        "📸 Отправьте именно фотографию автомобиля "
        "или нажмите «Готово»."
    )


@router.callback_query(
    AdForm.photos,
    F.data == "photos_done"
)
async def photos_done_handler(
    callback: CallbackQuery,
    state: FSMContext
):
    data = await state.get_data()

    photos = data.get("photos", [])

    if not photos:
        await callback.answer(
            "Добавьте хотя бы одну фотографию.",
            show_alert=True
        )
        return

    ad_id = data["ad_id"]

    fields = {
        "brand": data["brand"],
        "model": data["model"],
        "year": data["year"],
        "mileage": data["mileage"],
        "gearbox": data["gearbox"],
        "engine": data["engine"],
        "price": data["price"],
        "city": data["city"],
        "description": data["description"],
        "contact": data["contact"],
        "photo_id": json.dumps(photos),
    }

    for field, value in fields.items():
        update_ad(ad_id, field, value)

    ad = get_ad(ad_id)

    preview = (
        f"🚗 ПРЕДПРОСМОТР ОБЪЯВЛЕНИЯ №{ad['id']}\n\n"
        f"Марка: {ad['brand']}\n"
        f"Модель: {ad['model']}\n"
        f"Год: {ad['year']}\n"
        f"Пробег: {ad['mileage']} км\n"
        f"Коробка: {ad['gearbox']}\n"
        f"Двигатель: {ad['engine']}\n"
        f"Цена: {ad['price']}\n"
        f"Город: {ad['city']}\n\n"
        f"Описание:\n{ad['description']}\n\n"
        f"☎️ Контакт: {ad['contact']}\n\n"
        f"📸 Фотографий: {len(photos)}\n\n"
        "💰 Стоимость публикации: 100 ₽\n"
        "📅 Срок размещения: 10 дней"
    )

    builder = InlineKeyboardBuilder()

    builder.button(
        text="💰 Оплатить 100 ₽",
        callback_data=f"pay_{ad_id}"
    )

    builder.button(
        text="✏️ Изменить",
        callback_data=f"edit_{ad_id}"
    )

    builder.adjust(1)

    await callback.message.answer(
        preview,
        reply_markup=builder.as_markup()
    )

    await state.clear()
    await callback.answer()


# ==========================================================
# ОПЛАТА ЧЕРЕЗ TELEGRAM PAYMENTS / ЮKASSA
# ==========================================================

@router.callback_query(F.data.startswith("pay_"))
async def payment_handler(
    callback: CallbackQuery
):
    ad_id = int(
        callback.data.split("_")[1]
    )

    ad = get_ad(ad_id)

    if not ad:
        await callback.answer(
            "Объявление не найдено.",
            show_alert=True
        )
        return

    if ad["paid"]:
        await callback.answer(
            "Это объявление уже оплачено.",
            show_alert=True
        )
        return

    if not YOOKASSA_PROVIDER_TOKEN:
        await callback.answer(
            "Оплата пока не настроена.",
            show_alert=True
        )
        return

    await callback.message.answer_invoice(
        title="Публикация объявления",
        description=(
            f"Публикация объявления №{ad_id} "
            f"на 10 дней"
        ),
        payload=f"ad_{ad_id}",
        provider_token=YOOKASSA_PROVIDER_TOKEN,
        currency="RUB",
        prices=[
            LabeledPrice(
                label="Публикация объявления",
                amount=10000
            )
        ],
        need_phone_number=True,
        send_phone_number_to_provider=True
    )

    await callback.answer()


# ==========================================================
# ПОДТВЕРЖДЕНИЕ ПЛАТЕЖА
# ==========================================================

@router.pre_checkout_query()
async def process_pre_checkout(
    pre_checkout_query: PreCheckoutQuery
):
    await pre_checkout_query.answer(
        ok=True
    )


# ==========================================================
# УСПЕШНАЯ ОПЛАТА
# ==========================================================

@router.message(F.successful_payment)
async def successful_payment_handler(
    message: Message,
    bot: Bot
):
    payment = message.successful_payment

    payload = payment.invoice_payload

    if not payload.startswith("ad_"):
        return

    ad_id = int(
        payload.split("_")[1]
    )

    ad = get_ad(ad_id)

    if not ad:
        await message.answer(
            "Платёж получен, но объявление не найдено.\n"
            "Обратитесь к администратору."
        )
        return

    if ad["paid"]:
        await message.answer(
            "Платёж уже был обработан."
        )
        return

    payment_id = (
        payment.provider_payment_charge_id
    )

    mark_paid(
        ad_id,
        payment_id
    )

    ad = get_ad(ad_id)

    moderation_text = (
        f"🛡 НОВОЕ ОБЪЯВЛЕНИЕ НА МОДЕРАЦИЮ\n\n"
        f"№ {ad['id']}\n\n"
        f"🚗 {ad['brand']} {ad['model']}\n"
        f"📅 Год: {ad['year']}\n"
        f"🛣 Пробег: {ad['mileage']} км\n"
        f"⚙️ Коробка: {ad['gearbox']}\n"
        f"🔧 Двигатель: {ad['engine']}\n"
        f"💰 Цена: {ad['price']}\n"
        f"📍 Город: {ad['city']}\n\n"
        f"📝 Описание:\n"
        f"{ad['description']}\n\n"
        f"☎️ Контакт: {ad['contact']}\n\n"
        f"💳 Оплата: 100 ₽\n"
        f"✅ Платёж подтверждён"
    )

    builder = InlineKeyboardBuilder()

    builder.button(
        text="✅ Опубликовать",
        callback_data=f"approve_{ad_id}"
    )

    builder.button(
        text="❌ Отклонить",
        callback_data=f"reject_{ad_id}"
    )

    builder.adjust(2)

    if ADMIN_ID:
        await bot.send_message(
            ADMIN_ID,
            moderation_text,
            reply_markup=builder.as_markup()
        )

        photos = json.loads(
            ad["photo_id"]
        )

        for photo_id in photos:
            await bot.send_photo(
                ADMIN_ID,
                photo_id
            )

    await message.answer(
        f"✅ Оплата успешно получена!\n\n"
        f"Объявление №{ad_id} отправлено "
        f"на модерацию.\n\n"
        "После проверки оно будет опубликовано."
    )


# ==========================================================
# МОДЕРАЦИЯ — ОДОБРИТЬ
# ==========================================================

@router.callback_query(
    F.data.startswith("approve_")
)
async def approve_ad_handler(
    callback: CallbackQuery
):
    ad_id = int(
        callback.data.split("_")[1]
    )

    ad = get_ad(ad_id)

    if not ad:
        await callback.answer(
            "Объявление не найдено.",
            show_alert=True
        )
        return

    if ad["status"] != "moderation":
        await callback.answer(
            "Это объявление уже обработано.",
            show_alert=True
        )
        return

    update_ad(
        ad_id,
        "status",
        "approved"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        f"✅ Объявление №{ad_id} одобрено.\n\n"
        "Статус: approved\n\n"
        "Следующий этап — публикация "
        "в Telegram-канале."
    )

    await callback.answer(
        "Объявление одобрено."
    )


# ==========================================================
# МОДЕРАЦИЯ — ОТКЛОНИТЬ
# ==========================================================

@router.callback_query(
    F.data.startswith("reject_")
)
async def reject_ad_handler(
    callback: CallbackQuery
):
    ad_id = int(
        callback.data.split("_")[1]
    )

    ad = get_ad(ad_id)

    if not ad:
        await callback.answer(
            "Объявление не найдено.",
            show_alert=True
        )
        return

    if ad["status"] != "moderation":
        await callback.answer(
            "Это объявление уже обработано.",
            show_alert=True
        )
        return

    update_ad(
        ad_id,
        "status",
        "rejected"
    )

    await callback.message.edit_reply_markup(
        reply_markup=None
    )

    await callback.message.answer(
        f"❌ Объявление №{ad_id} отклонено.\n\n"
        "Статус: rejected"
    )

    await callback.answer(
        "Объявление отклонено."
    )