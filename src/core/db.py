"""Gestor de persistencia de historial y progreso con SQLite."""
import sqlite3
import datetime
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Generator
from src.core.config import DB_PATH
from src.core.models import HistoryEntry

# Compatibilidad para atributo is_secret en HistoryEntry sin modificar models.py
if not hasattr(HistoryEntry, "is_secret") or getattr(HistoryEntry, "_patched_for_secret", False) is False:
    _orig_history_init = HistoryEntry.__init__
    def _patched_history_init(self, *args, is_secret: bool = False, **kwargs):
        if len(args) > 6:
            is_secret = args[6]
            args = args[:6]
        _orig_history_init(self, *args, **kwargs)
        self.is_secret = is_secret
    HistoryEntry.__init__ = _patched_history_init
    HistoryEntry.is_secret = False
    HistoryEntry._patched_for_secret = True

class DatabaseManager:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        """Inicializa la tabla y aplica migraciones sin perder datos."""
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS animes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    anime TEXT,
                    url TEXT,
                    provider TEXT,
                    last_cap TEXT,
                    progress TEXT DEFAULT '00:00:00',
                    servers_data TEXT DEFAULT '',
                    updated_at TEXT DEFAULT (datetime('now')),
                    is_secret INTEGER DEFAULT 0
                )
                """
            )
            cursor.execute("PRAGMA table_info(animes)")
            cols = [col[1] for col in cursor.fetchall()]
            if "url" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN url TEXT")
            if "provider" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN provider TEXT")
            if "progress" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN progress TEXT DEFAULT '00:00:00'")
            if "servers_data" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN servers_data TEXT DEFAULT ''")
            if "updated_at" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN updated_at TEXT DEFAULT ''")
                cursor.execute("UPDATE animes SET updated_at = datetime('now') WHERE updated_at IS NULL OR updated_at = ''")
            if "is_secret" not in cols:
                cursor.execute("ALTER TABLE animes ADD COLUMN is_secret INTEGER DEFAULT 0")

            try:
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_animes_anime ON animes(anime)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_animes_updated ON animes(updated_at)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_animes_secret ON animes(is_secret)")
            except Exception:
                pass
            conn.commit()

    def get_last_watched(self, include_secret: bool = False) -> Optional[HistoryEntry]:
        """Obtiene el último anime visualizado para reanudar (-c) según fecha de actualización."""
        with self._connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT anime, url, provider, last_cap, progress, servers_data, is_secret
                FROM animes
            """
            if not include_secret:
                query += " WHERE (is_secret = 0 OR is_secret IS NULL) AND (provider != 'secret' OR provider IS NULL) "
            query += " ORDER BY updated_at DESC, id DESC LIMIT 1 "

            cursor.execute(query)
            row = cursor.fetchone()
            if not row:
                return None
            return HistoryEntry(
                anime_title=row[0],
                url=row[1] or "",
                provider=row[2] or "",
                last_episode=str(row[3]),
                progress=row[4] or "00:00:00",
                servers_data=row[5] or "",
                is_secret=bool(row[6])
            )

    def get_anime(self, anime_title: str) -> Optional[HistoryEntry]:
        """Obtiene el registro de progreso de un anime específico por título."""
        if not anime_title:
            return None
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT anime, url, provider, last_cap, progress, servers_data, is_secret
                FROM animes
                WHERE LOWER(TRIM(anime)) = LOWER(TRIM(?))
                LIMIT 1
                """,
                (anime_title,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return HistoryEntry(
                anime_title=row[0],
                url=row[1] or "",
                provider=row[2] or "",
                last_episode=str(row[3]),
                progress=row[4] or "00:00:00",
                servers_data=row[5] or "",
                is_secret=bool(row[6])
            )

    def save_progress(self, entry: HistoryEntry, is_secret: bool = False):
        """Guarda o actualiza el progreso de un anime actualizando la marca temporal."""
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        is_secret_val = 1 if (is_secret or getattr(entry, "is_secret", False) or entry.provider == "secret") else 0
        with self._connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, is_secret FROM animes WHERE LOWER(TRIM(anime)) = LOWER(TRIM(?))", (entry.anime_title,))
            row = cursor.fetchone()
            if row:
                final_is_secret = 1 if (is_secret_val or (row[1] and int(row[1]) == 1)) else 0
                cursor.execute(
                    """
                    UPDATE animes
                    SET url = ?, provider = ?, last_cap = ?, progress = ?, servers_data = ?, updated_at = ?, is_secret = ?
                    WHERE id = ?
                    """,
                    (
                        entry.url,
                        entry.provider,
                        entry.last_episode,
                        entry.progress,
                        entry.servers_data or "",
                        now_str,
                        final_is_secret,
                        row[0]
                    )
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO animes (anime, url, provider, last_cap, progress, servers_data, updated_at, is_secret)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.anime_title,
                        entry.url,
                        entry.provider,
                        entry.last_episode,
                        entry.progress,
                        entry.servers_data or "",
                        now_str,
                        is_secret_val
                    )
                )
            conn.commit()

    def get_all_history(self, limit: int = 50, include_secret: bool = False) -> List[HistoryEntry]:
        """Devuelve el historial ordenado por última visualización."""
        with self._connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT anime, url, provider, last_cap, progress, servers_data, is_secret
                FROM animes
            """
            if not include_secret:
                query += " WHERE (is_secret = 0 OR is_secret IS NULL) AND (provider != 'secret' OR provider IS NULL) "
            query += " ORDER BY updated_at DESC, id DESC LIMIT ? "
            cursor.execute(query, (limit,))
            return [
                HistoryEntry(
                    anime_title=r[0],
                    url=r[1] or "",
                    provider=r[2] or "",
                    last_episode=str(r[3]),
                    progress=r[4] or "00:00:00",
                    servers_data=r[5] or "",
                    is_secret=bool(r[6])
                )
                for r in cursor.fetchall()
            ]
