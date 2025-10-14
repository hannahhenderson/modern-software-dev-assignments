from __future__ import annotations

import logging
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    """Ensure the data directory exists, creating it if necessary."""
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Data directory ensured: {DATA_DIR}")
    except OSError as e:
        logger.error(f"Failed to create data directory {DATA_DIR}: {e}")
        raise RuntimeError(f"Failed to create data directory: {e}") from e


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager for database connections with proper error handling.

    Yields:
        sqlite3.Connection: Database connection with row factory set

    Raises:
        RuntimeError: If database connection fails
    """
    ensure_data_directory_exists()

    try:
        connection = sqlite3.connect(DB_PATH, timeout=30.0)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        logger.debug("Database connection established")

        try:
            yield connection
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            connection.rollback()
            raise
        else:
            connection.commit()
            logger.debug("Database transaction committed")
        finally:
            connection.close()
            logger.debug("Database connection closed")

    except sqlite3.Error as e:
        logger.error(f"Database connection failed: {e}")
        raise RuntimeError(f"Database connection failed: {e}") from e


def init_db() -> None:
    """Initialize the database with required tables."""
    try:
        with get_connection() as connection:
            cursor = connection.cursor()

            # Create notes table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL CHECK(length(content) > 0),
                    created_at TEXT DEFAULT (datetime('now'))
                );
                """
            )

            # Create action_items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL CHECK(length(text) > 0),
                    done INTEGER DEFAULT 0 CHECK(done IN (0, 1)),
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
                );
                """
            )

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_action_items_done ON action_items(done);"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);")

            logger.info("Database initialized successfully")

    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise RuntimeError(f"Failed to initialize database: {e}") from e


def insert_note(content: str) -> int:
    """
    Insert a new note into the database.

    Args:
        content: The note content

    Returns:
        The ID of the inserted note

    Raises:
        ValueError: If content is empty or invalid
        RuntimeError: If database operation fails
    """
    if not isinstance(content, str):
        raise TypeError(f"Content must be a string, got {type(content).__name__}")

    content = content.strip()
    if not content:
        raise ValueError("Note content cannot be empty")

    if len(content) > 1_000_000:  # 1MB limit
        raise ValueError(f"Note content too long: {len(content)} characters (max: 1,000,000)")

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (content,))
            note_id = int(cursor.lastrowid or 0)
            logger.info(f"Inserted note with ID {note_id}")
            return note_id
    except sqlite3.Error as e:
        logger.error(f"Failed to insert note: {e}")
        raise RuntimeError(f"Failed to insert note: {e}") from e


def list_notes() -> list[sqlite3.Row]:
    """
    List all notes in the database.

    Returns:
        List of note rows ordered by ID descending

    Raises:
        RuntimeError: If database operation fails
    """
    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT id, content, created_at FROM notes ORDER BY id DESC")
            notes = list(cursor.fetchall())
            logger.debug(f"Retrieved {len(notes)} notes")
            return notes
    except sqlite3.Error as e:
        logger.error(f"Failed to list notes: {e}")
        raise RuntimeError(f"Failed to list notes: {e}") from e


def get_note(note_id: int) -> sqlite3.Row | None:
    """
    Get a specific note by ID.

    Args:
        note_id: The ID of the note to retrieve

    Returns:
        The note row if found, None otherwise

    Raises:
        TypeError: If note_id is not an integer
        RuntimeError: If database operation fails
    """
    if not isinstance(note_id, int):
        raise TypeError(f"Note ID must be an integer, got {type(note_id).__name__}")

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT id, content, created_at FROM notes WHERE id = ?",
                (note_id,),
            )
            row = cursor.fetchone()
            if row:
                logger.debug(f"Retrieved note with ID {note_id}")
            else:
                logger.debug(f"Note with ID {note_id} not found")
            return row
    except sqlite3.Error as e:
        logger.error(f"Failed to get note {note_id}: {e}")
        raise RuntimeError(f"Failed to get note: {e}") from e


def insert_action_items(items: list[str], note_id: int | None = None) -> list[int]:
    """
    Insert action items into the database.

    Args:
        items: List of action item texts
        note_id: Optional note ID to associate with items

    Returns:
        List of inserted action item IDs

    Raises:
        TypeError: If items is not a list or note_id is not an integer
        ValueError: If items list is empty or contains invalid items
        RuntimeError: If database operation fails
    """
    if not isinstance(items, list):
        raise TypeError(f"Items must be a list, got {type(items).__name__}")

    if not items:
        logger.warning("Attempted to insert empty action items list")
        return []

    if note_id is not None and not isinstance(note_id, int):
        raise TypeError(f"Note ID must be an integer, got {type(note_id).__name__}")

    # Validate items
    validated_items = []
    for i, item in enumerate(items):
        if not isinstance(item, str):
            raise TypeError(f"Item at index {i} must be a string, got {type(item).__name__}")

        item = item.strip()
        if not item:
            logger.warning(f"Skipping empty item at index {i}")
            continue

        if len(item) > 1000:  # Reasonable length limit
            logger.warning(f"Item at index {i} too long ({len(item)} chars), truncating")
            item = item[:1000]

        validated_items.append(item)

    if not validated_items:
        logger.warning("No valid items to insert after validation")
        return []

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            ids: list[int] = []

            for item in validated_items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (note_id, item),
                )
                ids.append(int(cursor.lastrowid or 0))

            logger.info(f"Inserted {len(ids)} action items")
            return ids
    except sqlite3.Error as e:
        logger.error(f"Failed to insert action items: {e}")
        raise RuntimeError(f"Failed to insert action items: {e}") from e


def list_action_items(note_id: int | None = None) -> list[sqlite3.Row]:
    """
    List action items, optionally filtered by note ID.

    Args:
        note_id: Optional note ID to filter by

    Returns:
        List of action item rows ordered by ID descending

    Raises:
        TypeError: If note_id is not an integer
        RuntimeError: If database operation fails
    """
    if note_id is not None and not isinstance(note_id, int):
        raise TypeError(f"Note ID must be an integer, got {type(note_id).__name__}")

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            if note_id is None:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items ORDER BY id DESC"
                )
            else:
                cursor.execute(
                    "SELECT id, note_id, text, done, created_at FROM action_items WHERE note_id = ? ORDER BY id DESC",
                    (note_id,),
                )
            items = list(cursor.fetchall())
            logger.debug(f"Retrieved {len(items)} action items")
            return items
    except sqlite3.Error as e:
        logger.error(f"Failed to list action items: {e}")
        raise RuntimeError(f"Failed to list action items: {e}") from e


def mark_action_item_done(action_item_id: int, done: bool) -> None:
    """
    Mark an action item as done or not done.

    Args:
        action_item_id: The ID of the action item to update
        done: Whether the item is done

    Raises:
        TypeError: If action_item_id is not an integer
        RuntimeError: If database operation fails
    """
    if not isinstance(action_item_id, int):
        raise TypeError(f"Action item ID must be an integer, got {type(action_item_id).__name__}")

    try:
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?",
                (1 if done else 0, action_item_id),
            )

            if cursor.rowcount == 0:
                logger.warning(f"No action item found with ID {action_item_id}")
            else:
                logger.info(
                    f"Marked action item {action_item_id} as {'done' if done else 'not done'}"
                )
    except sqlite3.Error as e:
        logger.error(f"Failed to mark action item {action_item_id} as done: {e}")
        raise RuntimeError(f"Failed to mark action item as done: {e}") from e
