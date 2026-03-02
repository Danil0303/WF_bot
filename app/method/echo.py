from aiogram import F, types,Router
from config import EmailReg
echo_router = Router()



@echo_router.message(~F.regexp(EmailReg.EMAIL_REGEXP))
async def echo_handler(message: types.Message) -> None:
    try:
        await message.answer(f"Привет, {message.from_user.first_name}!\nВоспользуйся командами")
    except TypeError:
        await message.answer("Nice try!")