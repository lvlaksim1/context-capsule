"""Central GitHub service contracts: safe repository paths and schema checks."""
from __future__ import annotations

import datetime as dt
import json
import re
import stat
from pathlib import Path, PurePosixPath

BEGIN = "<!-- context-capsule:begin -->"
END = "<!-- context-capsule:end -->"


def safe_path(root: Path, relative: str, *, exists: bool = False, directory: bool = False) -> Path:
    if not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative:
        raise ValueError(f"invalid repository path: {relative!r}")
    parts = PurePosixPath(relative).parts
    if not parts or relative.startswith("/") or any(p in ("..", ".git") for p in parts):
        raise ValueError(f"path must stay inside the repository: {relative}")
    root = root.resolve()
    candidate = root
    for part in parts:
        candidate = candidate / part
        try:
            mode = candidate.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlink is not allowed in a context path: {relative}")
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise ValueError(f"special file is not allowed: {relative}")
    candidate.resolve().relative_to(root)
    if exists and not (candidate.is_dir() if directory else candidate.is_file()):
        raise ValueError(f"missing {'directory' if directory else 'file'}: {relative}")
    return candidate


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path.name}")
    return value


def schema_errors(value, schema: dict, label: str = "$", *, definitions: bool = True) -> list[str]:
    """Execute every keyword used by our schemas; fail on unsupported vocabulary.

    This is intentionally not a general-purpose Draft 2020-12 implementation.
    Adding a schema keyword requires adding and testing its implementation here.
    """
    supported = {"$schema", "$id", "title", "description", "default", "type", "required",
                 "properties", "additionalProperties", "items", "minLength", "pattern",
                 "format", "const", "enum", "minimum", "minItems", "maxItems"}
    unknown = set(schema) - supported
    if unknown:
        raise ValueError(f"unsupported schema keywords: {sorted(unknown)}")
    if definitions:
        for child in schema.get("properties", {}).values():
            schema_errors(None, child)
        for key in ("items", "additionalProperties"):
            if isinstance(schema.get(key), dict):
                schema_errors(None, schema[key])
    errors = []
    types = {"object": dict, "array": list, "string": str, "boolean": bool,
             "integer": int, "number": (int, float), "null": type(None)}
    expected = schema.get("type")
    if expected and (not isinstance(value, types[expected]) or
                     (expected in ("integer", "number") and isinstance(value, bool))):
        return [f"{label}: expected {expected}"]
    if "const" in schema and (type(value) is not type(schema["const"]) or value != schema["const"]):
        errors.append(f"{label}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{label}: unsupported value {value!r}")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{label}: missing {key}")
        properties = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                errors.extend(schema_errors(item, properties[key], f"{label}.{key}"))
            elif extra is False:
                errors.append(f"{label}: unexpected {key}")
            elif isinstance(extra, dict):
                errors.extend(schema_errors(item, extra, f"{label}.{key}"))
    if isinstance(value, list):
        if len(value) < schema.get("minItems", 0) or len(value) > schema.get("maxItems", float("inf")):
            errors.append(f"{label}: array length outside permitted range")
        for i, item in enumerate(value):
            if "items" in schema:
                errors.extend(schema_errors(item, schema["items"], f"{label}[{i}]"))
    if isinstance(value, str):
        if len(value) < schema.get("minLength", 0):
            errors.append(f"{label}: string is too short")
        if "pattern" in schema and re.search(schema["pattern"], value) is None:
            errors.append(f"{label}: invalid string format")
        if "format" in schema:
            try:
                if schema["format"] == "date":
                    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                        raise ValueError()
                    dt.date.fromisoformat(value)
                elif schema["format"] == "date-time":
                    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
                    if parsed.tzinfo is None:
                        raise ValueError()
                else:
                    raise ValueError(f"unsupported format: {schema['format']}")
            except ValueError:
                errors.append(f"{label}: invalid {schema['format']}")
    if isinstance(value, (int, float)) and "minimum" in schema and value < schema["minimum"]:
        errors.append(f"{label}: below minimum")
    return errors


def managed_block(text: str) -> str | None:
    if BEGIN not in text and END not in text:
        return None
    if text.count(BEGIN) != 1 or text.count(END) != 1 or text.index(END) < text.index(BEGIN):
        raise ValueError("malformed or duplicate Context Capsule managed block")
    return text[text.index(BEGIN):text.index(END) + len(END)]
