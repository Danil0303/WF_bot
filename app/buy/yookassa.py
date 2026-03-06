import asyncio
from datetime import datetime, timedelta
import re
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InputFile, FSInputFile
import pathlib
from app.user.button import payment_button, button_documents, start_command
from config import EmailReg
from app.model.errors import TimeOutPayments
from aioyookassa import YooKassa
from aioyookassa.types.payment import Money, Confirmation, Receipt, PaymentItem
from aioyookassa.types.enum import PaymentStatus, ConfirmationType, Currency, PaymentSubject, PaymentMode
from aioyookassa.types.params import CreatePaymentParams
from loguru import logger
from app.db.model import Subscribe
from app.db.method import add_user, get_user
from config import YooKasConfig
from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router_yookassa = Router()

class Form(StatesGroup):
    waiting_for_email = State()

def create_payment_method(user_id: int, email: str):
    return CreatePaymentParams(
        amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
        confirmation=Confirmation(
            type=ConfirmationType.REDIRECT,
            return_url=YooKasConfig.return_url_api
        ),
        description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
        metadata = {'user_id': user_id},
        capture=True,
        receipt=Receipt(
            items=[
                PaymentItem(description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
                            amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
                            quantity=1,
                            vat_code=11,
                            payment_subject=PaymentSubject.COMMODITY,
                            payment_mode=PaymentMode.FULL_PAYMENT
                            ),
            ],
            tax_system_code=1,
            internet=True,
            email=email


        ),
        save_payment_method=True
    )
def save_payment(user_id: int, save_id: str, email: str):
    return CreatePaymentParams(
        amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
        confirmation=Confirmation(
            type=ConfirmationType.REDIRECT,
            return_url=YooKasConfig.return_url_api
        ),
        description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
        metadata = {'user_id': user_id},
        capture=True,
        receipt=Receipt(
            items=[
                PaymentItem(description="Подписка 30 дней на закрытый клуб WildFemme - 2999p",
                            amount=Money(value=float(YooKasConfig.value_cur), currency=Currency.RUB),
                            quantity=1,
                            vat_code=11,
                            payment_subject=PaymentSubject.COMMODITY,
                            payment_mode=PaymentMode.FULL_PAYMENT
                            ),
            ],
            tax_system_code=1,
            internet=True,
            email=email
        ),
        payment_method_id=save_id
    )

async def auto_payment(user: Subscribe) -> bool:
    async with YooKassa(api_key=YooKasConfig.api_key, shop_id=int(YooKasConfig.shop_id)) as client:
        payment_response = save_payment(user_id=user.id_user, save_id=user.id_subscribe, email=user.email_str)
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
                await add_user(id_user=user.id_user, id_subscribe=str(payment_info.payment_method.id),
                               email=user.email_str)
                return True
            return False

@router_yookassa.callback_query(lambda c: c.data == 'buy')
async def buy_subscription(callback_query: types.CallbackQuery):
    is_block = await get_user(callback_query.from_user.id)
    if is_block and is_block.block:
        time_not_blocking = 30-(datetime.today()-is_block.data_end).days
        return await callback_query.message.answer("Ваш аккаунт заблокирован на 30 дней!\n "
                                                      f"Осталось еще {time_not_blocking} дней")
    document = InputFile("../../templates/documents/document.docx")
    await callback_query.message.answer_document(document=document, reply_markup=button_documents())

@router_yookassa.callback_query(lambda c: c.data == 'apply')
async def apply(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer("Пожалуйста, введите ваш email для чека:")
    await state.set_state(Form.waiting_for_email)

@router_yookassa.callback_query(lambda c: c.data == 'not_apply')
async def apply(callback_query: types.CallbackQuery):
    await callback_query.message.answer_photo(photo=FSInputFile(path=pathlib.Path('templates/images/IMG_4558.PNG')),
        caption=f"Привет, {callback_query.message.from_user.first_name}! \n\n"
                         f"Ты в боте закрытого женского клуба Вероники Литвинец «Wild Femme».\n\n"
                         "Это пространство для женщин, которые хотят:\n\n"
                         "❤️чувствовать и любить своё тело\n"
                         '✨быть в энергии и форме\n'
                         '\U0001FAE6 раскрывать женственность и сексуальность\n'
                         '\U0001FAC2 быть частью крутого, поддерживающего комьюнити', reply_markup=start_command()
                               )

@router_yookassa.message(Form.waiting_for_email)
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    if bool(re.match(EmailReg.EMAIL_REGEXP, email)):
        await state.update_data(user_email=email)
        await message.answer("Начинаем оформление подписки...")
        await asyncio.sleep(2)
        try:
            async with YooKassa(api_key=YooKasConfig.api_key, shop_id=int(YooKasConfig.shop_id)) as client:
                payment_response = create_payment_method(user_id=message.from_user.id, email=email)
                payment = await client.payments.create_payment(payment_response, )
                logger.success(f"✅ Платеж создан: {payment.id}")
                await message.answer(text=f"Оплата подписки 30 дней на закрытый клуб «WildFemme»👇🏻\n\n"
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
                        await add_user(id_user=message.from_user.id,
                                       id_subscribe=str(payment_info.payment_method.id),
                                       email=email)
                        return await message.answer(
                            text=f"Поздравляю, оплата прошла успешно!✅\n\n"
                                 "Добро пожаловать в закрытый женский клуб Вероники Литвинец «Wild Femme»!\n\n"
                                 f"Ссылка для входа👉🏻 {YooKasConfig.link}\n\n"
                                 "Доступ активен 30 дней с момента оплаты."
                        )
                    await message.answer(text="Оплата не прошла!")
                except TimeOutPayments as exp:
                    logger.error(exp)
                    await message.answer(text="Оплата не прошла!")
        except Exception as e:
            logger.error(e)
            await message.answer( "Упс, похоже, что-то пошло не так. Обратись за помощью сюда: @nika_litvinets")
        finally:
            await state.clear()
    else:
        await message.answer("Некорректный email!\n/start")

