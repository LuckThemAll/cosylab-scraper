import xlsxwriter

from typing import Dict


def initialize_xlsx():
    workbook = xlsxwriter.Workbook("Result.xlsx")
    worksheet = workbook.add_worksheet("Result")

    return workbook, worksheet


def add_headers(worksheet):
    headers = [
        "Title",
        "Country",
        "Region",
        "Ingredients",
    ]

    row = 0
    [worksheet.write(row, col, item) for col, item in enumerate(headers)]

    row += 1
    col = 0

    return row, col


def write_row(worksheet, data: Dict, row: int, col: int):
    data = [
        data["title"],
        data["country"],
        data["region"],
        "\n".join(data["ingredients"]),
    ]

    for fields in data:
        worksheet.write(row, col, fields)
        col += 1
    col = 0
    row += 1

    return row, col


def close_workbook(workbook):
    workbook.close()
