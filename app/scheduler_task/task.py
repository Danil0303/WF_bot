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
                    await bot.send_message(chat_id=1027526485,
                                           text=f"Пользователь: {user.email_str} заблокирован на 30 дней!")
                elif del_time == 30:
                    await blocking(id_user=user.id_user, block=False)
                    await bot.unban_chat_member(user_id=user.id_user, chat_id=str(SettingConfig.channel_id))
                    await bot.send_message(chat_id=user.id_user, text='Доступ снова открыт. Ты можешь снова вступить в клуб', reply_markup=buy_button())
                    await bot.send_message(chat_id=1027526485,
                                           text=f"Пользователь: {user.email_str} разблокирован!")
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
                logger.info(f"{user.id_user}-{del_time}-{user.email_str}")
                if del_time == 27:
                    await bot.send_message(chat_id=user.id_user, text='Твоя подписка заканчивается через 3 дня.\nЧтобы не терять доступ — убедись, что подписка активна.')
                elif del_time == 29:
                    await bot.send_message(chat_id=1027526485,
                                           text=f"Завтра списание у пользователя: {user.email_str}!")
                elif del_time in [30, 31, 32]:
                    result = await auto_payment(user)
                    if result:
                        await bot.send_message(chat_id=user.id_user, text='Подписка продлена!')
                        await bot.send_message(chat_id=1027526485, text=f"Пользователь: {user.email_str} оплатил подписку!")
                        continue
                    if del_time == 32 and not result:
                        await cancel_subscribe_db(id_user=user.id_user)
                        await bot.send_message(chat_id=user.id_user, text='Подписка не продлена!')
                        await bot.send_message(chat_id=1027526485,
                                               text=f"У пользователя: {user.email_str} отменена подписка!")
                        continue
                    await bot.send_message(chat_id=user.id_user, text='Упс, оплата не прошла. Повторное списание через 24 часа, проверьте, пожалуйста, баланс привязанной карты и наличие подписки')
                    await bot.send_message(chat_id=1027526485, text=f"У пользователь: {user.email_str} оплата не прошла!")
            except Exception as exp:
                logger.error(f"{exp}->{user.id_user}")
                continue

async def push_pay_user(bot: Bot):
    data_start = datetime(2026, 8, 12)
    list_user_push = [8482438571,
                      8000269592,
                      740729335,
                      459697699,
                      452355791,
                      5176330355,
                      1008629775,
                      1662872523,
                      6894692838,
                      406019270,
                      845017491,
                      1051057562]
    days_data = (datetime.today()-data_start).days
    users = await get_users_subscribe(subscribe=True)
    users_list_db = [i.id_user for i in users]
    logger.info("Временная задача запущена!")
    for user_in_list in list_user_push:
        try:
            if user_in_list in users_list_db:
                logger.info(f'Пользователь: {user_in_list} оплатил!')
                continue
            logger.info(f'Пользователь: {user_in_list} не оплатил!')
            if days_data == 0:
                await bot.send_message(user_in_list, """
            Привет!❤️ На связи Вероника - создатель клуба.\n
            Ура, технические неполадки с ботом устранены, теперь мы можем в полной мере продолжить заниматься и смотреть все уроки🥳\n
            Для этого необходимо самостоятельно заново оплатить подписку также, как и при входе в клуб. Жду тебя в канале!❤️
                """, reply_markup=buy_button())
            elif days_data == 1:
                await bot.send_message(user_in_list,
                                       text="""
                                        Привет!❤️ Напоминаю, чтобы остаться в клубе и не терять доступ ко всем материалам, необходимо оплатить подписку на клуб самостоятельно через кнопку👇🏻 
                                       """,
                                       reply_markup=buy_button())
            elif days_data == 2:
                await bot.send_message(user_in_list,
                                       text="""
                                        Привет!🥺❤️ Сегодня крайний день оплаты подписки, очень жду тебя. Оставайся с нами и приходи в форму с моей поддержкой👇🏻🔥
                                       """,
                                       reply_markup=buy_button())
            elif days_data == 3:
                await bot.ban_chat_member(user_id=user_in_list, chat_id=str(SettingConfig.channel_id))
                await bot.send_message(chat_id=user_in_list,
                                       text='Доступ временно закрыт. Повторное вступление будет доступно через 30 дней.')
                await bot.send_message(chat_id=1027526485,
                                       text=f"Пользователь: {user_in_list} заблокирован на 30 дней!")




        except Exception as e:
            logger.error(f"{e}->{user_in_list}")
            continue




