import functools
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import BotCommand, BotCommandScopeDefault

from app.db.base import create_tables
from app.db.method import get_user
from app.user.button import start_command, cancel_button_subscription
from app.user.answer import router_answer
from app.buy.yookassa import router_yookassa
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from config import SettingConfig
from loguru import logger
from app.scheduler_task.task import push_not_sub, push_sub
import asyncio

apscheduler_task = AsyncIOScheduler()

dp = Dispatcher()
dp.include_router(router_answer)
dp.include_router(router_yookassa)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! \n"
                         f"Ты в боте закрытого женского клуба Вероники Литвинец «Wild Femme».\n"
                         "Это пространство для женщин, которые хотят:\n"
                         "✨ чувствовать своё тело\n"
                         '✨ быть в энергии и форме\n'
                         '✨ раскрывать женственность и сексуальность\n'
                         '✨ быть частью крутого комьюнити', reply_markup=start_command())

@dp.message(Command('stop'))
async def stop(message: types.Message):
    res = await get_user(message.from_user.id)
    if res and res.subscribe:
        await message.answer(
            text="Точно хотите отменить подписку?", reply_markup=cancel_button_subscription())
    else:
        await message.answer(text=f"Упс, у вас нет подписки!")

@dp.message()
async def echo_handler(message: types.Message) -> None:
    try:
        await message.answer(f"Привет, {message.from_user.first_name}!\nВоспользуйся командами")
    except TypeError:
        await message.answer("Nice try!")

async def start_bot(bot: Bot):
    await set_commands(bot)
    await create_tables()
    apscheduler_task.add_job(push_not_sub, IntervalTrigger(days=1, start_date=datetime.now()+timedelta(minutes=1)), args=[bot])
    apscheduler_task.add_job(push_sub, IntervalTrigger(days=1, start_date=datetime.now()+timedelta(minutes=1)), args=[bot])
    apscheduler_task.start()
    logger.info("Бот запустился")

async def stop_bot():
    apscheduler_task.shutdown()
    logger.info("Бот отключен!")

async def set_commands(bot: Bot):
    commands = [BotCommand(command='start', description='Старт'),
                BotCommand(command='stop', description="Отмена подписки")]
    await bot.set_my_commands(commands, BotCommandScopeDefault())

async def main():
    bot = Bot(SettingConfig.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.startup.register(functools.partial(start_bot, bot))
    dp.shutdown.register(start_bot)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())