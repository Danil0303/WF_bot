from datetime import datetime
from aiogram import Bot
from loguru import logger

from app.buy.yookassa import auto_payment
from config import SettingConfig
from app.db.method import get_users_subscribe, blocking, cancel_subscribe_db
from app.user.button import buy_button


async def push_not_sub(bot: Bot):
    users = await get_users_subscribe(subscribe=False)
    logger.success('Рассылка для пользователей без подписки запущена')
    if users:
        logger.info(f'Обнаружено {len(users)} без подписки')
        for user in users:
            try:
                del_time = (datetime.today()-user.data_end).days
                if del_time == 1:
                    await bot.send_message(chat_id=user.id_user, text='Если передумаешь — можешь вернуться прямо сейчас.')
                elif del_time == 3:
                    await bot.send_message(chat_id=user.id_user, text='Через 2 дня доступ будет временно закрыт.')
                elif del_time == 5:
                    await bot.send_message(chat_id=user.id_user, text='Сегодня последний день для возврата без ожидания')
                elif del_time == 6:
                    await blocking(id_user=user.id_user, block=True)
                    await bot.ban_chat_member(user_id=user.id_user, chat_id=str(SettingConfig.channel_id))
                    await bot.send_message(chat_id=user.id_user, text='Доступ временно закрыт. Повторное вступление будет доступно через 30 дней.')
                elif del_time == 30:
                    await blocking(id_user=user.id_user, block=False)
                    await bot.unban_chat_member(user_id=user.id_user, chat_id=str(SettingConfig.channel_id))
                    await bot.send_message(chat_id=user.id_user, text='Доступ снова открыт. Ты можешь снова вступить в клуб', reply_markup=buy_button())
            except Exception as exp:
                logger.error(f"{exp}->{user.id_user}")
                continue

async def push_sub(bot: Bot):
    users = await get_users_subscribe(subscribe=True)
    logger.success('Рассылка для пользователей с подпиской запущена')
    if users:
        logger.info(f'Обнаружено {len(users)} с подпиской')
        for user in users:
            try:
                del_time = (datetime.today()-user.data_start).days
                if del_time == 27:
                    await bot.send_message(chat_id=user.id_user, text='Твоя подписка заканчивается через 3 дня.\nЧтобы не терять доступ — убедись, что подписка активна.')
                elif del_time == 30:
                    result = await auto_payment(user)
                    if result:
                        return await bot.send_message(chat_id=user.id_user, text='Подписка продлена!')
                    await cancel_subscribe_db(id_user=user.id_user)
                    await bot.send_message(chat_id=user.id_user, text='Подписка не продлена!')
            except Exception as exp:
                logger.error(f"{exp}->{user.id_user}")
                continue


