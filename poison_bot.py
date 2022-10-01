import telebot
from telebot import types
import sqlite3

TOKEN = '5077856006:AAGt_p7AHtmo6afIltDoOWBBf7QzB5Ww4KQ'
bot = telebot.TeleBot(TOKEN)

data_list = []


@bot.message_handler(commands=['start'])
def start(message, res=False):
    # подсоединились к бд, таблица users
    connect = sqlite3.connect('madders_database.bd')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username STRING NOT NULL
    )""")
    connect.commit()

    id_list = []
    people_id = message.chat.id
    id_list.append(people_id)
    id_changed = "('" + str(id_list) + "',)"
    cursor.execute(f"SELECT id FROM users")
    data = cursor.fetchall()
    """ почистить бд """
    sql_delete_query = """DELETE from users where id = '[1167546391]'"""
    cursor.execute(sql_delete_query)
    connect.commit()

    for value in data:
        if id_changed != value:
            users_id = [message.chat.id]
            users_name = [message.chat.first_name]
            lst = [users_id, users_name]
            cursor.execute("INSERT INTO users VALUES(?, ?);", (str(lst[0]), str(lst[1])))
            connect.commit()
        else:
            print("user is already in bd")
            continue

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    item1 = types.KeyboardButton('Сделать заказ!')
    item2 = types.KeyboardButton('Как это работает?')
    item4 = types.KeyboardButton('Поддержка')
    markup.add(item1)
    markup.add(item2)
    markup.add(item4)

    start_message = f"//Привет, {message.from_user.first_name}!\nТеперь ты можешь САМ(A) выбирать товары, которые мы " \
                    f"привезем для тебя с самой крупной биржи брендовой одежды!\nСкорее выбирай вещи!♡\n "
    bot.send_message(message.chat.id, start_message, reply_markup=markup)


@bot.message_handler()
def get_user_text(message):
    # подсоединились к бд, таблица orders
    connect = sqlite3.connect('madders_database.bd')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name_and_surname STRING NOT NULL,
        order_name STRING,
        order_num INTEGER,
        order_price INTEGER,
        order_full_price INTEGER,
        delivery_adress STRING
    )""")
    connect.commit()


    if message.text == "Сделать заказ!":
        main_pack(message)



    elif message.text == 'Оформить заказ!':
        add_pack(message)

    elif message.text == 'Ввести адрес!':
        add_pack_2(message)


    elif message.text == "Как это работает?":
        bot.send_message(message.chat.id, f"//Как это работает?\n 1) Присылаете боту название и размер вещи, которую "
                                          f"хотите приобрести.\n 2) Бот уточняет информацию по заказу и передает её "
                                          f"поставщикам. \n 3) Менеджер сообщит вам точную цену и расчетную дату "
                                          f"получения.\n 4)Оплачиваете переводом- посылка уже едет к вам!(при личной "
                                          f"встрече в Москве оплата после получения товара)\nс уважением, MADDERS.")

    elif message.text == "Поддержка":
        manager = '@pollythecreator'
        bot.send_message(message.chat.id, f"по всем вопросам обращайтесь к {manager}")

    elif message.text == "Вернуться на главную!":
        start(message)

    elif message.text == "детки были бы здоровее и вкуснее":
        connect = sqlite3.connect('madders_database.bd')
        cursor = connect.cursor()
        cursor.execute(f"SELECT * FROM orders")
        data = cursor.fetchall()
        bot.send_message(message.chat.id, str(data))


def main_pack(message):
    def make_order(message):
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        msg = bot.send_message(message.from_user.id, "Полный список названий вещей с размерами:",
                               reply_markup=keyboard1)
        bot.register_next_step_handler(msg, help_order)


    def help_order(message):
        order = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item = types.KeyboardButton('Оформить заказ!')
        markup.add(item)
        bot.send_message(message.from_user.id, f"Ваш заказ:\n {order}.\nОформляем?", reply_markup=markup)
        add_to_database(order)


    make_order(message)




def add_pack(message):
    def make_name(message):
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        msg = bot.send_message(message.from_user.id, "На чьё имя оформляем посылку? (введите своё имя и фамилию)",
                               reply_markup=keyboard1)
        bot.register_next_step_handler(msg, get_name)

    def get_name(message):
        name = message.text
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item = types.KeyboardButton('Ввести адрес!')
        markup.add(item)
        bot.send_message(message.from_user.id, f"Теперь нужно ввести адрес для оформления доставки!",
                         reply_markup=markup)
        add_to_database(name)

    make_name(message)


def add_pack_2(message):
    def make_adress(message):
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True)
        msg = bot.send_message(message.from_user.id, "Введите полный адрес доставки: ", reply_markup=keyboard1)
        bot.register_next_step_handler(msg, get_adress)

    def get_adress(message):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        item = types.KeyboardButton('Вернуться на главную!')
        markup.add(item)
        adress = message.text
        bot.send_message(message.from_user.id,
                         "Спасибо за заказ!♡\nЦену и сроки доставки вам сообщит наш менеджер после обработки заказа!",
                         reply_markup=markup)
        add_to_database(adress)
        connect = sqlite3.connect('madders_database.bd')
        cursor = connect.cursor()
        sqlite_insert_with_param = "INSERT INTO orders (name_and_surname, order_name, order_num, order_price,order_full_price, delivery_adress) VALUES (?, ?, ?, ?, ?, ?);"
        data_tuple = (data_list[1], data_list[0], 1, 0, 0, data_list[2])
        cursor.execute(sqlite_insert_with_param, data_tuple)
        connect.commit()

    make_adress(message)


def add_to_database(order):
    data_list.append(order)
    return data_list



bot.polling(none_stop=True)
