"""MongoDB index definitions — centralized for clarity and scripting.

These are also applied at startup via `ensure_indexes()` in mongodb.py,
but this module provides a declarative reference and can be used by
migration scripts.
"""
from __future__ import annotations

from pymongo import ASCENDING, DESCENDING, IndexModel

# ---------- Index definitions per collection ----------

USERS_INDEXES = [
    IndexModel([("email", ASCENDING)], unique=True, name="uniq_email"),
    IndexModel([("created_at", DESCENDING)], name="users_created"),
]

FILES_INDEXES = [
    IndexModel([("user_id", ASCENDING), ("status", ASCENDING)], name="files_user_status"),
    IndexModel([("created_at", DESCENDING)], name="files_created"),
    IndexModel([("user_id", ASCENDING), ("is_deleted", ASCENDING)], name="files_user_del"),
]

CONVERSATIONS_INDEXES = [
    IndexModel([("user_id", ASCENDING)], name="conv_user"),
    IndexModel([("updated_at", DESCENDING)], name="conv_updated"),
]

MESSAGES_INDEXES = [
    IndexModel(
        [("conversation_id", ASCENDING), ("created_at", ASCENDING)],
        name="msg_conv_time",
    ),
]

SUMMARIES_INDEXES = [
    IndexModel([("file_id", ASCENDING)], unique=True, name="summaries_file"),
]

TIMESTAMPS_INDEXES = [
    IndexModel(
        [("file_id", ASCENDING), ("start_time", ASCENDING)],
        name="ts_file_start",
    ),
]

# Mapping of collection name -> indexes for programmatic use.
ALL_INDEXES: dict[str, list[IndexModel]] = {
    "users": USERS_INDEXES,
    "files": FILES_INDEXES,
    "conversations": CONVERSATIONS_INDEXES,
    "messages": MESSAGES_INDEXES,
    "summaries": SUMMARIES_INDEXES,
    "timestamp_entries": TIMESTAMPS_INDEXES,
}
