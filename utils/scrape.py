import asyncio
import hashlib
import json
import os
import random
from typing import Set

import aiofiles
import aiohttp
from colorama import Fore
from discord import File, Webhook, errors


async def scrape_channel(client, channel_id, filename):
    ignored_keywords = set()
    with open('config.json', 'r') as f:
        config = json.load(f)
        ignored_keywords.update(config.get('ignored', []))

    async with aiofiles.open(filename, 'a', encoding='utf-8') as f:
        channel = await client.fetch_channel(channel_id)
        async with aiohttp.ClientSession() as session:
            async for message in channel.history(limit=None):
                for attachment in message.attachments:
                    url = attachment.url.lower()
                    if url.startswith('https://') and not any(
                        keyword in url for keyword in ignored_keywords
                    ):
                        async with session.head(url) as response:
                            content_type = response.headers.get(
                                'Content-Type', ''
                            )
                            if content_type.startswith(('image/', 'video/')):
                                await f.write(f'{url}\n')
                                print(
                                    f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {url}'
                                )

    async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
        lines = await f.readlines()
        random.shuffle(lines)

    async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
        await f.writelines(lines)


async def scrape_category(category_id, client):
    category = await client.fetch_channel(category_id)

    tasks = []
    for channel in category.channels:
        task = asyncio.create_task(
            scrape_channel(
                client=client,
                channel_id=channel.id,
                filename='data/images.txt',
            )
        )
        tasks.append(task)

    await asyncio.gather(*tasks)


async def send_to_channel(channel_id, client):
    channel = await client.fetch_channel(channel_id)

    async with aiofiles.open(
        'data/images.txt', 'r'
    ) as f, aiohttp.ClientSession() as session:
        async for line in f:
            async with session.get(line.strip()) as r:
                if r.status == 200:
                    file_format = line.strip().split('.')[-1]
                    file_name = f'{os.urandom(16).hex()}.{file_format}'
                    async with aiofiles.open(file_name, mode='wb') as file:
                        await file.write(await r.read())
                    try:
                        await channel.send(
                            file=File(file_name, filename=file_name)
                        )
                        os.remove(file_name)
                        print(
                            f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                        )
                    except errors.HTTPException:
                        pass

    # Clear the contents of the file after sending all images
    async with aiofiles.open('data/images.txt', 'w'):
        pass


async def purge_duplicates(channel_id: int, client) -> None:
    channel = await client.fetch_channel(channel_id)

    processed_hashes: Set[str] = set()
    messages_to_delete = []

    async for message in channel.history(limit=None):
        attachments_to_delete = []
        for attachment in message.attachments:
            async with aiohttp.ClientSession() as session, session.get(
                attachment.url
            ) as r:
                if r.status == 200:
                    file = await r.read()
                    hash = hashlib.md5(file).hexdigest()
                    if hash in processed_hashes:
                        attachments_to_delete.append(attachment)
                    else:
                        processed_hashes.add(hash)
        if attachments_to_delete:
            messages_to_delete.append(message)

    if messages_to_delete:
        await channel.delete_messages(messages_to_delete)
        print(f'{len(messages_to_delete)} messages deleted')


async def send_to_webhook(webhook_url: str, client) -> None:
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, client=client)
        async with aiofiles.open(
            'data/images.txt', 'r', encoding='UTF-8'
        ) as f:
            async for line in f:
                async with session.get(line.strip()) as r:
                    if r.status == 200:
                        file_format = line.strip().split('.')[-1]
                        file_name = os.urandom(16).hex() + '.' + file_format
                        async with aiofiles.open(file_name, mode='wb') as file:
                            await file.write(await r.read())
                        try:
                            filename = os.urandom(16).hex()
                            await webhook.send(
                                file=File(
                                    file_name,
                                    filename=f'{filename}.{file_format}',
                                )
                            )
                            os.remove(file_name)
                            print(
                                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} {line.strip()}'
                            )
                        except errors.HTTPException:
                            pass
