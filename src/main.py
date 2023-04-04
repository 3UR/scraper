import os
import sys
import selfcord as discord
import aiohttp
import aiofiles
import random
import asyncio
from colorama import init, Fore


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
        Deletes a subset of files that start with 'file' from the current directory.

        Args:
            confirm: A boolean indicating whether to ask for confirmation before deleting the files.

        Returns:
            None
        """
        for file in os.listdir():
            if file.startswith('file'):
                if confirm:
                    response = input(
                        f'Are you sure you want to delete {file}? (y/n) '
                    )
                    if response.lower() != 'y':
                        continue
                os.remove(file)


console_utils = ConsoleUtils()
init(autoreset=True)

console_utils.clear_file('images.txt')
console_utils.delete_files(confirm=True)
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

__client__ = discord.Client()


async def scrape_channel(
    client: discord.Client,
    channel_id: int,
    filename: str,
    ignored_keywords: str,
) -> None:
    """
    Scrapes a Discord channel for image and video attachments and saves their URLs to a text file.

    Args:
        client: A Discord client object used to fetch the channel.
        channel_id: An integer representing the ID of the channel to scrape.
        filename: A string representing the name of the file to save the URLs to.
        ignored_keywords: A string representing the name of the file containing keywords to ignore.

    Returns:
        None
    """
    valid_extensions = {
        '.png',
        '.jpg',
        '.jpeg',
        '.mp4',
        '.webm',
        '.mov',
    }

    async with aiofiles.open(ignored_keywords, 'r', encoding='utf-8') as f:
        ignored_keywords = {
            line.strip().lower() for line in await f.readlines()
        }  # type: ignore

    channel = await client.fetch_channel(channel_id)
    async with aiohttp.ClientSession() as session:
        async for message in channel.history(limit=None):  # type: ignore
            for attachment in message.attachments:
                url = attachment.url.lower()
                if url.startswith('https://') and url.endswith(
                    tuple(valid_extensions)
                ):
                    if not any(keyword in url for keyword in ignored_keywords):
                        async with session.head(url) as response:
                            content_type = response.headers.get(
                                'Content-Type', ''
                            )
                            if content_type.startswith(('image/', 'video/')):
                                async with aiofiles.open(
                                    filename, 'a', encoding='utf-8'
                                ) as f:
                                    await f.write(f'{url}\n')
                                print(
                                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {url}'
                                )

    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        lines = await f.readlines()
        random.shuffle(lines)

    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.writelines(lines)


async def scrape_category(category_id: int) -> None:
    """
    Scrapes a Discord category for image and video attachments and saves their URLs to a text file.

    Args:
        category_id (int): The ID of the Discord category to scrape.

    Returns:
        None
    """
    category = await __client__.fetch_channel(category_id)

    tasks = []
    for channel in category.channels:  # type: ignore
        task = asyncio.create_task(
            scrape_channel(__client__, channel.id, 'images.txt', 'ignored.txt')
        )
        tasks.append(task)

    await asyncio.gather(*tasks)


async def send_to_channel(channel_id: int) -> None:
    """
    This function sends a file from a URL to a Discord channel.
    It takes input for channel ID and reads the URL from a file 'image.txt'.
    It then downloads the image, saves it to a file with a randomly generated name,
    sends it to the Discord channel and clears the file 'image.txt'.
    """
    channel = await __client__.fetch_channel(channel_id)

    async with aiohttp.ClientSession() as session:
        async with aiofiles.open('images.txt', 'r', encoding='utf-8') as f:
            for line in await f.readlines():
                line = line.strip()
            async with session.get(line) as response:
                if response.status != 200:
                    return

                file_format = line.split('.')[-1]
                file_name = os.urandom(16).hex() + '.' + file_format

                async with aiofiles.open(file_name, mode='wb') as file:
                    await file.write(await response.read())

                try:
                    await channel.send(
                        file=discord.File(file_name)
                    )   # type: ignore

                    os.remove(file_name)
                    print(
                        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line}'
                    )
                except discord.errors.HTTPException:
                    pass

        async with aiofiles.open('images.txt', 'w', encoding='utf-8') as f:
            await f.truncate(0)


async def send_to_webhook(webhook_url: str) -> None:
    """
    This function sends files from a list of URLs to a Discord webhook.
    It takes input for webhook URL and reads the URLs from a file 'images.txt'.
    It then downloads each image, saves it to a file with a randomly generated name,
    sends it to the Discord webhook and clears the file 'images.txt'.
    """

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            webhook_url, adapter=discord.AsyncWebhookAdapter(session)
        )

        with open('images.txt', 'r', encoding='UTF-8') as f:
            for line in f:
                async with session.get(line.strip()) as r:

                    if r.status == 200:
                        file_format = line.strip().split('.')[-1]
                        file_name = os.urandom(16).hex() + '.' + file_format
                        async with aiofiles.open(file_name, mode='wb') as file:
                            await file.write(await r.read())

                        try:
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
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 2. Scrape Category\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 3. Send to Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 4. Send to Webhook\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 5. Credits\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 6. Exit'
    )

    while True:
        choice = input(
            f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Choice: '
        )

        if choice == '1':

            channel_id = int(
                input(
                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Channel ID: '
                )
            )

            await scrape_channel(
                channel_id=channel_id,
                filename='images.txt',
                client=__client__,
                ignored_keywords='ignored.txt',
            )
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Scraping Channel'
            )
            await asyncio.sleep(1)

        elif choice == '3':
            channel_id = int(
                input(
                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Channel ID: '
                )
            )

            await send_to_channel(channel_id=channel_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Channel'
            )
            await asyncio.sleep(3)

        elif choice == '4':

            webhook_url = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Webhook Url: '
            )
            await send_to_webhook(webhook_url=webhook_url)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Webhook'
            )
            await asyncio.sleep(3)

        elif choice == '2':
            category_id = int(
                input(
                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Category ID: '
                )
            )
            await scrape_category(category_id=category_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Scraping Category'
            )
            await asyncio.sleep(3)

        elif choice == '5':

            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Credits:\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Made by: {{C.RESET}}igna\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Github: {{C.RESET}}obstructive'
            )
            await asyncio.sleep(3)

        elif choice == '6':

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


@__client__.event
async def on_ready():
    await menu()


__client__.run(token, reconnect=True)
