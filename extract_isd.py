"""
extract_isd.py
Extracts API name and input parameters from an ISD .docx file.

API name  → segment between underscores immediately before "_ISD" in the filename
            e.g.  ESB_GetCabinetInterfaces_ISD_V1.docx  →  GetCabinetInterfaces

Parameters → tried in this order:
  1. Table form   – row whose first cell = "Input Parameters" / "Input Parameter";
                    subsequent rows whose first cell is not a column header or new
                    section heading are the parameter names.
  2. MessageBody  – scan every cell/paragraph for  MessageBody/<name>  patterns,
                    collect in order of first appearance (deduplicated).
"""

import os
import re
from typing import Tuple, List

from docx import Document


# ---------------------------------------------------------------------------
# public API
# ---------------------------------------------------------------------------

def extract_from_isd(path: str) -> Tuple[str, List[str]]:
    """Return (api_name, [param1, param2, ...]) from an ISD .docx file.

    Raises ValueError if the API name cannot be detected from the filename.
    Returns an empty params list (with a warning printed) if no parameters
    are found — the caller decides whether to block or warn.
    """
    api_name = _api_name_from_filename(path)
    params   = _params_from_docx(path)
    return api_name, params


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _api_name_from_filename(path: str) -> str:
    basename = os.path.basename(path)
    m = re.search(r'_([A-Za-z0-9]+)_ISD', basename, re.IGNORECASE)
    if not m:
        raise ValueError(
            f"Cannot detect API name — filename does not match "
            f"*_<ApiName>_ISD*.docx\nGot: {basename}"
        )
    return m.group(1)


_SKIP_FIRST_CELLS = frozenset({"parameter", "name", "field", "type", "mandatory",
                                "description", "direction", "remarks"})
_STOP_FIRST_CELLS = frozenset({"output parameter", "output parameters",
                                "header", "fault", "request", "response body",
                                "response", "output", "notes", "remarks"})


def _params_from_docx(path: str) -> List[str]:
    doc = Document(path)
    params = _try_table_form(doc.tables)
    if not params:
        params = _try_messagebody_form(doc)
    if not params:
        print("WARNING: no input parameters found in ISD — "
              "please verify the parameter list manually.")
    return params


def _try_table_form(tables) -> List[str]:
    params: List[str] = []
    for table in tables:
        in_section = False
        for row in table.rows:
            cells = [c.text.strip() for c in row.cells]
            if not cells:
                continue
            first = cells[0].strip()
            first_lower = first.lower()

            # Detect section header
            if first_lower in ("input parameters", "input parameter"):
                in_section = True
                continue

            if not in_section:
                continue

            # Stop at next section
            if first_lower in _STOP_FIRST_CELLS:
                break

            # Skip column-header rows
            if first_lower in _SKIP_FIRST_CELLS:
                continue

            # Skip empty first cell or merged/spanning rows
            if not first or first_lower.startswith("output"):
                break

            if first not in params:
                params.append(first)

    return params


def _try_messagebody_form(doc) -> List[str]:
    full_text = "\n".join(p.text for p in doc.paragraphs)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                full_text += "\n" + cell.text

    matches = re.findall(r'MessageBody/([A-Za-z0-9_]+)', full_text)
    seen: set = set()
    params: List[str] = []
    for name in matches:
        if name not in seen:
            seen.add(name)
            params.append(name)
    return params
