import os
import sys
import selfcord as discord
import aiohttp
import aiofiles
import contextlib
import random
import asyncio
from colorama import init, Fore

class ConsoleUtils:
    """
    a class that contains a bunch of console utils like title and clear console

    TODO: #9 (move this to it's own module.)
    """

    def __init__(self) -> None:

        pass
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
init(convert=True)

ConsoleUtils.clear_file('images.txt')
ConsoleUtils.delete_files(confirm=True)
ConsoleUtils.set_console_title('discord img scraper | by @obstructive')
ConsoleUtils.clear_console()
token = input(
    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter token: '
)
client = discord.Client()


async def scrape_channel():
    channel_id = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter channel id: '
    )
    channel = await client.fetch_channel(channel_id)
    async for message in channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.url.endswith(
                    (
                        '.png',
                        '.jpg',
                        '.jpeg',
                        '.gif',
                        '.mp4',
                        '.webm',
                        '.gifv',
                        '.mp4v',
                        '.mov',
                        '.avi',
                        '.wmv',
                        '.flv',
                        '.mkv',
                        '.webp',
                    )
                ):

                    with open('images.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{attachment.url}\n')

                    print(
                        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {attachment.url}'
                    )



                with open('images.txt', 'r', encoding='UTF-8') as f:
                    lines = f.readlines()
                    random.shuffle(lines)
                with open('images.txt', 'w', encoding='UTF-8') as f:
                    f.writelines(lines)


async def send_to_channel():
    channel_id = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter channel id: '
    )
    channel = await client.fetch_channel(channel_id)
    with open('images.txt', 'r') as f:
        for line in f:

            async with (
                aiohttp.ClientSession() as session,
                session.get(line.strip()) as r,
            ):
                if r.status == 200:
                    format = line.strip().split('.')[-1]
                    f = await aiofiles.open(f'file.{format}', mode='wb')
                    await f.write(await r.read())
                    await f.close()
                    try:
                        filename = os.urandom(16).hex()
                        await channel.send(
                            file=discord.File(
                                f'file.{format}',
                                filename=f'{filename}.{format}',
                            )
                        )
                    except discord.errors.HTTPException:
                        pass
                    os.remove(f'file.{format}')
                    print(
                        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                    )
                    ConsoleUtils.clear_file('images.txt')



async def send_to_webhook():
    webhook_url = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Webhook Url: '
    )
    with open('images.txt', 'r', encoding='UTF-8') as f:
        for line in f:

            async with aiohttp.ClientSession() as session, session.get(
                line.strip()
            ) as r:
                if r.status == 200:
                    format = line.strip().split('.')[-1]
                    f = await aiofiles.open(f'file.{format}', mode='wb')
                    await f.write(await r.read())
                    await f.close()
                    webhook = discord.Webhook.from_url(
                        webhook_url, adapter=discord.AsyncWebhookAdapter(session)
                    )
                    with contextlib.suppress(discord.errors.HTTPException):
                        filename = os.urandom(16).hex()
                        await webhook.send(
                            file=discord.File(
                                f'file.{format}',
                                filename=f'{filename}.{format}',
                            )
                        )
                    os.remove(f'file.{format}')
                    print(
                        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                    )
                    ConsoleUtils.clear_file('images.txt')



async def menu():
    with open('images.txt') as f:
        len(f.readlines())
    ConsoleUtils.clear_console()
    print(

        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 1. Scrape Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 2. Send to Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 3. Send to Webhook\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 4. Credits\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 5. Exit'
    )
    while True:
        choice = input(
            f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Choice: '
        )
        if choice == '1':
            await scrape_channel()
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Scraping Channel'
            )
            await asyncio.sleep(1)
            await menu()
        elif choice == '2':
            await send_to_channel()
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Channel'
            )
            await asyncio.sleep(3)
            await menu()
        elif choice == '3':
            await send_to_webhook()
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Webhook'
            )
            await asyncio.sleep(3)
            await menu()
        elif choice == '4':
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Credits:\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Made by: {{C.RESET}}igna#0002\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Github: {{C.RESET}}obstructive'
            )
            await asyncio.sleep(3)
            await menu()
        elif choice == '5':
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Exiting...'
            )
            await asyncio.sleep(1)
            ConsoleUtils.clear_console()
            sys.exit()
        else:
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Invalid Choice'
            )
            await asyncio.sleep(1)
            await menu()


@client.event
async def on_ready():
    await menu()


client.run(token, reconnect=True)
