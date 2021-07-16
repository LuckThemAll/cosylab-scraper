import asyncio
import aiohttp
import requests
import json
import xlsx_writer

from bs4 import BeautifulSoup

BASE_URL = "https://cosylab.iiitd.edu.in/recipedb/search_recipe"
headers = {"Content-Type": "application/x-www-form-urlencoded"}


async def get(page, session):
    print(f"Processing page {page}")
    try:
        async with session.post(
            url=BASE_URL, data=f"page={page}", headers=headers, timeout=20
        ) as response:
            return await response.read()
    except:
        print(f"Unable to get page {page}")
        return None


async def async_requests(pages):
    async with aiohttp.ClientSession() as session:
        return await asyncio.gather(*[get(page, session) for page in pages])


def process_page(page_content):
    parser = BeautifulSoup(page_content, "html.parser")
    result = []
    for button in parser.find_all(
        "button", class_="btn-small waves-effect waves-light modal-trigger"
    ):
        json_data = button["onclick"].replace("handleInfoClick(", "")[:-1]
        obj = json.loads(json_data)
        result.append(
            {
                "title": obj["Recipe_title"],
                "country": obj["Sub_region"],
                "region": obj["Region"],
                "ingredients": [
                    ingredient["ingredient_name"] for ingredient in obj["Ingredients"]
                ],
            }
        )

    return result


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def scrape():
    first_page = requests.post(BASE_URL, data="page=1", headers=headers)
    page_content = BeautifulSoup(first_page.content, "html.parser")

    workbook, worksheet = xlsx_writer.initialize_xlsx()

    data = process_page(first_page.content)
    row, col = xlsx_writer.add_headers(worksheet)
    for data_item in data:
        row, col = xlsx_writer.write_row(worksheet, data_item, row, col)

    last_page = int(page_content.find("li", id="seventh").find("a").text)

    for chunk, pages in enumerate(chunks([i for i in range(2, last_page + 1)], 8)):
        pages_result = asyncio.run(async_requests(pages))
        for page_result in pages_result:
            if page_result is not None:
                data = process_page(page_result)
                for data_item in data:
                    row, col = xlsx_writer.write_row(worksheet, data_item, row, col)

    xlsx_writer.close_workbook(workbook)


if __name__ == "__main__":
    scrape()
