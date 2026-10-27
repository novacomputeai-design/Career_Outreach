"""Typed and schema-checked handoff boundary between research and report.

Schema validates structure, NOT whether live source claims are truthful.
"""
import json
from functools import lru_cache
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker

SCHEMA=Path(__file__).resolve().parents[1]/"schemas"/"source-corroborated-prospect.schema.json"

@lru_cache(maxsize=1)
def validator():
    data=json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(data)
    return Draft202012Validator(data,format_checker=FormatChecker())

def validate_prospect(prospect):
    errors=sorted(validator().iter_errors(prospect),key=lambda e:list(map(str,e.path)))
    return ["/".join(map(str,e.absolute_path))+": "+e.message for e in errors]
