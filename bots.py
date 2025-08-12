# bots.py  (Demo OTP flow)
import random
import asyncio
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- ====== SET YOUR TOKEN HERE ======
TOKEN = "8407350933:AAGnZuEeabFyz1lwgG6a7DDymS6BgcE4DwM"
# =====================================

# In-memory state (for demo). Production: use DB.
# structure: states[chat_id] = {"step": str, "choice": str, "number": str, "otp": str}
states = {}

MENU_BUTTONS = [
    [KeyboardButton("3GB"), KeyboardButton("2GB")],
    [KeyboardButton("50MB"), KeyboardButton("Minutes")],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # reset state
    states.pop(chat_id, None)

    # Salam + dua
    await update.message.reply_text("Assalamualaikum —  Allah apko khush rakhe 🤲\n\nAb niche se apni choice select karein.")
    # show menu
    reply_markup = ReplyKeyboardMarkup(MENU_BUTTONS, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Select package:", reply_markup=reply_markup)

    # set state
    states[chat_id] = {"step": "await_choice"}

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    # If no state, ask to start
    if chat_id not in states:
        await update.message.reply_text("Pehlay /start karo takay flow begin ho.\nType /start")
        return

    state = states[chat_id]

    # Step: waiting for choice
    if state["step"] == "await_choice":
        if text not in ("3GB", "2GB", "50MB", "Minutes"):
            await update.message.reply_text("Please select one of the menu buttons (3GB / 2GB / 50MB / Minutes).")
            return

        # store choice and ask for number
        state["choice"] = text
        state["step"] = "await_number"
        await update.message.reply_text(
            f"Aap ne select kiya: *{text}*\n\nAb apna number bhejein (example format): `03XXXXXXXXX`",
            parse_mode="Markdown"
        )
        return

    # Step: waiting for number
    if state["step"] == "await_number":
        # basic validation — just demo
        num = text.replace(" ", "")
        if not (num.startswith("03") and len(num) == 11 and num.isdigit()):
            await update.message.reply_text("Number sahi format mein nahin hai. Example: 03312345678\nDobara try karein.")
            return

        state["number"] = num
        # generate fake OTP
        otp = f"{random.randint(1000, 9999)}"
        state["otp"] = otp
        state["step"] = "await_otp"

        # In real system, OTP would be sent by telecom. Here we SHOW the OTP (demo).
        await update.message.reply_text(
            f"Demo: OTP bhej diya gaya hai aapko (fake). OTP: *{otp}*\n\nPlease enter the OTP to confirm.",
            parse_mode="Markdown"
        )
        return

    # Step: waiting for OTP
    if state["step"] == "await_otp":
        entered = text.strip()
        if entered == state.get("otp"):
            choice = state.get("choice", "package")
            # success — "activate" the package (demo)
            await update.message.reply_text(
                f"OTP verified ✅\n\nCongratulations! {choice} has been activated (demo confirmation)."
            )
            # clear state
            states.pop(chat_id, None)
        else:
            await update.message.reply_text("Wrong OTP. Agar chahen to number phir se bhejein ya /start se dobara shuru karein.")
        return

    # Fallback
    await update.message.reply_text("Kuch samajh nahi aaya — /start se dobara shuru karein.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Demo OTP bot running (polling).")
    app.run_polling()

if __name__ == "__main__":
    main()
