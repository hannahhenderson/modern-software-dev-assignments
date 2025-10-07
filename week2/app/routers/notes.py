from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

from .. import db


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("")
def create_note(payload: Dict[str, Any]) -> Dict[str, Any]:
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=400, detail="content is required")
    note_id = db.insert_note(content)
    note = db.get_note(note_id)
    return {
        "id": note["id"],
        "content": note["content"],
        "created_at": note["created_at"],
    }


@router.get("/{note_id}")
def get_single_note(note_id: int) -> Dict[str, Any]:
    row = db.get_note(note_id)
    if row is None:
        raise HTTPException(status_code=404, detail="note not found")
    return {"id": row["id"], "content": row["content"], "created_at": row["created_at"]}

# Class notes

# You're going to use the tools that you set up in the coding agent
# FastMCP makes your life easier
# you're going to want to use cursor
# expose the MCP&Integrations tab

# "SimpleMCPTestServer": {
#     "command": "",
#     "args": ""
# }

# Prompt: read the pyproject.toml using the simple mcp test server
#   LLM gets confused when there are too many tools within a server
#   This is likely a Cursor limit
#       Gets confused in the 10s of tools, somewhere between 30 and 100
#       the clearer the boundaries between tools 
# Is MCP only on the pro version of Cursor? Sounds like it's not gated
