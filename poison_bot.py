import telebot
from telebot import types
import psycopg2
import os


TOKEN = '5077856006:AAGt_p7AHtmo6afIltDoOWBBf7QzB5Ww4KQ'
bot = telebot.TeleBot(TOKEN)

DATABASE_URL = os.environ.get("postgres://xmdkgoosppjkpf:ae401634958b7993c6f603e6a802486f2c6ac9bf88d6d5e9ba2ae25f9cb2a23d@ec2-34-242-84-130.eu-west-1.compute.amazonaws.com:5432/ddmafn6f85lbbi", None)

data_list = []



@bot.message_handler(commands=['start'])
def start(message, res=False):
    # подсоединились к бд, таблица users
    connect = psycopg2.connect(DATABASE_URL, dbname='ddmafn6f85lbbi', user='xmdkgoosppjkpf', password='ae401634958b7993c6f603e6a802486f2c6ac9bf88d6d5e9ba2ae25f9cb2a23d', host='ec2-34-242-84-130.eu-west-1.compute.amazonaws.com')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY,
        username TEXT NOT NULL
    )""")
    connect.commit()

    id_list = []
    people_id = message.chat.id
    id_list.append(people_id)
    id_changed = "('" + str(id_list) + "',)"
    cursor.execute(f"SELECT id FROM users")
    data = cursor.fetchall()

    #почистить бд
    sql_delete_query = """"DELETE from users where id = "'[1167546391]'"""
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
    connect = psycopg2.connect(dbname='d9emvsl74ldlf9', user='ovjpgiaivcagsd', password='b848e6739db3babe64ea0d01efecd668fceb752fe8513840febde14b32a04204', host='ec2-54-246-185-161.eu-west-1.compute.amazonaws.com')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS orders_new(
        name_and_surname TEXT NOT NULL,
        order_name TEXT,
        order_num INTEGER,
        order_price INTEGER,
        order_full_price INTEGER,
        delivery_adress TEXT
    )""")
    connect.commit()

    cursor.execute("""ALTER TABLE orders_new ALTER COLUMN name_and_surname TYPE text;""")
    connect.commit()
    cursor.execute("""ALTER TABLE orders_new ALTER COLUMN order_name TYPE text;""")
    connect.commit()
    cursor.execute("""ALTER TABLE orders_new ALTER COLUMN delivery_adress TYPE text;""")
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
        connect = psycopg2.connect(dbname='d9emvsl74ldlf9', user='ovjpgiaivcagsd', password='b848e6739db3babe64ea0d01efecd668fceb752fe8513840febde14b32a04204', host='ec2-54-246-185-161.eu-west-1.compute.amazonaws.com')
        cursor = connect.cursor()
        cursor.execute(f"SELECT * FROM orders_new")
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
        connect = psycopg2.connect(dbname='d9emvsl74ldlf9', user='ovjpgiaivcagsd', password='b848e6739db3babe64ea0d01efecd668fceb752fe8513840febde14b32a04204', host='ec2-54-246-185-161.eu-west-1.compute.amazonaws.com')
        cursor = connect.cursor()
        cursor.execute("INSERT INTO orders_new (name_and_surname, order_name, order_num, order_price, order_full_price, delivery_adress) VALUES (%s, %s, %s, %s, %s, %s);", (data_list[1], data_list[0], 1, 0, 0, data_list[2]))
        connect.commit()

    make_adress(message)


def add_to_database(order):
    data_list.append(order)
    return data_list



bot.polling(none_stop=True)
