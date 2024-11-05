import logging
import threading
import warnings
from telegram import Update, Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters
from binance.client import Client
from binance import ThreadedWebsocketManager
import pandas as pd
import key  # Импортируйте ваш файл с ключами API
#import gui  # Импортируйте ваш файл с GUI

# Подавление предупреждений
warnings.filterwarnings("ignore", category=UserWarning, module="telegram.utils.request")

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Создание клиента Binance
client = Client(key.api_key, key.api_secret, testnet=True)
df, d = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume', 'num']), []

# Глобальные переменные для хранения объекта Bot и twm
bot = None
twm = None
authorized_users = set()

def start(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id not in authorized_users:
        update.message.reply_text('Введите пароль для доступа:')
    else:
        show_menu(update)

def show_menu(update: Update):
    keyboard = [
        [KeyboardButton('/run'), KeyboardButton('/stop')],
        [KeyboardButton('/info')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text('Меню:', reply_markup=reply_markup)

def password(update: Update, context: CallbackContext) -> None:
    if update.message.text == '1111':
        authorized_users.add(update.message.chat_id)
        update.message.reply_text('Доступ разрешен.')
        show_menu(update)
    else:
        update.message.reply_text('Неверный пароль. Попробуйте снова.')

def run(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id in authorized_users:
        global bot, twm
        bot = context.bot
        threading.Thread(target=Run, args=(update.message.chat_id,)).start()
        update.message.reply_text('Started getting data from Binance.')
    else:
        update.message.reply_text('Доступ запрещен. Введите пароль.')

def stop(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id in authorized_users:
        global twm
        if twm:
            twm.stop()
            update.message.reply_text('Stopped getting data from Binance.')
        else:
            update.message.reply_text('No active data stream to stop.')
    else:
        update.message.reply_text('Доступ запрещен. Введите пароль.')

def info(update: Update, context: CallbackContext) -> None:
    if update.message.chat_id in authorized_users:
        update.message.reply_text('Какой же Dandr11 молодец, просто красавец')
    else:
        update.message.reply_text('Доступ запрещен. Введите пароль.')

def Run(chat_id):
    global twm
    twm = ThreadedWebsocketManager(api_key=key.api_key, api_secret=key.api_secret)
    twm.start()
    twm.start_kline_socket(symbol="ETHUSDT", callback=lambda msg: Di(msg, chat_id))
    twm.join()

def Di(msg, chat_id, hours=3):
    global bot
    d.append(msg)
    if len(d) == 6:
        del d[0]
    if len(d) >= 5:
        for y in range(-5, -1):
            event_time = pd.to_datetime(d[y]['E'], unit='ms') + pd.Timedelta(hours=hours)
            df.loc[y] = [event_time, float(d[y]['k']['o']), float(d[y]['k']['h']),
                         float(d[y]['k']['l']), float(d[y]['k']['c']),
                         float(d[y]['k']['v']), int(d[y]['k']['n'])]
        # Отправка сообщения в Telegram бота
        bot.send_message(chat_id=chat_id, text=str(df.iloc[-1]))

def main():
    updater = Updater("7772169803:AAFOT0hDlbBkiC2vVv5fYMGpjgQeQRMAm78")

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("run", run))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("info", info))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, password))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
