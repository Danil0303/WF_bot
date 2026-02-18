import asyncio
from datetime import datetime, timedelta
from app.model.errors import TimeOutPayments
from aioyookassa import YooKassa
from aioyookassa.types.payment import Money, Confirmation
from aioyookassa.types.enum import PaymentStatus, ConfirmationType, Currency
from aioyookassa.types.params import CreatePaymentParams
from loguru import logger
from app.db.model import Subscribe
from app.db.method import add_user, get_user
from app.user.button import payment_button
from config import YooKasConfig
from aiogram import Router, types, Bot
from aiogram.fsm.context import FSMContext

router_yookassa = Router()

def create_payment(user_id: int):
    return CreatePaymentParams(
        amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
        confirmation=Confirmation(
            type=ConfirmationType.REDIRECT,
            return_url=YooKasConfig.return_url_api
        ),
        description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
        metadata = {'user_id': user_id},
        capture=True,
        save_payment_method=True
    )
def save_payment(user_id: int, save_id: str):
    return CreatePaymentParams(
        amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
        confirmation=Confirmation(
            type=ConfirmationType.REDIRECT,
            return_url=YooKasConfig.return_url_api
        ),
        description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
        metadata = {'user_id': user_id},
        capture=True,
        payment_method_id=save_id
    )

async def auto_payment(user: Subscribe) -> bool:
    async with YooKassa(api_key=YooKasConfig.api_key, shop_id=int(YooKasConfig.shop_id)) as client:
        payment_response = save_payment(user_id=user.id_user, save_id=user.id_subscribe)
        payment = await client.payments.create_payment(payment_response)
        start_time = datetime.now()
        timeout = timedelta(minutes=int(YooKasConfig.time_delta))
        payment_info = await client.payments.get_payment(payment.id)
        try:
            while payment_info.status == PaymentStatus.PENDING:
                current_time = datetime.now()
                elapsed_time = current_time - start_time
                payment_info = await client.payments.get_payment(payment.id)
                if elapsed_time > timeout:
                    raise TimeOutPayments('Вышло время оплаты подписки')
                if payment_info.status.lower() != PaymentStatus.PENDING:
                    break
                await asyncio.sleep(10)
        except TimeOutPayments as exp:
            logger.error(exp)
            return False
        else:
            logger.info(f"📊 Статус платежа: {payment_info.status}")
            if payment_info.status == PaymentStatus.SUCCEEDED:
                logger.success("Платеж подтвержден")
                await add_user(id_user=user.id_user, id_subscribe=str(payment_info.payment_method.id))
                return True
            return False

@router_yookassa.callback_query(lambda c: c.data == 'buy')
async def buy_subscription(callback_query: types.CallbackQuery, bot: Bot, state: FSMContext):
    is_block = await get_user(callback_query.from_user.id)
    if is_block and is_block.block:
        time_not_blocking = 30-(datetime.today()-is_block.data_end).days
        return await callback_query.message.answer("Ваш аккаунт заблокирован на 30 дней!\n "
                                                      f"Осталось еще {time_not_blocking} дней")
    await callback_query.message.answer("Начинаем оформление подписки...")
    await asyncio.sleep(2)
    try:
        async with YooKassa(api_key=YooKasConfig.api_key, shop_id=int(YooKasConfig.shop_id)) as client:
            payment_response = create_payment(user_id=callback_query.from_user.id)
            payment = await client.payments.create_payment(payment_response)
            logger.success(f"✅ Платеж создан: {payment.id}")
            await callback_query.message.answer(text=f"Оплаты подписки 30 дней на закрытый клуб WildFemme\n"
                                                    f"Цена подписки - 2999p\n",
                                                reply_markup=payment_button(payment.confirmation.url))
            # await callback_query.message.answer(f"Ссылка для оплаты подписки 30 дней на закрытый клуб WildFemme\n"
            #                                        f"Цена подписки - 2999p\n"
            #                                        f"Ссылка на оплату:\n {payment.confirmation.url}")
            start_time = datetime.now()
            timeout = timedelta(minutes=int(YooKasConfig.time_delta))
            payment_info = await client.payments.get_payment(payment.id)
            try:
                while payment_info.status == PaymentStatus.PENDING:
                    current_time = datetime.now()
                    elapsed_time = current_time - start_time
                    payment_info = await client.payments.get_payment(payment.id)
                    if elapsed_time > timeout:
                        raise TimeOutPayments('Вышло время оплаты подписки')
                    if payment_info.status.lower() != PaymentStatus.PENDING:
                        break
                    await asyncio.sleep(10)
                logger.info(f"📊 Статус платежа: {payment_info.status}")
                if payment_info.status == PaymentStatus.SUCCEEDED:
                    logger.success("Платеж подтвержден")
                    await add_user(id_user=callback_query.from_user.id, id_subscribe=str(payment_info.payment_method.id))
                    return await callback_query.message.answer(
                        text=f"Поздравляю, оплата прошла успешно!✅\n\n"
                             "Добро пожаловать в закрытый женский клуб Вероники Литвинец «Wild Femme»!\n\n"
                            f"Ссылка для входа👉🏻 {YooKasConfig.link}\n\n"
                             "Доступ активен 30 дней с момента оплаты."
                        )
                await callback_query.message.answer(text="Оплата не прошла!")
            except TimeOutPayments as exp:
                logger.error(exp)
                await callback_query.message.answer(text="Оплата не прошла!")
    except Exception as e:
        logger.error(e)
        await bot.send_message(callback_query.from_user.id, "Упс, похоже, что-то пошло не так. Обратись за помощью сюда: @nika_litvinets")
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()