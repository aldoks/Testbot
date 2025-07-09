
import logging
import json
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

with open("questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

user_data = {}

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"score": 0, "index": 0}
    await send_question(message.chat.id, user_id)

async def send_question(chat_id, user_id):
    idx = user_data[user_id]["index"]
    if idx >= len(questions):
        score = user_data[user_id]["score"]
        total = len(questions)
        percent = round(score / total * 100, 2)
        await bot.send_message(chat_id, f"✅ Test yakunlandi!\nNatijangiz: {score}/{total} ({percent}%)")
        return

    q = questions[idx]
    markup = InlineKeyboardMarkup()
    for i, ans in enumerate(q["answers"]):
        markup.add(InlineKeyboardButton(ans, callback_data=str(i)))
    await bot.send_message(chat_id, f"❓ {q['question']}", reply_markup=markup)

@dp.callback_query_handler()
async def answer_handler(call: types.CallbackQuery):
    user_id = call.from_user.id
    idx = user_data[user_id]["index"]
    correct = questions[idx]["correct"]
    chosen = int(call.data)
    if chosen == correct:
        user_data[user_id]["score"] += 1
        await call.message.answer("✅ To‘g‘ri javob!")
    else:
        await call.message.answer(f"❌ Noto‘g‘ri. To‘g‘ri javob: {questions[idx]['answers'][correct]}")
    user_data[user_id]["index"] += 1
    await send_question(call.message.chat.id, user_id)
    await call.answer()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
