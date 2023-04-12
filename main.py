import hashlib
import os
import sys
from typing import Set
import discord
import aiohttp
import aiofiles
import random
import asyncio
from colorama import init, Fore
from utils.console import ConsoleUtils

console_utils = ConsoleUtils()
init(autoreset=True)

console_utils.clear_file('data/images.txt')
console_utils.delete_files(confirm=True)
console_utils.set_console_title('discord img scraper | by @obstructive')
console_utils.clear_console()

try:
    with open('data/token.txt', 'r') as f:
        token = f.read().strip()
except FileNotFoundError:
    token = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter your token: '
    )
    with open('data/token.txt', 'w') as f:
        f.write(token)

client = discord.Client()


async def scrape_channel(
    client: discord.Client,
    channel_id: int,
    filename: str,
    ignored_keywords: str,
) -> None:
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
        }

    channel = await client.fetch_channel(channel_id)
    async with aiohttp.ClientSession() as session:
        async for message in channel.history(limit=None):
            for attachment in message.attachments:
                url = attachment.url.lower()
                if (
                    url.startswith('https://')
                    and url.endswith(
                    tuple(valid_extensions)
                )
                    and not any(keyword in url for keyword in ignored_keywords)
                ):
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
    category = await client.fetch_channel(category_id)

    tasks = []
    for channel in category.channels:
        task = asyncio.create_task(
            scrape_channel(
                client, channel.id, 'data/images.txt', 'data/ignored.txt'
            )
        )
        tasks.append(task)

    await asyncio.gather(*tasks)


async def send_to_channel(channel_id):
    """
    This function sends files from a list of URLs to a Discord channel.
    It takes input for channel ID and reads the URLs from a file 'data/images.txt'.
    It then downloads each image, saves it to a file with a randomly generated name,
    sends it to the Discord channel and clears the file 'data/images.txt'.
    """

    # Fetch the channel from the given ID
    channel = await client.fetch_channel(channel_id)

    # Read URLs from 'data/images.txt' and download each image
    async with aiofiles.open('data/images.txt', 'r') as f:
        async with aiohttp.ClientSession() as session:
            async for line in f:
                async with session.get(line.strip()) as r:
                    # Check if the request is successful
                    if r.status == 200:
                        # Save the file with a randomly generated name
                        file_format = line.strip().split('.')[-1]
                        file_name = os.urandom(16).hex() + '.' + file_format
                        async with aiofiles.open(file_name, mode='wb') as f:
                            await f.write(await r.read())
                        # Try sending the file to the channel
                        try:
                            await channel.send(
                                file=discord.File(
                                    file_name, filename=file_name
                                )
                            )
                            # Remove the file if it has been sent successfully
                            os.remove(file_name)
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                            )
                        except discord.errors.HTTPException:
                            pass

    # Clear the file 'data/images.txt' after all files have been processed
    async with aiofiles.open('data/images.txt', 'w'):
        pass


async def purge_duplicates(channel_id: int) -> None:
    """
    This function removes duplicate files from a discord channel and deletes them from the server.

    Args:
        channel: A TextChannel object representing the channel to be cleaned.
    """

    channel = await client.fetch_channel(channel_id)

    # Create a set to store the md5 hashes of attachments that have already been processed
    processed_hashes: Set[str] = set()

    # Iterate over all messages in the channel
    async for message in channel.history(limit=None):
        for attachment in message.attachments:
            # Download the attachment using aiohttp and calculate its md5 hash
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as r:
                    if r.status == 200:
                        file = await r.read()
                        hash = hashlib.md5(file).hexdigest()

                        # If the hash is already in the set of processed hashes, delete the message
                        if hash in processed_hashes:
                            await message.delete()
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}-{Fore.MAGENTA}]{Fore.RESET} {attachment.url}'
                            )

                        # Otherwise, add the hash to the set of processed hashes
                        else:
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}+{Fore.MAGENTA}]{Fore.RESET} {attachment.url}'
                            )
                            processed_hashes.add(hash)


async def send_to_webhook(webhook_url: str) -> None:
    """
    This function sends files from a list of URLs to a Discord webhook.
    It takes input for webhook URL and reads the URLs from a file 'data/images.txt'.
    It then downloads each image, saves it to a file with a randomly generated name,
    sends it to the Discord webhook and clears the file 'data/images.txt'.
    """

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            webhook_url, adapter=discord.AsyncWebhookAdapter(session)
        )

        with open('data/images.txt', 'r', encoding='UTF-8') as f:
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

    ConsoleUtils.clear_file('data/images.txt')


async def menu():

    ConsoleUtils.clear_console()

    print(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 1. Scrape Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 2. Scrape Category\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 3. Send to Channel\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 4. Send to Webhook\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 5. Purge Duplicates\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 6. Credits\n'
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} 7. Exit'
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
                filename='data/images.txt',
                client=client,
                ignored_keywords='data/ignored.txt',
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
            channel_id = int(
                input(
                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Channel ID: '
                )
            )
            await purge_duplicates(channel_id=channel_id)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Purging Duplicates'
            )
            await asyncio.sleep(3)

        elif choice == '6':

            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Credits:\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Made by: {{C.RESET}}igna\n'
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Github: {{C.RESET}}obstructive'
            )
            await asyncio.sleep(3)

        elif choice == '7':

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


client.run(token)
