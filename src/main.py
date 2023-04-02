import os
import sys
import time
import selfcord as discord
import aiohttp
import aiofiles
import contextlib
import random


class ConsoleUtils:
    """
    a class that contains a bunch of console utils such as colors, title and clear console

    TODO: move this to it's own module.
    """

    def __init__(self) -> None:
        
        pass

    class ConsoleColors:
        """a class that contains a bunch of console colors in ANSI format."""

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
            print('Your operating system is not supported.')

    @staticmethod
    def set_console_title(title: str) -> None:
        """sets the console title."""
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            import ctypes

            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif os.name in ('linux', 'osx', 'posix'):
            os.system(f'echo -ne "\033]0;{title}\007"')
        else:
            print('Your operating system is not supported.')

    @staticmethod
    def clear_file(file: str) -> None:
        """clears the file."""
        with open(file, 'r+') as f:
            f.truncate(0)

    @staticmethod
    def delete_files(confirm: bool) -> None:
        """
        delete a subset of files

        delete files that start with file
        """
        for file in os.listdir():
            if file.startswith('file'):
                os.remove(file)


ConsoleUtils = ConsoleUtils()
ConsoleColors = ConsoleUtils.ConsoleColors


ConsoleUtils.clear_file('images.txt')
ConsoleUtils.delete_files(confirm=True)
ConsoleUtils.set_console_title('discord img scraper | by @obstructive')
ConsoleUtils.clear_console()
try:
    with open('token.txt', 'r') as f:
        token = f.read()
except FileNotFoundError:
    
    token = input(
        f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter token: '
    )
    with open('token.txt', 'w') as f:
        f.write(token)


client = discord.Client()




async def scrape_channel():
    channel_id = input(
        f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter channel id: '
    )
    channel = await client.fetch_channel(channel_id)
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:

                if (
                    attachment.url.endswith(
                        (
                            '.png',
                            '.jpg',
                            '.jpeg',
                            '.gif',
                            '.mp4',
                            '.webm',
                            '.gifv',
                            '.mov',
                            '.avi',
                            '.wmv',
                            '.flv',
                            '.mkv',
                        )
                    )
                    and 'onlyfans' not in attachment.url and 'patreon' not in attachment.url and 'telegram' not in attachment.url
                ):
                    with open('images.txt', 'a') as f:
                        print(f'{ConsoleColors.GREEN}[{ConsoleColors.RESET}+{ConsoleColors.GREEN}]{ConsoleColors.RESET} {attachment.url}')
                        f.write(f'{attachment.url}\n')
                        

        with open('images.txt', 'r') as f:
            lines = f.readlines()
        random.shuffle(lines)
        with open('images.txt', 'w') as f:
            f.writelines(lines)


async def send_to_channel():
    channel_id = input(
        f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter channel id: '
    )
    channel = await client.fetch_channel(channel_id)
    with open('images.txt', 'r') as f:
        for line in f:
            with contextlib.suppress(Exception):
                async with aiohttp.ClientSession() as session, session.get(
                    line.strip()
                ) as r:
                    if r.status == 200:
                        __format__ = line.strip().split('.')[-1]
                        f = await aiofiles.open(f'file.{__format__}', mode='wb')
                        await f.write(await r.read())
                        await f.close()
                        await channel.send(
                            file=discord.File(f'file.{__format__}')
                        )
                        os.remove(f'file.{__format__}')
                        ConsoleUtils.clear_file('images.txt')




async def send_to_webhook():
    webhook_url = input(
        f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter Webhook Url: '
    )
    with open('images.txt', 'r', encoding='UTF-8') as f:
        for line in f:
            with contextlib.suppress(Exception):
                async with aiohttp.ClientSession() as session, session.get(
                    line.strip()
                ) as r:
                    if r.status == 200:
                        __format__ = line.strip().split('.')[-1]
                        f = await aiofiles.open(f'file.{__format__}', mode='wb')
                        await f.write(await r.read())
                        await f.close()
                        async with aiohttp.ClientSession() as session:
                            webhook = discord.Webhook.from_url(
                                webhook_url, adapter=discord.AsyncWebhookAdapter(session)
                            )
                            await webhook.send(
                                file=discord.File(f'file.{__format__}')
                            )
                            os.remove(f'file.{__format__}')
                            ConsoleUtils.clear_file('images.txt')


async def menu():
    with open('images.txt') as f:
        len(f.readlines())
    ConsoleUtils.clear_console()
    print(
        
        f'''
        {ConsoleColors.MAGENTA}[1] {ConsoleColors.RESET}Scrape Channel
        {ConsoleColors.MAGENTA}[2] {ConsoleColors.RESET}Send to Channel
        {ConsoleColors.MAGENTA}[3] {ConsoleColors.RESET}Send to Webhook
        {ConsoleColors.MAGENTA}[4] {ConsoleColors.RESET}Credits
        {ConsoleColors.MAGENTA}[5] {ConsoleColors.RESET}Exit
        '''
    )
    while True:
        choice = input(
            f'        {ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Enter choice: '
        )
        if choice == '1':
            await scrape_channel()
            print(
                f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Finished Scraping Channel'
            )
            time.sleep(1)
            await menu()
        elif choice == '2':
            await send_to_channel()
            print(
                f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Finished Sending to Channel'
            )
            time.sleep(3)
            await menu()
        elif choice == '3':
            await send_to_webhook()
            print(
                f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Finished Sending to Webhook'
            )
            time.sleep(3)
            await menu()
        elif choice == '4':
            print(
                f'''
                {ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Made by: {ConsoleColors.MAGENTA}igna{ConsoleColors.RESET}
                {ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Github: {ConsoleColors.MAGENTA}@obstructive{ConsoleColors.RESET}
                '''
            )
            time.sleep(3)
            await menu()
        elif choice == '5':
            print(
                f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Exiting...'
            )
            time.sleep(1)
            sys.exit()
        else:
            print(
                f'{ConsoleColors.MAGENTA}[{ConsoleColors.RESET}~{ConsoleColors.MAGENTA}]{ConsoleColors.RESET} Invalid Choice'
            )
            time.sleep(1)
            await menu()


@client.event
async def on_ready():
    await menu()


client.run(token, reconnect=True)
