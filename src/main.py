import os
import sys
import selfcord as discord
import aiohttp
import aiofiles
import asyncio
from colorama import init, Fore
import random

class ConsoleUtils:
    """
    A class that provides console utilities, such as clearing the console, setting the console title,
    clearing a file, and deleting a subset of files.

    Attributes:
        None

    Methods:
        clear_console():
            Clears the console.

        set_console_title(title: str):
            Sets the title of the console window.

        clear_file(file: str):
            Clears the contents of a given file.

        delete_files(confirm: bool):
            Deletes a subset of files that start with 'file' from the current directory.
    """

    @staticmethod
    def clear_console() -> None:
        """
        Clears the console window.

        Args:
            None

        Returns:
            None
        """
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            os.system('cls')
        elif os.name in ('linux', 'osx', 'posix'):
            os.system('clear')
        else:
            print('Your operating system is not supported.')

    @staticmethod
    def set_console_title(title: str) -> None:
        """
        Sets the title of the console window.

        Args:
            title: A string representing the title to set.

        Returns:
            None
        """
        if os.name in ('nt', 'dos', 'ce', 'win32', 'win64'):
            import ctypes

            ctypes.windll.kernel32.SetConsoleTitleW(title)
        elif os.name in ('linux', 'osx', 'posix'):
            os.system(f'echo -ne "\033]0;{title}\007"')
        else:
            print('Your operating system is not supported.')

    @staticmethod
    def clear_file(file: str) -> None:
        """
        Clears the contents of a given file.

        Args:
            file: A string representing the file to clear.

        Returns:
            None
        """
        with open(file, 'r+') as f:
            f.truncate(0)

    @staticmethod
    def delete_files(confirm: bool) -> None:
        """
        Deletes a subset of files that end with '.*' from the current directory but not images.txt, token.txt or main.py.

        Args:
            confirm: A boolean indicating whether to ask for confirmation before deleting the files.

        Returns:
            None
        """
        for file in os.listdir():
            if file in ('images.txt', 'token.txt', 'main.py'):
                continue
            if confirm:
                response = input(
                    f'Are you sure you want to delete {file}? (y/n) '
                )
                if response.lower() != 'y':
                    continue
            os.remove(file)


console_utils = ConsoleUtils()
init(convert=True)

console_utils.clear_file('images.txt')
console_utils.delete_files(confirm=False)
console_utils.set_console_title('discord img scraper | by @obstructive')
console_utils.clear_console()

try:
    with open('token.txt', 'r') as f:
        token = f.read().strip()
except FileNotFoundError:
    token = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter your token: '
    )
    with open('token.txt', 'w') as f:
        f.write(token)

client = discord.Client(chunk_guilds_at_startup=False)


async def scrape_channel(channel_id):
    """
    Scrapes a Discord channel for image and video attachments and saves their URLs to a text file.

    Args:
        client: A Discord client object used to fetch the channel.

    Returns:
        None
    """
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
                            '.mp4v',
                            '.mov',
                            '.avi',
                            '.wmv',
                            '.flv',
                            '.mkv',
                            '.webp',
                        )
                    )
                    and 'onlyfans' not in attachment.url.lower()
                    and 'brazzers' not in attachment.url.lower()
                ):

                    with open('images.txt', 'a', encoding='utf-8') as f:
                        f.write(f'{attachment.url}\n')

                    print(
                        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {attachment.url}'
                    )
            # open the images.txt and randomize the order of the URLs

            with open('images.txt', 'r') as f:
                lines = f.readlines()
                random.shuffle(lines)

            with open('images.txt', 'w') as f:
                f.writelines(lines)


#


async def scrape_category(category_id):
    """
    Scrapes a Discord category for image and video attachments and saves their URLs to a text file.

    Args:
        client: A Discord client object used to fetch the category.

    Returns:
        None
    """
    category = await client.fetch_channel(category_id)

    for channel in category.channels:
        await scrape_channel(channel.id)


async def scrape_hentai(channel_id):
    """
    Scrapes a Discord channel for image and video attachments and saves their URLs to a text file.

    Args:
        client: A Discord client object used to fetch the channel.

    Returns:
        None
    """
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
            with open('images.txt', 'r') as f:
                lines = f.readlines()
                lines.sort(key=lambda x: int(x.split('/')[-1].split('.')[0]))
            with open('images.txt', 'w') as f:
                f.writelines(lines)


async def send_to_channel(channel_id):
    """
    This function sends files from a list of URLs to a Discord channel.
    It takes input for channel ID and reads the URLs from a file 'images.txt'.
    It then downloads each image, saves it to a file with a randomly generated name,
    sends it to the Discord channel and clears the file 'images.txt'.
    """

    channel = await client.fetch_channel(channel_id)

    with open('images.txt', 'r') as f:
        async with aiohttp.ClientSession() as session:
            for line in f:
                async with session.get(line.strip()) as r:

                    if r.status == 200:

                        file_format = line.strip().split('.')[-1]
                        file_name = os.urandom(16).hex() + '.' + file_format
                        async with aiofiles.open(file_name, mode='wb') as f:
                            await f.write(await r.read())

                        try:
                            await channel.send(
                                file=discord.File(
                                    file_name, filename=file_name
                                )
                            )

                            os.remove(file_name)
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                            )
                        except discord.errors.HTTPException:
                            pass

    ConsoleUtils.clear_file('images.txt')


async def send_to_webhook(webhook_url):
    """
    This function sends files from a list of URLs to a Discord webhook.
    It takes input for webhook URL and reads the URLs from a file 'images.txt'.
    It then downloads each image, saves it to a file with a randomly generated name,
    sends it to the Discord webhook and clears the file 'images.txt'.
    """

    with open('images.txt', 'r', encoding='UTF-8') as f:
        async with aiohttp.ClientSession() as session:
            for line in f:
                async with session.get(line.strip()) as r:

                    if r.status == 200:

                        file_format = line.strip().split('.')[-1]
                        file_name = os.urandom(16).hex() + '.' + file_format
                        async with aiofiles.open(file_name, mode='wb') as f:
                            await f.write(await r.read())

                        try:
                            webhook = discord.Webhook.from_url(
                                webhook_url,
                                adapter=discord.AsyncWebhookAdapter(session),  # type: ignore
                            )
                            filename = os.urandom(16).hex()
                            await webhook.send(
                                file=discord.File(
                                    file_name,
                                    filename=f'{filename}.{file_format}',
                                )
                            )

                            os.remove(file_name)
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                            )
                        except discord.errors.HTTPException:
                            pass

    ConsoleUtils.clear_file('images.txt')


async def menu():

    ConsoleUtils.clear_console()

    print(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 1. Scrape Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 2. Send to Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 3. Send to Webhook\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 4. Scrape Category\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 5. Scrape Hentai (Reverse Lines based in number)\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 6. Credits\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 7. Exit'
    )

    while True:
        choice = input(
            f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Choice: '
        )

        if choice == '1':

            channel_id = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Channel ID: '
            )
            await scrape_channel(channel_id=channel_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Scraping Channel'
            )
            await asyncio.sleep(1)

        elif choice == '2':
            channel_id = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Channel ID: '
            )
            await send_to_channel(channel_id=channel_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Channel'
            )
            await asyncio.sleep(3)

        elif choice == '3':

            webhook_url = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Webhook URI: '
            )
            await send_to_webhook(webhook_url=webhook_url)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Webhook'
            )
            await asyncio.sleep(3)

        elif choice == '4':
            category_id = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Category ID: '
            )
            await scrape_category(category_id=category_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Scraping Category'
            )
            await asyncio.sleep(3)

        elif choice == '6':
            username = await client.fetch_user(793115273997451304)
            username = username.name
            discrim = await client.fetch_user(793115273997451304)
            discrim = discrim.discriminator

            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Credits:\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Made by: {{C.RESET}}{username}#{discrim}\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Github: {{C.RESET}}obstructive'
            )
            await asyncio.sleep(3)

        elif choice == '6':

            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Exiting...'
            )
            await asyncio.sleep(1)
            console_utils.clear_console()
            sys.exit()

        else:

            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Invalid Choice'
            )
            await asyncio.sleep(1)
            console_utils.clear_console()
            console_utils.clear_file('images.txt')
        await menu()


@client.event
async def on_ready():
    await menu()


client.run(token, reconnect=True)
