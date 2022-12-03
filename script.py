import asyncio
from aiohttp import ClientSession
from aiohttp_proxy import ProxyConnector
from fake_useragent import FakeUserAgent
from loguru import logger
from sys import stderr
from itertools import cycle
from time import sleep
from typing import Union


URL: str = "https://phantom.app/api/waitlist"

COUNT_OF_PROCESSES: int = 10
TIME_DELTA: int = 60
EMAILS_FILE_NAME: str = "emails.txt"
PROXIES_FILE_NAME: str = "proxies.txt"
OUTPUT_FILE_NAME: str = "output.txt"

logger.remove()
logger.add(stderr,
           format="<white>{time:HH:mm:ss}</white> | "
                  "<level>[{level}]</level> | "
                  "<white>{message}</white>")

headers = {
    "User-Agent": FakeUserAgent().random,
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://phantom.app",
    "Connection": "keep-alive",
    "Referer": "https://phantom.app/waitlist",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}


def get_file_data(file_name: str) -> list[str]:
    """Gets data from the file"""
    with open(file_name, "r") as file:
        return [line.rstrip() for line in file]


def save_email(email: str) -> None:
    """Save email to the file"""
    with open("output.txt", "a") as f:
        f.write(f"{email}\n")


async def get_request(email: str, proxy: Union[str, None] = None) -> bool:
    """Makes request to Phantom API"""
    async with ClientSession(headers=headers, connector=ProxyConnector.from_url(proxy)) as session:
        async with session.post(URL, json={"email": email}) as response:
            if response.status != 200:
                logger.error(await response.text())
                return False
            else:
                logger.success(f"{email} was successfully registered!")
                return True


if __name__ == "__main__":
    emails = get_file_data(EMAILS_FILE_NAME)
    proxies = get_file_data(PROXIES_FILE_NAME)

    for email, proxy in zip(emails, cycle(proxies)):
        if asyncio.run(get_request(email, proxy)):
            save_email(email)

        # counter += 1
        # if counter % len(proxies) == 0:
        #     sleep(TIME_DELTA)
        sleep(TIME_DELTA)
