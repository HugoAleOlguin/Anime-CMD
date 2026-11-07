"""Pruebas unitarias para el gestor de base de datos."""
import unittest
import tempfile
from pathlib import Path
from src.core.db import DatabaseManager
from src.core.models import HistoryEntry

class TestDatabase(unittest.TestCase):
    def test_database_init_and_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_history.db"
            db = DatabaseManager(db_path=db_file)

            # Base vacía inicialmente
            self.assertIsNone(db.get_last_watched())

            # Guardar entrada
            entry = HistoryEntry(
                anime_title="Shingeki no Kyojin",
                url="https://ww3.animeonline.ninja/online/shingeki-no-kyojin/",
                provider="animeonline",
                last_episode="1",
                progress="00:15:30",
                servers_data="servers_json"
            )
            db.save_progress(entry)

            # Recuperar última entrada
            last = db.get_last_watched()
            self.assertIsNotNone(last)
            self.assertEqual(last.anime_title, "Shingeki no Kyojin")
            self.assertEqual(last.last_episode, "1")
            self.assertEqual(last.progress, "00:15:30")
            self.assertEqual(last.provider, "animeonline")

            # Actualizar progreso
            entry.last_episode = "2"
            entry.progress = "00:05:00"
            db.save_progress(entry)

            last_updated = db.get_last_watched()
            self.assertEqual(last_updated.last_episode, "2")
            self.assertEqual(last_updated.progress, "00:05:00")

    def test_legacy_database_without_unique_constraint(self):
        """Prueba que el gestor funcione con esquemas antiguos que no tenían la restricción UNIQUE en 'anime'."""
        import sqlite3
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "legacy_history.db"
            # Crear esquema antiguo de ani-es (sin UNIQUE en anime)
            conn = sqlite3.connect(str(db_file))
            conn.execute("CREATE TABLE animes (id INTEGER PRIMARY KEY, anime TEXT, last_cap TEXT, progress TEXT, url TEXT, provider TEXT, servers_data TEXT DEFAULT '')")
            conn.commit()
            conn.close()

            # Inicializar DatabaseManager con la BD existente
            db = DatabaseManager(db_path=db_file)
            entry = HistoryEntry(
                anime_title="Tokyo Revengers",
                url="https://ww4.animeonline.ninja/online/tokyo-revengers/",
                provider="animeonline",
                last_episode="57",
                progress="00:10:20"
            )
            # No debe lanzar sqlite3.OperationalError: ON CONFLICT clause does not match...
            db.save_progress(entry)

            last = db.get_last_watched()
            self.assertIsNotNone(last)
            self.assertEqual(last.anime_title, "Tokyo Revengers")
            self.assertEqual(last.last_episode, "57")

            # Actualizar de nuevo
            entry.last_episode = "58"
            db.save_progress(entry)
            updated = db.get_last_watched()
            self.assertEqual(updated.last_episode, "58")

    def test_chronological_ordering_on_update(self):
        """Verifica que al actualizar un anime viejo, este pase a ser el último visto (no dependa del id autoincremental)."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_chrono.db"
            db = DatabaseManager(db_path=db_file)

            # Insertar Anime 1 (id=1)
            db.save_progress(HistoryEntry(
                anime_title="Tokyo Revengers",
                url="url1",
                provider="animeonline",
                last_episode="57"
            ))
            time.sleep(0.01)

            # Insertar Anime 2 (id=2)
            db.save_progress(HistoryEntry(
                anime_title="Re:Zero",
                url="url2",
                provider="animeonline",
                last_episode="14"
            ))
            self.assertEqual(db.get_last_watched().anime_title, "Re:Zero")
            time.sleep(0.01)

            # Ahora actualizar Anime 1 (id=1 sigue siendo 1, pero debe ser el más reciente)
            db.save_progress(HistoryEntry(
                anime_title="Tokyo Revengers",
                url="url1",
                provider="animeonline",
                last_episode="58"
            ))
            self.assertEqual(db.get_last_watched().anime_title, "Tokyo Revengers")
            self.assertEqual(db.get_last_watched().last_episode, "58")

            # Verificar get_anime para cada anime independientemente
            rz = db.get_anime("re:zero")
            self.assertIsNotNone(rz)
            self.assertEqual(rz.last_episode, "14")

    def test_secret_anime_isolation_by_provider(self):
        """Verifica que animes con provider='secret' no aparezcan en get_last_watched(include_secret=False)."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_secret_prov.db"
            db = DatabaseManager(db_path=db_file)

            # 1. Guardar anime normal
            normal_entry = HistoryEntry(
                anime_title="Frieren",
                url="https://animeonline.ninja/online/frieren/",
                provider="animeonline",
                last_episode="28"
            )
            db.save_progress(normal_entry)
            time.sleep(0.01)

            # 2. Guardar anime secreto (provider='secret')
            secret_entry = HistoryEntry(
                anime_title="Secret OVA 1",
                url="https://tiohentai.com/hentai/secret-1",
                provider="secret",
                last_episode="1"
            )
            db.save_progress(secret_entry)

            # get_last_watched(include_secret=False) debe ignorar el secreto y devolver el normal
            last_normal = db.get_last_watched(include_secret=False)
            self.assertIsNotNone(last_normal)
            self.assertEqual(last_normal.anime_title, "Frieren")
            self.assertFalse(getattr(last_normal, "is_secret", False))

            # get_last_watched(include_secret=True) debe devolver el secreto más reciente
            last_secret = db.get_last_watched(include_secret=True)
            self.assertIsNotNone(last_secret)
            self.assertEqual(last_secret.anime_title, "Secret OVA 1")
            self.assertTrue(getattr(last_secret, "is_secret", False))

            # get_all_history
            all_normal = db.get_all_history(include_secret=False)
            self.assertEqual(len(all_normal), 1)
            self.assertEqual(all_normal[0].anime_title, "Frieren")

            all_secret = db.get_all_history(include_secret=True)
            self.assertEqual(len(all_secret), 2)
            self.assertEqual(all_secret[0].anime_title, "Secret OVA 1")

    def test_secret_anime_isolation_by_is_secret_flag(self):
        """Verifica que animes con is_secret=True queden aislados aunque provider no sea 'secret'."""
        import time
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_secret_flag.db"
            db = DatabaseManager(db_path=db_file)

            # 1. Guardar anime normal
            db.save_progress(HistoryEntry(
                anime_title="Steins;Gate",
                url="url_sg",
                provider="animeflv",
                last_episode="24"
            ))
            time.sleep(0.01)

            # 2. Guardar anime con is_secret=True en save_progress
            db.save_progress(
                HistoryEntry(
                    anime_title="Secret Flagged Anime",
                    url="url_secret",
                    provider="other_provider",
                    last_episode="2"
                ),
                is_secret=True
            )

            # En modo normal, no debe devolverse el secreto
            last_normal = db.get_last_watched(include_secret=False)
            self.assertIsNotNone(last_normal)
            self.assertEqual(last_normal.anime_title, "Steins;Gate")

            # En modo secreto, sí debe devolverse
            last_secret = db.get_last_watched(include_secret=True)
            self.assertIsNotNone(last_secret)
            self.assertEqual(last_secret.anime_title, "Secret Flagged Anime")
            self.assertTrue(getattr(last_secret, "is_secret", False))

    def test_only_secret_anime_in_database(self):
        """Si solo existen animes secretos, get_last_watched(include_secret=False) debe retornar None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_only_secret.db"
            db = DatabaseManager(db_path=db_file)

            db.save_progress(HistoryEntry(
                anime_title="Solo Secreto",
                url="url_s",
                provider="secret",
                last_episode="1"
            ))

            self.assertIsNone(db.get_last_watched(include_secret=False))
            self.assertIsNotNone(db.get_last_watched(include_secret=True))
            self.assertEqual(db.get_last_watched(include_secret=True).anime_title, "Solo Secreto")

if __name__ == "__main__":
    unittest.main()
