from __future__ import annotations

import re


def table_to_repeater(table: list[list[str]], child_fields: list[str]) -> list[dict]:
    if not table:
        return []

    headers = [_slug(cell) for cell in table[0]]
    rows = [row for row in table[1:] if any(cell.strip() for cell in row)]
    output = []

    for row in rows:
        item = {}
        for index, child in enumerate(child_fields):
            child_slug = _slug(child)
            header_index = next(
                (i for i, header in enumerate(headers) if child_slug in header or header in child_slug),
                index,
            )
            item[child] = row[header_index].strip() if header_index < len(row) and row[header_index].strip() else None
        output.append(item)

    return output


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
