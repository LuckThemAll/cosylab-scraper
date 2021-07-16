import asyncio
import aiohttp


async def get(url, session):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    try:
        async with session.post(url, data="page=", headers=headers) as response:
            return await response.read()
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))

        return None


async def async_requests(urls):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[get(url, session) for url in urls])