import os
import sys
import time
import discord
import aiohttp
import aiofiles
from discord_webhook import DiscordWebhook


class ConsoleUtils:
    """
    a class that contains a bunch of console utils such as colors, title and clear console

    TODO: move this to it's own module.
    """

    def __init__(self) -> None:
        raise NotImplementedError()

    class ConsoleColors:
        """a class that contains a bunch of console colors."""
        RESET = '\033[0m'
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'

    @staticmethod
    def clear_console() -> None:
        """clears the console."""
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            os.system('cls')
        elif os.name in ('linux', 'osx', 'posix'):
            os.system('clear')
        else:
            print("Your operating system is not supported.")

    @staticmethod
    def set_console_title(title: str) -> None:
        """sets the console title."""
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif os.name in ('linux', 'osx', 'posix'):
            os.system(f'echo -ne "\033]0;{title}\007"')
        else:
            print("Your operating system is not supported.")

ConsoleUtils = ConsoleUtils()
ConsoleColors = ConsoleUtils.ConsoleColors

# Set console title
ConsoleUtils.set_console_title("discord img scraper | by @obstructive")
ConsoleUtils.clear_console()

client = discord.Client()

# Scrape images from a Discord channel's chat history
async def scrape_channel():
    channel_id = input(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter channel id: ")
    channel = await client.fetch_channel(channel_id)
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.webm', '.gifv', '.mp4v', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webp')):
                    # Write image URL to file
                    with open("images.txt", "a", encoding="utf-8") as f:
                        f.write(attachment.url + '\n')
                    # Print image URL to console
                    print(f"{ConsoleUtils.ConsoleColors.MAGENTA}[{ConsoleUtils.ConsoleColors.RESET}~{ConsoleUtils.ConsoleColors.MAGENTA}]{ConsoleUtils.ConsoleColors.RESET} {attachment.url}")
                else:
                    pass
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
            # download image, send to webhook, delete image
            async with aiohttp.ClientSession() as session, session.get(line.strip()) as r:
                print(f"{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} {line.strip()}")
                if r.status == 200:
                    f = await aiofiles.open('temp.jpg', mode='wb')
                    await f.write(await r.read())
                    await f.close()
                    webhook = DiscordWebhook(url=webhook_url, rate_limit_retry=True)
                    with open("temp.jpg", "rb") as f:
                        webhook.add_file(file=f.read(), filename='image.jpg')
                    response = webhook.execute()
                    os.remove("temp.jpg") 

async def menu():
    with open('images.txt') as f:
        num_lines = len(f.readlines())
    os.system('cls')
    print('''\x1b[38;5;199m
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
            "\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Choice{{C.RESET}}: \x1b[0m")
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
            sys.exit()
        else:
            print("\x1b[38;5;199m[{{C.RESET}}~\x1b[38;5;199m] {{C.RESET}}Invalid Choice")
            time.sleep(1)
            await menu()

@client.event
async def on_ready():
    await menu()

client.run(token, reconnect=True)
