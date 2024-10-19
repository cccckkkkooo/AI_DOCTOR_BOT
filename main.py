import telebot
from telebot import types
from g4f.client import Client

TOKEN = '7817694585:AAH-_iVN4J5VVhNpr1_P1WA2l4gW4YzkVg4'
bot = telebot.TeleBot(TOKEN)

client = Client()
topic = "Пожалуйста, предложите возможные решения и советы, основываясь на жалобах пользователя."

user_states = {}
user_dialogs = {}

questions = {
    1: "Можете рассказать, что вас беспокоит?",
    2: "Как долго у вас наблюдаются эти симптомы?"
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    help_button = types.KeyboardButton('Help')
    sos_button = types.KeyboardButton('SOS')
    markup.add(help_button, sos_button)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Привет!\nЯ помощник с вопросами о здоровье, внедренный командой GPT WARRIORS.\nЕсли ты чувствуешь себя плохо, нажми Help", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == 'Help')
def handle_help(message):
    chat_id = message.chat.id
    user_states[chat_id] = 1
    user_dialogs[chat_id] = []
    bot.send_message(chat_id, questions[1])

@bot.message_handler(func=lambda message: message.text == 'SOS')
def handle_sos(message):
    chat_id = message.chat.id
    sos_message = (
        "Экстренные службы:\n"
        "📞 Полиция: 102\n"
        "📞 Скорая помощь: 103\n"
        "📞 Пожарная служба: 101\n"
        "📞 Единый номер экстренной службы: 112\n"
    )
    bot.send_message(chat_id, sos_message)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id

    if chat_id in user_states and user_states[chat_id] <= len(questions):
        stage = user_states[chat_id]

        user_dialogs[chat_id].append(message.text)

        if stage == 2:
            user_input = " ".join(user_dialogs[chat_id])
            full_message = f"{topic} {user_input}"

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": full_message}]
            )

            bot.reply_to(message, response.choices[0].message.content)

            bot.send_message(chat_id, "Рад был помочь! Если у вас возникнут еще вопросы, нажмите Help или SOS.", reply_markup=main_menu())

            del user_states[chat_id]
            del user_dialogs[chat_id]
        else:
            user_states[chat_id] = stage + 1
            next_question = questions[stage + 1]
            bot.send_message(chat_id, next_question)

bot.polling()
