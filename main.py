import multiprocessing

import requests
import json
import xlsx_writer

from bs4 import BeautifulSoup

BASE_URL = 'https://cosylab.iiitd.edu.in/recipedb/search_recipe'


def internet_resource_getter(page):
    stuff_got = []
    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        response = requests.post(BASE_URL, headers=headers, data=f"page={page}", timeout=15)
        stuff_got.append(response.content)
    except:
        print(f'Error occured while getting content for page {page}')
        stuff_got.append(None)
    return stuff_got


def process_page(page_content):
    parser = BeautifulSoup(page_content, 'html.parser')
    result = []
    for button in parser.find_all('button', class_='btn-small waves-effect waves-light modal-trigger'):
        json_data = button['onclick'].replace('handleInfoClick(', '')[:-1]
        obj = json.loads(json_data)
        result.append({
            'title': obj['Recipe_title'],
            'country': obj['Sub_region'],
            'region': obj['Region'],
            'ingredients': [ingredient['ingredient_name'] for ingredient in obj['Ingredients']],
        })

    return result


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def scrape():
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    first_page = requests.post(BASE_URL, data='page=2', headers=headers)
    page_content = BeautifulSoup(first_page.content, 'html.parser')

    workbook, worksheet = xlsx_writer.initialize_xlsx()

    data = process_page(first_page.content)
    row, col = xlsx_writer.add_headers(worksheet)
    for data_item in data:
        row, col = xlsx_writer.write_row(worksheet, data_item, row, col)

    last_page = int(page_content.find('li', id='seventh').find('a').text)

    for chunk, pages in enumerate(chunks([i for i in range(2, last_page + 1)], 8)):
        print(f"Processing page {chunk * 8}")
        pool = multiprocessing.Pool(processes=8)
        pool_outputs = pool.map(internet_resource_getter, pages)
        pool.close()
        pool.join()

        for pool_output in pool_outputs:
            if pool_output[0] is None:
                continue
            data = process_page(pool_output[0])
            for data_item in data:
                row, col = xlsx_writer.write_row(worksheet, data_item, row, col)

    xlsx_writer.close_workbook(workbook)


if __name__ == '__main__':
    scrape()
