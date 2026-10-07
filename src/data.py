from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Table:
    headers: list[str]
    rows: list[list[str]]
    numeric_columns: list[int]


def number(value: str) -> float:
    return float(value.strip().replace(" ", "").replace("\u00a0", "").replace(",", "."))


def read_table(path: Path) -> Table:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        content = path.read_text(encoding="cp1251")

    lines = [line for line in content.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not lines:
        raise ValueError("Файл пуст или содержит только комментарии.")

    sample = "\n".join(lines[:10])
    if "\t" in sample:
        separator = "\t"
    elif ";" in sample:
        separator = ";"
    elif "," in sample:
        separator = ","
    else:
        separator = None

    if separator is None:
        parsed = [re.split(r"\s+", line.strip()) for line in lines]
    else:
        parsed = list(csv.reader(lines, delimiter=separator))
    parsed = [[cell.strip() for cell in row] for row in parsed]
    width = len(parsed[0])
    if width == 0 or any(len(row) != width for row in parsed):
        raise ValueError("Строки файла должны содержать одинаковое число столбцов.")

    def is_number(value: str) -> bool:
        try:
            number(value)
            return True
        except ValueError:
            return False

    has_header = any(not is_number(cell) for cell in parsed[0])
    headers = parsed[0] if has_header else [f"Столбец {i + 1}" for i in range(width)]
    rows = parsed[1:] if has_header else parsed
    if not rows:
        raise ValueError("В файле нет строк с данными.")
    numeric_columns = [
        index
        for index in range(width)
        if any(row[index] for row in rows)
        and all(not row[index] or is_number(row[index]) for row in rows)
    ]
    if not numeric_columns:
        raise ValueError("В файле нет числовых столбцов для построения графика.")
    return Table(headers, rows, numeric_columns)


