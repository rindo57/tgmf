import os
from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.types import Message

from services.sox import generateSpek
from services.tgFile import tgInfo

#load_dotenv()

helpMessage = """MediaInfo supports the following services:
`• G-DRIVE
• MEGA.nz
• AppDrive
• GDTOT
• Direct download links
• Telegram files`

**Example:**
For MediaInfo:
`/info url`
`reply /info to file`

For audio Spek:
`reply /spek to audio`

For AppleMusic album info:
`/info album_url`

Made by @pseudoboi🧪"""

owner = int(os.getenv('owner'))  # Ensure this is stored as an integer in your environment

app = Client('botsession', 
             api_id=10247139,
             api_hash="96b46175824223a33737657ab943fd6a",
             bot_token="6769415354:AAHh7IfKn11PWuNxUo0qmoIuW7NclxaaFHQ")

print("MediaInfo bot started!", flush=True)


@app.on_message(filters.text & filters.private)
async def hello(client: Client, message: Message):
    try:
        # Unauthorized check
     

        # Handle commands
        if '/start' in message.text:
            await message.reply("Send /help for more info.")
            return

        if '/help' in message.text:
            await message.reply(helpMessage)
            return

        # Process spectrogram request
        if "/spek" in message.text:
            await message.reply("Processing your spectrogram request...")
            await generateSpek(message)  # Ensure generateSpek is an async function
            return

        # Process media info
        if "/info" in message.text:
            if message.reply_to_message:
                await message.reply("Processing your Telegram file request...")
                await tgInfo(client, message)  # Ensure tgInfo is an async function
            elif len(message.text) > 10:
                await message.reply("Processing your DDL request...")
                await ddlinfo(message)  # Ensure ddlinfo is an async function
    except Exception as e:
        await message.reply(f"`An error occurred!`\n{e}")
        print(e, flush=True)


app.run()
