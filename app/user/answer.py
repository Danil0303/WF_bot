from aiogram import Router, types, Bot


from app.db.method import  cancel_subscribe_db
from app.user.button import  start_command, info_command, buy_button

router_answer = Router()

@router_answer.callback_query(lambda c: c.data == 'info')
async def info(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(
            '✨ Мои супер-эффективные тренировки и секреты фигуры\n'
            '✨ Питание без запретов\n'
            '✨ Практики на женственность и сексуальность\n'
            '✨ Поддерживающее комьюнити\n'
            '✨ Новые темы каждый месяц\n'
            '✨ Приглашенные эксперты\n'
            '✨ Встречи онлайн и офлайн\n'
        ),
        reply_markup=info_command()
    )
    await callback_query.answer()


@router_answer.callback_query(lambda c: c.data == 'process')
async def process_info(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(
            '✨ Подписка на 30 дней\n'
            '✨ Полный доступ ко всему контенту\n'
            '✨ Можно отменить в любой момент\n'
            '✨ После отмены есть 5 дней для возврата без ограничений'
        ),
        reply_markup=buy_button()
    )
    await callback_query.answer()


@router_answer.callback_query(lambda c: c.data == 'not')
async def callback_cancel_subscription(callback_query: types.CallbackQuery, bot: Bot):
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=(f"{callback_query.message.from_user.first_name}, ты в боте закрытого женского клуба Вероники Литвинец «Wild Femme».\n"
                         "Это пространство для женщин, которые хотят:\n"
                         "✨ чувствовать своё тело\n"
                         '✨ быть в энергии и форме\n'
                         '✨ раскрывать женственность и сексуальность\n'
                         '✨ быть частью крутого комьюнити'),
        reply_markup=start_command())
    await callback_query.answer()

@router_answer.callback_query(lambda c: c.data=='yes')
async def cancel_subscription(callback_query: types.CallbackQuery, bot: Bot):
    data = await cancel_subscribe_db(callback_query.from_user.id)
    if data:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text='К сожалению, подписка отменена. У тебя есть 5 дней, чтобы вернуться без ограничений')
    else:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Упс, похоже, что-то пошло не так. Обратись за помощью сюда: @nika_litvinets")
    await callback_query.answer()