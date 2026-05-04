from aiogram import Router, types, Bot


from app.db.method import  cancel_subscribe_db
from app.user.button import  start_command, info_command, buy_button

router_answer = Router()

@router_answer.callback_query(lambda c: c.data == 'info')
async def info(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(
            "<b>Внутри клуба тебя ждут:</b>\n\n"
            '✅ Мои супер-эффективные тренировки и секреты фигуры\n\n'
            '✅ Уроки по питанию без запретов\n\n'
            '✅ Бьюти-находки и секреты красоты\n\n'
            '✅ Уроки по продажам в соцсетях\n\n'
            '✅ Поддерживающее комьюнити\n\n'
            '💎 А также - новая тема в клубе каждый месяц \n\n'
            'Готова вступить в клуб и расти во всех сферах лично со мной?😍\n'
        ),
        reply_markup=info_command()
    )
    await callback_query.answer()


@router_answer.callback_query(lambda c: c.data == 'process')
async def process_info(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(
            f"<b>Как все происходит?</b>\n\n"
            '✨ Подписка на 30 дней\n'
            '✨ Полный доступ ко всему контенту\n'
            '✨ Можно отменить в любой момент\n'
            '✨ После отмены есть 5 дней для возврата без ограничений\n\n'
            '✅ Каждый месяц планирую приглашать экспертов из разных актуальных сфер (косметологи, визажисты, эксперты по ИИ)\n\n'
            '✅ Встречи онлайн и офлайн (разборы, девичники, общение)\n\n'
            '✅ Обратная связь и поддержка лично от меня в общем чате на протяжении всей подписки\n\n'
            'Очень жду именно тебя в своем крутом комьюнити «WildFemme»!\n\n'
            'Присоединяйся🐾'
        ),
        reply_markup=buy_button()
    )
    await callback_query.answer()


@router_answer.callback_query(lambda c: c.data == 'not')
async def callback_cancel_subscription(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(f"{callback_query.message.from_user.first_name}, ты в боте закрытого женского клуба Вероники Литвинец «Wild Femme».\n"
                          "Это пространство для женщин, которые хотят:\n\n"
                         "❤️чувствовать и любить своё тело\n"
                         '✨быть в энергии и форме\n'
                         '\U0001FAE6 раскрывать женственность и сексуальность\n'
                         '\U0001FAC2 быть частью крутого, поддерживающего комьюнити'),
        reply_markup=start_command())
    await callback_query.answer()

@router_answer.callback_query(lambda c: c.data=='yes')
async def cancel_subscription(callback_query: types.CallbackQuery, bot: Bot):
    data = await cancel_subscribe_db(callback_query.from_user.id)
    if data:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text='К сожалению, подписка отменена🥺 У тебя есть 5 дней, чтобы вернуться без ограничений.')
        await bot.send_message(chat_id=1027526485,
                               text=f"Пользователь: {callback_query.message.chat.username} отменил подписку!")
    else:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Упс, похоже, что-то пошло не так. Обратись за помощью сюда: @nika_litvinets")
    await callback_query.answer()