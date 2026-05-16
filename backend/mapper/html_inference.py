from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any


SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "html_templates"


class HeadingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._capture = False
        self._buffer: list[str] = []
        self.headings: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"h1", "h2", "h3", "h4"}:
            self._capture = True
            self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h1", "h2", "h3", "h4"} and self._capture:
            heading = re.sub(r"\s+", " ", "".join(self._buffer)).strip()
            if heading:
                self.headings.append(heading)
            self._capture = False

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._buffer.append(data)


def load_schema_document(page_type: str):
    path = SCHEMA_DIR / f"{page_type}_schema.json"
    return json.loads(path.read_text())


def load_schema(page_type: str) -> list[dict]:
    document = load_schema_document(page_type)
    if isinstance(document, list):
        return document
    return flatten_schema(document)


def flatten_schema(schema_document: dict) -> list[dict]:
    fields: list[dict] = []
    root_name, root_node = _schema_root(schema_document)
    initial_path = (root_name,) if root_name else ()
    _flatten_node(root_name, root_node, fields, parent_path=initial_path)
    return fields


def infer_template_sections(page_type: str) -> list[str]:
    folder = TEMPLATE_DIR / page_type
    headings: list[str] = []
    for html_file in folder.glob("*.html"):
        parser = HeadingParser()
        parser.feed(html_file.read_text(errors="ignore"))
        headings.extend(parser.headings)
    return headings


def inferred_fields(page_type: str):
    document = load_schema_document(page_type)
    template_sections = infer_template_sections(page_type)

    if isinstance(document, list):
        return {
            field["name"]: {
                "type": field["type"],
                "required": field.get("required", False),
                "source_section": field.get("section"),
                "repeater_fields": field.get("children"),
            }
            for field in document
        } | {"_template_sections": template_sections}

    return {
        "schema": document,
        "flat_fields": {
            field["name"]: {
                "type": field["type"],
                "required": field.get("required", False),
                "source_section": field.get("section"),
                "repeater_fields": field.get("children"),
                "schema_path": field.get("schema_path"),
            }
            for field in flatten_schema(document)
        },
        "_template_sections": template_sections,
    }


def build_payload_from_flat(schema_document: dict, flat_values: dict[str, Any]) -> dict:
    root_name, root_node = _schema_root(schema_document)
    shaped = _build_node(root_node, flat_values, (root_name,) if root_name else ())
    if root_name is None:
        return shaped
    return {root_name: shaped}


def _flatten_node(section_name: str | None, node: dict, fields: list[dict], parent_path: tuple[str, ...]) -> None:
    for field_name, value in node.items():
        field_path = parent_path + (field_name,)
        path_name = ".".join(field_path)
        section_label = _humanize(parent_path[0] if parent_path else section_name or field_name)
        aliases = [_humanize(field_name)]
        if parent_path:
            aliases.append(_humanize(parent_path[-1]))
        if section_name:
            aliases.append(_humanize(section_name))

        if isinstance(value, str):
            fields.append(
                {
                    "name": path_name,
                    "leaf_name": field_name,
                    "type": value,
                    "required": False,
                    "section": section_label,
                    "aliases": aliases,
                    "schema_path": path_name,
                }
            )
            continue

        if not isinstance(value, dict):
            continue

        field_type = value.get("type")
        field_children = value.get("fields")

        if field_type == "repeater" and isinstance(field_children, dict):
            fields.append(
                {
                    "name": path_name,
                    "leaf_name": field_name,
                    "type": "repeater",
                    "required": False,
                    "section": section_label,
                    "children": list(field_children.keys()),
                    "aliases": aliases,
                    "schema_path": path_name,
                }
            )
            continue

        if field_type and field_children is None:
            fields.append(
                {
                    "name": path_name,
                    "leaf_name": field_name,
                    "type": field_type,
                    "required": False,
                    "section": section_label,
                    "aliases": aliases,
                    "schema_path": path_name,
                }
            )
            continue

        _flatten_node(field_name, value, fields, field_path)


def _schema_root(schema_document: dict) -> tuple[str | None, dict]:
    if len(schema_document) == 1:
        root_name, root_node = next(iter(schema_document.items()))
        if isinstance(root_node, dict) and root_name.endswith("_schema"):
            return None, root_node
    return None, schema_document


def _build_node(node: Any, flat_values: dict[str, Any], parent_path: tuple[str, ...]):
    if isinstance(node, str):
        return flat_values.get(".".join(parent_path))

    if not isinstance(node, dict):
        return None

    field_type = node.get("type")
    field_children = node.get("fields")
    if field_type == "repeater" and isinstance(field_children, dict):
        return flat_values.get(".".join(parent_path), [])

    if field_type and field_children is None:
        return flat_values.get(".".join(parent_path))

    output = {}
    for child_name, child_value in node.items():
        output[child_name] = _build_node(child_value, flat_values, parent_path + (child_name,))
    return output


def _humanize(value: str) -> str:
    return value.replace("_", " ").strip().title()
