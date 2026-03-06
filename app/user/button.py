from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def cancel_button_subscription()->InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да 😭", callback_data='yes'),
         InlineKeyboardButton(text='Нет ☺️', callback_data='not')]

    ])
def start_command()-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Что внутри клуба?', callback_data='info'),
         InlineKeyboardButton(text='Вступить в клуб', callback_data='buy')]
    ])
def info_command()-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Как все происходит?', callback_data='process'),
         InlineKeyboardButton(text='Вступить в клуб', callback_data='buy')]
    ])

def buy_button()-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вступить в клуб', callback_data='buy')]
    ])

def payment_button(url: str)-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Оплатить подписку",
                              url=url)]
    ])

def button_documents()-> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Да', callback_data='apply'),
         InlineKeyboardButton(text="Нет", callback_data="not_apply")]
    ])