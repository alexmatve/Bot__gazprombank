import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage

from Consultant import SalesGPT, llm

bot_token = '6680547488:AAGw_y0ncoSJf7UqFUvb36Yggg9PQI0BjNY'

sales_agent = None


async def main():
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    bot = Bot(bot_token, parse_mode=None)
    logging.basicConfig(level=logging.INFO)

    @dp.channel_post(Command(commands=["start"]))  # для группы
    async def repl(message):
        global sales_agent
        sales_agent = SalesGPT.from_llm(llm, verbose=False)
        sales_agent.seed_agent()
        #await message.answer('Генерируется ответ♻️')  # Даём понять пользователю, что бот работает (удалили, чтобы тестирующий бот не отвечал на данное сообщение)
        ai_message = sales_agent.ai_step()
        print(f"BOT: {ai_message}")
        #await message.answer(ai_message) # удаляем данную строчку, чтобы не создавалось конфликта между ботами в чате (чтобы не начинали переписываться по два сообщения). Если тестирующий бот не начинает сообщение первым после команды /start, то данную строчку нужно добавить
        #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)

    @dp.channel_post(F.text)  # для группы
    async def repl(message):
        if sales_agent is None:
            await message.answer('Используйте команду /start')
        else:
            human_message = message.text
            print(f"User: {message.text}") # Выводим в консоль сообщение пользователя (необязательная опция)
            if human_message:
                sales_agent.human_step(human_message)
                sales_agent.analyse_stage()
            #await message.answer('Генерируется ответ♻️') # Даём понять пользователю, что бот работает (удалили, чтобы тестирующий бот не отвечал на данное сообщение)
            ai_message = sales_agent.ai_step()
            print(f"BOT: {ai_message}") # Выводим в консоль сообщение бота (необязательная опция)
            await message.answer(ai_message)
            #await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id + 1)


    @dp.channel_post(~F.text)  # для группы
    async def empty(message):
        await message.answer('Бот принимает только текст')

    await bot.delete_webhook(drop_pending_updates=True)  # для группы
    await dp.start_polling(bot, allowed_updates=['channel_post'])  # для группы


if __name__ == "__main__":
    asyncio.run(main())
