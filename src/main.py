import contextlib
import os
import time
from discord.ext import commands
from discord_webhook import DiscordWebhook


class ConsoleColors:
    MAGENTA = '\x1b[35m'
    RED = '\x1b[31m'
    RESET = '\x1b[0m'

# Clear console and set window title
os.system('cls & title Finessed')

# Create a client for self-botting
client = commands.Bot(command_prefix="--", self_bot=True, help_command=None)

# Prompt user for Discord token
token = input("Enter Token: ")

# List of image and video file extensions to look for
image_types = ["png", "jpeg", "gif", "jpg", "mp4", "mov", "webm", "gifv"]

# Scrape images from a Discord channel's chat history
async def scrape_channel():
    channel_id = input(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter channel id: ")
    channel = await client.fetch_channel(channel_id)
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if any(attachment.filename.lower().endswith(image_type) for image_type in image_types):
                    # Write image URL to file
                    with open("images.txt", "a", encoding="utf-8") as f:
                        f.write(attachment.url + '\n')
                    # Print image URL to console
                    print(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} {attachment.url}")
                else:
                    # Print message skip message to console
                    print(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}] Message Not An Image | Skipping {ConsoleColors.RESET}")
# Send images to a Discord channel
async def send_to_channel():
    channel_id = input(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter channel id: ")
    channel = await client.fetch_channel(channel_id)
    with open("images.txt", "r") as f:
        for line in f:
            # Print image filename to console
            print(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} {line.strip()}")
            await channel.send(line.strip())

# Send images to a webhook
async def send_to_webhook():
    webhook_url = input(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter Webhook Url: ")
    with open("images.txt", "r") as f:
        for line in f:
            # Print image filename to console
            print(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} {line.strip()}")
            # Send image to webhook
            webhook = DiscordWebhook(url=webhook_url, content=line.strip(), rate_limit_retry=True)
            response = webhook.execute()
            print(response)
###################################################
os.system('cls')


async def menu():
    with open('images.txt') as f:
        num_lines = len(f.readlines())
    os.system('cls')
    print(f'''\x1b[38;5;199m
                 ╔═╗╦╔╗╔╔═╗╔═╗╔═╗╔═╗╔╦╗
                 ╠╣ ║║║║║╣ ╚═╗╚═╗║╣  ║║
                 ╚  ╩╝╚╝╚═╝╚═╝╚═╝╚═╝═╩╝
\x1b[38;5;199m       ╔═════════════════════════════════════════╗
       ║\x1b[38;5;199m[{{C.RESET}}1\x1b[38;5;199m] {{C.RESET}}Scrape Avatars/GIFs\x1b[38;5;199m                     ║
\x1b[38;5;199m       ║\x1b[38;5;199m[{{C.RESET}}2\x1b[38;5;199m] {{C.RESET}}Upload to Server\x1b[38;5;199m                       ║
       ║\x1b[38;5;199m[{{C.RESET}}3\x1b[38;5;199m] {{C.RESET}}Send to Webhook (May be Rate-Limited)\x1b[38;5;199m   ║
       ║\x1b[38;5;199m[{{C.RESET}}4\x1b[38;5;199m] {{C.RESET}}Credits\x1b[38;5;199m                              ║
       ║\x1b[38;5;199m[{{C.RESET}}5\x1b[38;5;199m] {{C.RESET}}Exit\x1b[38;5;199m                                 ║
\x1b[38;5;199m       ╚═════════════════════════════════════════╝

  {{C.RESET}}''')
    while True:
        choice = input(
            f"\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Choice{{C.RESET}}: \x1b[0m")
        if choice == "1":
            await scrape_channel()
            print("\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Scraped Avatars/GIFs")
            time.sleep(1)
            await menu()
        elif choice == "2":
            await send_to_channel()
            print(
                "\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Finished Uploading Scraped Avatars/GIFs to Server")
            time.sleep(3)
            await menu()
        elif choice == "3":
            await send_to_webhook()
            print(
                "\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Finished Sending Scraped Avatars/GIFs to Webhook")
            time.sleep(3)
            await menu()
        elif choice == "4":
            print(
                """\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Credits: {{C.RESET}}
                \x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Discord: {{C.RESET}}igna#0002 n igna#0003
                \x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Github: {{C.RESET}}@obstructive
                """)
            time.sleep(3)
            await menu()
        elif choice == "5":
            print("\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Exiting...")
            time.sleep(1)
            os.system('cls')
            exit()
        else:
            print("\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Invalid Choice")
            time.sleep(1)
            await menu()

@client.event
async def on_ready():
    await menu()

client.run(token, reconnect=True)
