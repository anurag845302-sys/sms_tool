# file: telegram_sms_bot.py, target: Python 3.10+, dependencies: requests, python-telegram-bot
import logging
import time
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

API_KEY = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE4MjMzMzQwNTUsImlhdCI6MTc5MTc5ODA1NSwicmF5IjoiM2I3NWVkZDUwMzU0ZjU1ODNkNjNmMjEzZTJkZTNkZDciLCJzdWIiOjQ2MTY3NDh9.toWh5Vb9DbCZk_B1Bb11q36H4u_wa8aeT8Oln79-S_MUsDcOSXx6rnfozaKW38CB8dI8m0u2r9wEGwM2jZG0tUjdpfh7R6N3MSxQY5JYRpJ3rE4guOBR2n8Mvu6Hkhw5avJNQmcn7ldjuWV6pXvvK5kkgWvD9va5sMeSMG2PZBIGwJHzNFMMLfZ01Qgj6ha2vKUJ2Su0-RQJmlvNpWjVdvfnuzXnsPSji_KQzquiWx1N23tfbkwszpilU5uCcOHytGr5xxfxI4AoJs5Un937M1jin1ZstKMsJdAFCIIYirNiGefFNv50RjMHrc2aiBxrzbZ3OfEV7nyCTkECVtWz6A"
BASE_URL = "https://5sim.net/v1/user"
GUEST_URL = "https://5sim.net/v1/guest"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json",
}

# Supported low-cost countries
COUNTRIES = {
    "Colombia": "colombia",
    "Liberia": "liberia",
    "Ecuador": "ecuador",
    "Honduras": "honduras",
    "Sri Lanka": "srilanka",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = [
      [InlineKeyboardButton(name, callback_data=code)]
      for name, code in COUNTRIES.items()
  ]
  reply_markup = InlineKeyboardMarkup(keyboard)
  await update.message.reply_text(
      "Sasta number lene ke liye country select karo:", reply_markup=reply_markup
  )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  country = query.data
  await query.edit_message_text(
      text=f"Selected country: {country.capitalize()}. Checking cheapest"
      " stock under $0.30..."
  )

  # Fetch and buy cheapest under $0.30
  price_url = f"{GUEST_URL}/prices?country={country}&product=telegram"
  try:
    res = requests.get(price_url, timeout=10)
    if res.status_code == 200:
      data = res.json()
      country_data = data.get(country, {}).get("telegram", {})
      valid_ops = []
      for op, details in country_data.items():
        cost = details.get("cost", 0)
        count = details.get("count", 0)
        if cost <= 0.30 and count > 0:
          valid_ops.append({"operator": op, "price": cost})

      if not valid_ops:
        await query.edit_message_text(
            text=f"❌ {country.capitalize()} me $0.30 se kam me koi stock"
            " available nahi hai."
        )
        return

      valid_ops.sort(key=lambda x: x["price"])
      cheapest = valid_ops[0]
      operator = cheapest["operator"]
      price = cheapest["price"]

      # Buy number
      buy_url = f"{BASE_URL}/buy/activation/{country}/{operator}/telegram"
      buy_res = requests.get(buy_url, headers=headers)

      if buy_res.status_code == 200:
        b_data = buy_res.json()
        order_id = b_data.get("id")
        phone = b_data.get("phone")

        await query.edit_message_text(
            text=(
                f"✅ Number Mil Gaya!\n\n📱 Phone: `+{phone}`\n💰 Cost:"
                f" ${price}\n运营商 (Operator): {operator}\n\nOTP ka wait kar"
                " rahe hain..."
            ),
            parse_mode="Markdown",
        )

        # Poll OTP (Background loop simulation or quick check)
        code = poll_otp_sync(order_id)
        if code:
          await context.bot.send_message(
              chat_id=query.message.chat_id,
              text=f"🎉 **OTP Code Received:** `{code}`",
              parse_mode="Markdown",
          )
        else:
          await context.bot.send_message(
              chat_id=query.message.chat_id,
              text=(
                  "⏳ Timeout ho gaya! Number automatically cancel kar diya"
                  " gaya hai aur paise refund ho gaye hain."
              ),
          )
      else:
        await query.edit_message_text(
            text=f"❌ Purchase failed: {buy_res.text}"
        )
  except Exception as e:
    await query.edit_message_text(text=f"❌ Error: {str(e)}")


def poll_otp_sync(order_id, timeout=120, interval=5):
  url = f"{BASE_URL}/check/{order_id}"
  start_time = time.time()
  while time.time() - start_time < timeout:
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
      try:
        data = res.json()
        if data.get("status") == "RECEIVED":
          sms_list = data.get("sms", [])
          if sms_list:
            return sms_list[0].get("code")
      except:
        pass
    time.sleep(interval)

  # Timeout -> Cancel
  requests.get(f"{BASE_URL}/cancel/{order_id}", headers=headers)
  return None


if __name__ == "__main__":
  TOKEN = "8850213208:AAFFC4TG2UndJo0gKg-t1IPSOs1RP_5Tahw"
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CallbackQueryHandler(button_handler))
  print("Telegram Bot is running...")
  app.run_polling()