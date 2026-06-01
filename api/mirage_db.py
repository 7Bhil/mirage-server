"""Accès à la base MIRAGE centrale (mirage_core.db) depuis Django."""
import os
import sys

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WORKSPACE_ROOT not in sys.path:
    sys.path.insert(0, WORKSPACE_ROOT)

from database_manager import MirageDBManager  # noqa: E402

_db = None


def get_mirage_db() -> MirageDBManager:
    global _db
    if _db is None:
        _db = MirageDBManager(WORKSPACE_ROOT)
    return _db
