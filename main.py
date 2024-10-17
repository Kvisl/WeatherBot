import os
from dotenv import load_dotenv
import asyncio
import datetime
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
import logging


logging.basicConfig(level=logging.INFO, format=f'{datetime.datetime.now():%Y-%m-%d %H:%M:%S} - %(levelname)s - %(message)s')


load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
open_weather_token = os.getenv('OPEN_WEATHER_TOKEN')

bot = Bot(token=bot_token)
dp = Dispatcher()
router = Router()


@router.message(CommandStart())
async def start_message(message: Message):
    await message.answer('\U0001F324\U0001F329\U00002744Привет! Я бот прогноза погоды\n'
                         'Сообщите мне название города, и я расскажу вам о погоде в данный момент!')


@router.message()
async def get_weather(message: Message):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                f'https://api.openweathermap.org/data/2.5/weather?q={message.text}'
                    f'&appid={open_weather_token}&units=metric', timeout=10) as response:

                data = await response.json()


                if response.status == 200:
                    city = data['name']
                    current_temp = int(data['main']['temp'])
                    humidity = data['main']['humidity']
                    pressure = data['main']['pressure']
                    wind_speed = int(data['wind']['speed'])
                    weather_description = data['weather'][0]['main']


                    weather_icons = {
                        'Clear': 'Ясно \u2600',
                        'Clouds': 'Облачно \u2601',
                        'Rain': 'Дождь \U0001F327',
                        'Drizzle': 'Mоросящий дождь \u2614',
                        'Thunderstorm': 'Гроза \u26A1',
                        'Snow': 'Снег \u2744',
                        'Mist': 'Туман \U0001F32B'
                     }


                    if weather_description in weather_icons:
                        emoji = weather_icons.get(weather_description, '\U0001F32A')


                    await message.reply(
                        f'\U0001F553{datetime.datetime.now().strftime("%d-%m-%Y | %H:%M:%S")}\n'
                        f'\U0001F3D9Погода в городе {city}:\n'
                        f'\U00002705Сейчас - {emoji}\n'
                        f'\U0001F321Температура: {current_temp}°C.\n'
                        f'\U0001F32CСкорость ветра: {wind_speed} м/с.\n'
                        f'\U0001F4A7Влажность: {humidity}%.\n'
                        f' \U000021C5Давление: {pressure} мм. рт. ст.'
                    )


                else:
                    error_message = data.get('message', 'Ошибка при получении данных')
                    await message.reply(f'Ошибка: {error_message}')


        except Exception as e:
            logging.error(f'Ошибка при получении данных о погоде: {repr(e)}')
            logging.exception(f'Полная информация об ошибке:')
            await message.reply(f'Не удалось получить данные о погоде. Ошибка: {repr(e)}')



async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    print('Бот запущен!')
    asyncio.run(main())