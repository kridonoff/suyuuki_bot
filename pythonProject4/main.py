import sqlite3
import telebot
from telebot import types

bot = telebot.TeleBot('6114796729:AAHR1lW0uYscS4Z9xnPB58fy1C64VMfCZVc')

#Обробка команди /start
@bot.message_handler(commands=['start'])
def on_start(message):

    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('Створити заявку', 'Редагувати заявку')
    keyboard.row('Список послуг', 'Зворотній зв`язок')
    keyboard.add('Передоплата')
    bot.send_message(message.chat.id, "Вас вітає сервіс підтримки користувачів.")
    bot.send_message(message.chat.id, 'Для створення заяки нажміть кнопку Створити заявку:', reply_markup=keyboard)
    bot.register_next_step_handler(message, on_click)

#Обробка команди /info

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, "В цьому боті ви можете:\nЗамовити одну з послуг, що надаються в вигляді заявки"
                                      "\nРедагувати створені вами заявки\nОплатити замовлену послугу карткою")


#Обробка подій на кнопки
@bot.message_handler(func=lambda message: True)
def on_click(message):
    if message.text == 'Створити заявку':
        main(message)
    elif message.text == 'Редагувати заявку':
        bot.send_message(message.chat.id, 'Введіть номер заявки, яку потрібно відредагувати')
        bot.register_next_step_handler(message, edit_application)
    elif message.text == 'Список послуг':
        bot.send_message(message.chat.id,
                             'В цьому боті ви можете замовити послугу з переліку нижче. \nПослуги які надаються:'
                             '\n1. Чистка ПК;\n2. Ремонт ПК;\n3. Ремонт моніторів;\n4. Ремонт принтерів;\n5. '
                             'Установка ПЗ, драйверів;\n6. Діагностика ПК;\n7. Оптимізація налаштувань та конфігурацій, '
                             'очищення системи та реєстру;\n8. Налагодження мережевого з`єднання;')
    elif message.text == 'Зворотній зв`язок':
        bot.send_message(message.chat.id, 'Наша пошта для зв`язку: kridonoff@gmail.com\nНомер телефону: +380 68 123 45 67')
    elif message.text == 'Передоплата':
        bot.send_message(message.chat.id, 'Введіть id заявки')
        bot.register_next_step_handler(message, payment)
# Створення заявки
@bot.message_handler()
def main(message):
    if not message.text.isdigit():
        conn = sqlite3.connect('aadd.sql')
        cur = conn.cursor()

        cur.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, '
                    'name VARCHAR(50), broke VARCHAR(50), phone VARCHAR(50), adress VARCHAR(50))')
        conn.commit()
        conn.close()

        bot.send_message(message.chat.id, 'Введіть Ім`я')
        bot.register_next_step_handler(message, user_name)
#Реакція на введене ім`я
def user_name(message):
    global name
    name = message.text.strip()

    bot.send_message(message.chat.id, 'Введіть вид послуги')
    bot.send_message(message.chat.id, 'В цьому боті ви можете замовити послугу з переліку нижче. \nПослуги які '
                                      'надаються:\n1. Чистка ПК;\n2. Ремонт ПК;\n3. Ремонт моніторів;\n4. '
                                      'Ремонт принтерів;\n5. Установка ПЗ, драйверів;\n6. Діагностика ПК;\n7. '
                                      'Оптимізація налаштувань та конфігурацій, очищення системи та реєстру;\n8. '
                                      'Налагодження мережевого з`єднання;')
    bot.register_next_step_handler(message, user_broke)
# Реакція на введену послугу
def user_broke(message):
    global broke
    broke = message.text.strip()

    bot.send_message(message.chat.id, 'Введіть номер телефону(+38(099)999-99-99)')
    bot.register_next_step_handler(message, user_phone)
# Реакція на введений номер телефону
def user_phone(message):
    global phone
    phone = message.text.strip()
    if phone.isalpha():
        bot.send_message(message.chat.id, 'Номер телефону вводиться цифрами:)')
        bot.register_next_step_handler(message, user_phone)
    else:
        bot.send_message(message.chat.id, 'Введіть адресу куди приїхати майстру')
        bot.register_next_step_handler(message, user_adress)
# Реакція на введену адресу та збереження даних в бд
def user_adress(message):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()
    adress = message.text.strip()
    markup1 = types.InlineKeyboardMarkup()

    cur.execute(f"INSERT INTO users (name, broke, phone, adress) VALUES ('%s', '%s', '%s', '%s')" % (name, broke, phone, adress))
    conn.commit()
    cur.execute("SELECT last_insert_rowid()")
    last_id = cur.fetchone()[0]
    cur.close()
    conn.close()

    markup1.add(types.InlineKeyboardButton('Ваш ID: ' + str(last_id), callback_data='get_id'))
    markup1.add(types.InlineKeyboardButton('Передоплата', callback_data='oplata'))

    bot.send_message(message.chat.id, 'Дані прийнято в обробку, Гарного дня!', reply_markup=markup1)

#Обробка кнопок оплати
@bot.callback_query_handler(func=lambda message: True)
def callback(callback):
    if callback.data == 'oplata':

        markup2 = types.InlineKeyboardMarkup()
        inline_btn1 = types.InlineKeyboardButton('Передоплата Monobank', callback_data='monobank')
        inline_btn2 = types.InlineKeyboardButton('Оплата готівкою', callback_data='cash')

        markup2.add(inline_btn1, inline_btn2)
        bot.send_message(callback.message.chat.id, 'Тариф:\nЧистка ПК - 150 грн\nРемонт ПК - 300 грн\n'
                                                   'Ремонт моніторів- 300 грн\nРемонт принтерів - 400 грн\nУстановка ПЗ'
                                                   ', драйверів - 100 грн\nДіагностика ПК- 100 грн\nОптимізація '
                                                   'налаштувань та конфігурацій, очищення системи та реєстру - 100 грн'
                                                   '\nНалагодження мережевого з`єднання - 300 грн', reply_markup=markup2)
    elif callback.data == 'monobank':

        bot.send_message(callback.message.chat.id, 'Оплатити послугу можна за посиланням'
                                                   '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                                   '5375 4114 2592 6487\n\nОбов`язково вказуйте номер телефону або '
                                                   'id заявки в коментарях оплати')
        bot.send_message(callback.message.chat.id, 'Гарного вам дня!!')
        bot.register_next_step_handler(callback.message, on_start)

    elif callback.data == 'cash':
        bot.send_message(callback.message.chat.id, 'До зустрічі, та гарного вам дня')
        bot.register_next_step_handler(callback.message, on_start)

#Редагування заявки
def edit_application(message):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (message.text,))
    application = cur.fetchone()

    if application:
        bot.send_message(message.chat.id, f"Заявка #{application[0]}")
        bot.send_message(message.chat.id, f"Ім'я: {application[1]}")
        bot.send_message(message.chat.id, f"Вид послуги: {application[2]}")
        bot.send_message(message.chat.id, f"Номер телефону: {application[3]}")
        bot.send_message(message.chat.id, f"Адреса куди приїхати майстру: {application[4]}")
        bot.send_message(message.chat.id, "Введіть нове ім'я")
        bot.register_next_step_handler(message, edit_name, application)
    else:
        bot.send_message(message.chat.id, "Заявка з таким ID не знайдена.")

    cur.close()
    conn.close()

#Редагування введеного імені
def edit_name(message, application):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()

    cur.execute("UPDATE users SET name=? WHERE id=?", (message.text.strip(), application[0]))
    conn.commit()

    bot.send_message(message.chat.id, "Ім'я заявки оновлено.")
    bot.send_message(message.chat.id, "Введіть новий вид послуги")
    bot.send_message(message.chat.id, 'В цьому боті ви можете замовити послугу з переліку нижче. \nПослуги які '
                                      'надаються:\n1. Чистка ПК;\n2. Ремонт ПК;\n3. Ремонт моніторів;\n4. '
                                      'Ремонт принтерів;\n5. Установка ПЗ, драйверів;\n6. Діагностика ПК;\n7. '
                                      'Оптимізація налаштувань та конфігурацій, очищення системи та реєстру;\n8. '
                                      'Налагодження мережевого з`єднання;')
    bot.register_next_step_handler(message, edit_broke, application)

    cur.close()
    conn.close()

#Редагування введеного виду послуги
def edit_broke(message, application):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()

    cur.execute("UPDATE users SET broke=? WHERE id=?", (message.text.strip(), application[0]))
    conn.commit()

    bot.send_message(message.chat.id, "Вид послуги заявки оновлено.")
    bot.send_message(message.chat.id, "Введіть новий номер телефону(+38(099)999-99-99)")
    bot.register_next_step_handler(message, edit_phone, application)

    cur.close()
    conn.close()

# Редагування введеного номеру телефону
def edit_phone(message, application):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()

    cur.execute("UPDATE users SET phone=? WHERE id=?", (message.text.strip(), application[0]))
    conn.commit()

    bot.send_message(message.chat.id, "Номер телефону заявки оновлено.")

    bot.send_message(message.chat.id, "Введіть нову адресу куди приїхати майстру")
    bot.register_next_step_handler(message, edit_adress, application)

    cur.close()
    conn.close()

#Редагування введеної адреси та оплата якщо потрібно
def edit_adress(message, application):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()
    markup3 = types.InlineKeyboardMarkup()
    markup3.add(types.InlineKeyboardButton('Передоплата', callback_data='oplata'))

    cur.execute("UPDATE users SET adress=? WHERE id=?", (message.text.strip(), application[0]))
    conn.commit()

    bot.send_message(message.chat.id, "Адреса куди приїхати майстру оновлено.")
    bot.send_message(message.chat.id, "Заявка успішно відредагована.", reply_markup=markup3)

    cur.close()
    conn.close()
def payment(message):
    conn = sqlite3.connect('aadd.sql')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE id=?", (message.text,))
    application = cur.fetchone()

    if application:
        bot.send_message(message.chat.id, f"Вид послуги: {application[2]}")
        if application[2] == '1' or application[2] == 'Чистка ПК':
            bot.send_message(message.chat.id, 'До сплати - 150 грн'
                                                   '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                                   '5375 4114 2592 6487\n\n')
        elif application[2] == '2' or application[2] == 'Ремонт ПК':
            bot.send_message(message.chat.id, 'До сплати - 300 грн'
                                             '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                             '5375 4114 2592 6487\n\n')
        elif application[2] == '3'or application[2] == 'Ремонт моніторів':
            bot.send_message(message.chat.id, 'До сплати - 300 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        elif application[2] == '4'or application[2] == 'Ремонт принтерів':
            bot.send_message(message.chat.id, 'До сплати - 400 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        elif application[2] == '5'or application[2] == 'Установка ПЗ, драйверів':
            bot.send_message(message.chat.id, 'До сплати - 100 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        elif application[2] == '6'or application[2] == 'Діагностика ПК':
            bot.send_message(message.chat.id, 'До сплати - 100 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        elif application[2] == '7'or application[2] == 'Оптимізація налаштувань та конфігурацій, очищення системи та реєстру':
            bot.send_message(message.chat.id, 'До сплати - 400 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        elif application[2] == '8'or application[2] == 'Налагодження мережевого з`єднання':
            bot.send_message(message.chat.id, 'До сплати - 300 грн'
                                              '\nhttps://send.monobank.ua/2uBtvM3FSY\n\nабо за номером картки\n'
                                              '5375 4114 2592 6487\n\n')
        else:
            bot.send_message(message.chat.id, 'Такої послуги не існує')
    else: bot.send_message(message.chat.id, "Заявка з таким ID не знайдена.")




bot.polling(none_stop=True)