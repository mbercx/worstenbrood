"""JSON output parser."""

from __future__ import annotations

import json
from typing import Any, cast

from dough.outputs.parsers.base import BaseOutputFileParser


class JSONParser(BaseOutputFileParser):
    """Parse a JSON file into a Python dict."""

    @staticmethod
    def parse(content: str) -> dict[str, Any]:
        return cast(dict[str, Any], json.loads(content))
