import asyncio
import sys

import discord
import orjson
from colorama import Fore, init

from utils.console import ConsoleUtils
from utils.scrape import *

console_utils = ConsoleUtils()
init(autoreset=True)

console_utils.clear_file('data/images.txt')
console_utils.purge_directory('data/images')
console_utils.set_console_title('discord img scraper | by @obstructive')
console_utils.clear_console()
try:
    with open('data/config.json', 'r') as f:
        config = orjson.loads(f.read())
        token = config.get('token')
        if not token:
            raise FileNotFoundError
except FileNotFoundError:
    token = input(
        f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter your token: '
    )
    config['token'] = token
    with open('data/config.json', 'w') as f:

        f.write(orjson.dumps(config, option=orjson.OPT_INDENT_2).decode())
client = discord.Client()


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
                client=client,
                channel_id=channel_id,
                filename='data/images.txt',
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

            await send_to_channel(channel_id=channel_id, client=client)
            print(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Finished Sending Scraped attachments to Channel'
            )
            await asyncio.sleep(3)

        elif choice == '4':

            webhook_url = input(
                f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Enter Webhook Url: '
            )
            await send_to_webhook(webhook_url=webhook_url, client=client)
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
            await scrape_category(category_id=category_id, client=client)
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
            await purge_duplicates(channel_id=channel_id, client=client)
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
        ConsoleUtils.purge_directory('data/images')
        ConsoleUtils.clear_file('data/images.txt')


@client.event
async def on_ready():
    await menu()


if __name__ == '__main__':
    try:
        client.run(token, reconnect=True)
    except discord.errors.LoginFailure:
        token = input(
            f'{Fore.MAGENTA}[{Fore.RESET}~{Fore.MAGENTA}]{Fore.RESET} Invalid Token, Enter your token: '
        )
        config['token'] = token
        with open('data/config.json', 'w') as f:

            f.write(orjson.dumps(config, option=orjson.OPT_INDENT_2).decode())
        client.run(token, reconnect=True)
