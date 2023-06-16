import telebot, json, sqlite3, threading, re, requests, os, types
from currency_converter import CurrencyConverter



bot = telebot.TeleBot('6016939554:AAGulF-7VHWK2b1YIQa3YRJfEiTXWNpLXYU')
API = '408c3f1147da01b24019171b397ccb6a'



currency = CurrencyConverter()
amount = 0

# Функція для створення об'єкта conn і cursor у кожному потоці
def get_database():
    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    return conn, cursor

# Створення таблиці для зберігання даних про зворотній зв'язок
def create_feedback_table():
    conn, cursor = get_database()
    with conn:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                name TEXT,
                phone TEXT,
                email TEXT
            )
        ''')
        

# Запуск функції create_feedback_table для створення таблиці
create_feedback_table()

# Функція для вставки даних про зворотній зв'язок до бази даних
def insert_feedback_data(user_id, name, phone, email):
    conn, cursor = get_database()
    with conn:
        cursor.execute("INSERT INTO feedback (user_id, name, phone, email) VALUES (?, ?, ?, ?)",
                       (user_id, name, phone, email))
        


# Створення головного меню з кнопкою "Give Feedback"
menu_markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
button_feedback = telebot.types.KeyboardButton('Give Feedback')
button_command1 = telebot.types.KeyboardButton('Weather')
button_command2 = telebot.types.KeyboardButton('Choose your language')
button_command3 = telebot.types.KeyboardButton('Currency Converter')
menu_markup.add(button_feedback, button_command1, button_command2, button_command3)




# Функція для завантаження файлу локалізації за мовою
def load_localization(language):
    filename = f"strings_{language}.json"
    path = os.path.join(os.getcwd(), filename)
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


# Визначте мову за замовчуванням
default_language = "english"

# Завантажте локалізацію за замовчуванням
localization = load_localization(default_language)


# Створіть клавіатуру з кнопками мов
language_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
language_keyboard.add("English", "Polski", "Українська")

# Створіть клавіатуру з кнопками мов
language_keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
language_keyboard.add("English", "Polski", "Українська")


@bot.message_handler(func=lambda message: message.text in ["en", "pl", "ua"])
def handle_language_selection(message):
    user_id = message.from_user.id
    selected_language = message.text.lower()
    
    # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
    state = bot_state.get(user_id, {})
    state["language"] = selected_language  # Зберегти обрану мову у стані бота
    bot_state[user_id] = state

    # Завантажити вибрану локалізацію
    localization = load_localization(selected_language)
    
    # Відправити повідомлення з підтвердженням обраної мови
    language_changed_text = localization["language_changed"]
    bot.send_message(user_id, f"{language_changed_text} {selected_language.capitalize()}")

    

# Створіть словник для зберігання стану бота
bot_state = {}

    
@bot.message_handler(commands=['start'])
def start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username

        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)
        
        # Замініть URL-адреси на ваші посилання на профілі GitHub
        greeting_text = localization["greeting"]
        github_link = 'https://github.com/evhenhoretski'
        resume_en = 'Evhen_Horetskyi.pdf'
        resume_pl = 'Evhen_Horetskyi_pl.pdf'
        
        markup = telebot.types.InlineKeyboardMarkup()
        
        # Додаємо кнопки для вибору мови резюме
        button_link = telebot.types.InlineKeyboardButton(text='GitHub', url=github_link)
        button_file = telebot.types.InlineKeyboardButton(text=localization['resume_file'], callback_data='resume_file')
        

        markup.add(button_link, button_file)
        
        
        bot.send_message(user_id, f"{greeting_text}, {username}! {localization['profile']}", reply_markup=markup)
    
    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")






@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
        
    try:
        user_id = call.from_user.id

        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)
        
        if call.data == 'resume_file':
            # Додаємо кнопки для вибору мови резюме
            markup = telebot.types.InlineKeyboardMarkup()
            button_en = telebot.types.InlineKeyboardButton(text='English', callback_data='resume_en')
            button_pl = telebot.types.InlineKeyboardButton(text='Polski', callback_data='resume_pl')
            markup.add(button_en, button_pl)
            
            bot.send_message(user_id, localization["choose_resume_language"], reply_markup=markup)

        elif call.data == 'resume_en':
            resume_file = open('Evhen_Horetskyi.pdf', 'rb')
            bot.send_document(user_id, resume_file)
            resume_file.close()
            
        elif call.data == 'resume_pl':
            resume_file = open('Evhen_Horetskyi_pl.pdf', 'rb')
            bot.send_document(user_id, resume_file)
            resume_file.close()
        elif call.data != 'else':
            values = call.data.upper().split('/')
            res = currency.convert(amount, values[0], values[1])
            bot.send_message(call.message.chat.id, f'Result: {round(res, 2)}. You can enter the amount again')
            #bot.register_next_step_handler(call.message, summa)
        else:
            bot.send_message(call.message.chat.id, localization['enter_through'])
            #bot.register_next_step_handler(call.message, my_currency)

    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")

markup_conv = None
def summa(message):
    global amount
    global markup_conv
    try:
        amount = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, localization['wrong_format'])
        #bot.register_next_step_handler(message, summa)
        return

    if amount > 0:
        markup_conv = telebot.types.InlineKeyboardMarkup(row_width=4)
        btn1 = telebot.types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = telebot.types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = telebot.types.InlineKeyboardButton('USD/PLN', callback_data='usd/pln')
        btn4 = telebot.types.InlineKeyboardButton('PLN/USD', callback_data='pln/usd')
        btn5 = telebot.types.InlineKeyboardButton('PLN/EUR', callback_data='pln/eur')
        btn6 = telebot.types.InlineKeyboardButton('EUR/PLN', callback_data='eur/pln')
        btn7 = telebot.types.InlineKeyboardButton(localization['other_meaning'], callback_data='eur/pln')
        markup_conv.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
        bot.send_message(message.chat.id, localization['select_pair'], reply_markup=markup_conv)
    else:
        pass
        #bot.send_message(message.chat.id, localization['number_must'])
        #bot.register_next_step_handler(message, summa)


def my_currency(message):
        try:
            values = message.text.upper().split('/')
            res = currency.convert(amount, values[0], values[1])
            bot.send_message(message.chat.id, f'Result: {round(res, 2)}. You can enter the amount again')
            #bot.register_next_step_handler(message, summa)
        except Exception:
            bot.send_message(message.chat.id, localization['smt_wrong'])
            #bot.register_next_step_handler(message, summa)



@bot.message_handler(func=lambda message: True)
def handle_message(message):


    try:
        user_id = message.from_user.id
        text = message.text

        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)

        if text == localization['menu_option1']:
            # Відправляємо запит на зворотній зв'язок
            bot.send_message(user_id, localization['enter_name'])
            bot.register_next_step_handler(message, get_name)
        elif text == localization['menu_option2']:
            bot.send_message(user_id, localization['weather_prompt'])
            bot.register_next_step_handler(message, get_weather)
        elif text == localization['menu_option3']:
            bot.send_message(user_id, localization['language_selection'], reply_markup=language_keyboard)
            bot.register_next_step_handler(message, handle_language_selection)
        elif text == localization['menu_option4']:
            bot.send_message(user_id, localization['enter_amount'], reply_markup=markup_conv)
            bot.register_next_step_handler(message, summa)
        else:
            bot.send_message(user_id, localization['menu_navigate'], reply_markup=menu_markup)

    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")





    

@bot.message_handler(func=lambda message: True)
def get_weather(message):
    user_id = message.from_user.id

    state = bot_state.get(user_id, {})
    language = state.get("language", default_language) 
    # Завантажити словник локалізації для обраної мови
    localization = load_localization(language)

    city = message.text.strip().lower()
    res = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API}&units=metric')
    if res.status_code == 200:
        data = json.loads(res.text)
        temp = data["main"]["temp"]

        weather_message = localization['weather_now'].format(temperature=temp)
        bot.send_message(user_id, weather_message)

        # image = 'sunny.png' if temp > 5.0 else 'sun.png'
        # file = open('./' + image, 'rb')
        # bot.send_photo(message.chat.id, file)
    else:
        bot.send_message (user_id, localization['city_wrong'])

    







def get_name(message): 
    try:
        user_id = message.from_user.id
        name = message.text
        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)

        
        bot.send_message(user_id, localization['enter_phone'])
        bot.register_next_step_handler(message, get_phone, name)

    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")



def get_phone(message, name):
    try:
        user_id = message.from_user.id
        phone = message.text
        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)
        
        bot.send_message(user_id, localization['enter_email'])
        bot.register_next_step_handler(message, get_email, name, phone)
    
    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")


# Перевірка правильності формату електронної пошти
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def get_email(message, name, phone):
    try:
        user_id = message.from_user.id
        email = message.text
        # Отримайте стан бота для поточного користувача або створіть новий, якщо його немає
        state = bot_state.get(user_id, {})
        language = state.get("language", default_language) 
        # Завантажити словник локалізації для обраної мови
        localization = load_localization(language)
        
        if is_valid_email(email):
            # Записуємо електронну пошту у змінну зворотнього зв'язку
            bot.feedback_email = email
        
            # Додавання даних про зворотній зв'язок до бази даних
            insert_feedback_data(user_id, name, phone, email)
            
            bot.send_message(user_id, localization['feedback_thank_you'])
        else:
            bot.send_message(user_id, localization['invalid_email'])

    except Exception as e:
        # Обробка помилок тут
        bot.send_message(user_id, f"An error occurred: {str(e)}")


bot.polling()
