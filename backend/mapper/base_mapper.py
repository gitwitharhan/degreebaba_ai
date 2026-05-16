from __future__ import annotations

from backend.mapper.html_inference import build_payload_from_flat


class MappingBuilder:
    def __init__(self, schema_fields: list[dict], schema_document: dict) -> None:
        self._schema_fields = schema_fields
        self._schema_document = schema_document
        self.values = {
            field["name"]: ([] if field["type"] == "repeater" else None)
            for field in schema_fields
        }
        self.metadata = {
            field["name"]: {
                "type": field["type"],
                "source": None,
                "mapped": False,
                "required": field.get("required", False),
                "score": 0.0,
                "resolver": "deterministic",
            }
            for field in schema_fields
        }

    def set(self, path: str, value, source: str | None = None, score: float = 1.0) -> None:
        if path not in self.values:
            return
        self.values[path] = value
        self.metadata[path] = {
            **self.metadata[path],
            "source": source,
            "mapped": self._has_value(value),
            "score": round(score, 2),
        }

    def build_payload(self) -> dict:
        return build_payload_from_flat(self._schema_document, self.values)

    @staticmethod
    def _has_value(value) -> bool:
        if isinstance(value, list):
            return len(value) > 0
        return value is not None and str(value).strip() != ""
