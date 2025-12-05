import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path: str = "todo.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)')

                conn.commit()
                logger.info("✅ База данных инициализирована")

                cursor.execute("SELECT COUNT(*) as count FROM tasks")
                count = cursor.fetchone()["count"]

                if count == 0:
                    self._add_sample_data(cursor)
                    conn.commit()
                    logger.info("✅ Добавлены тестовые данные")

        except sqlite3.Error as e:
            logger.error(f"❌ Ошибка инициализации БД: {e}")
            raise

    def _add_sample_data(self, cursor):

        sample_tasks = [
            ("Изучить Python", "Пройти курс по Python и Flask", True),
            ("Создать REST API", "Написать API на Flask с SQLite", False),
            ("Изучить SQLite", "Разобраться с работой SQLite в Python", False),
            ("Добавить валидацию", "Реализовать Pydantic схемы", True),
            ("Написать документацию", "Описать API endpoints", False)
        ]

        cursor.executemany(
            "INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)",
            sample_tasks
        )

    def get_all_tasks(self) -> List[Dict[str, Any]]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, description, completed, 
                           created_at, updated_at 
                    FROM tasks 
                    ORDER BY completed, created_at DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения задач: {e}")
            return []

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, title, description, completed, 
                           created_at, updated_at 
                    FROM tasks WHERE id = ?
                """, (task_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения задачи {task_id}: {e}")
            return None

    def create_task(self, title: str, description: str = "") -> Optional[Dict[str, Any]]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tasks (title, description) 
                    VALUES (?, ?)
                """, (title, description))
                conn.commit()

                task_id = cursor.lastrowid
                return self.get_task_by_id(task_id)
        except sqlite3.Error as e:
            logger.error(f"Ошибка создания задачи: {e}")
            return None

    def update_task(self, task_id: int, **kwargs) -> Optional[Dict[str, Any]]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                set_clauses = []
                values = []

                allowed_fields = ["title", "description", "completed"]
                for key, value in kwargs.items():
                    if key in allowed_fields and value is not None:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)

                if not set_clauses:
                    return None

                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(task_id)

                sql = f"UPDATE tasks SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(sql, values)
                conn.commit()

                return self.get_task_by_id(task_id) if cursor.rowcount > 0 else None
        except sqlite3.Error as e:
            logger.error(f"Ошибка обновления задачи {task_id}: {e}")
            return None

    def delete_task(self, task_id: int) -> bool:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления задачи {task_id}: {e}")
            return False

    def delete_all_tasks(self) -> int:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM tasks")
                count_before = cursor.fetchone()["count"]

                cursor.execute("DELETE FROM tasks")
                conn.commit()
                return count_before
        except sqlite3.Error as e:
            logger.error(f"Ошибка удаления всех задач: {e}")
            return 0


    def get_stats(self) -> Dict[str, Any]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN completed = 0 THEN 1 ELSE 0 END) as active
                    FROM tasks
                """)

                stats = dict(cursor.fetchone())
                total = stats["total"] or 0
                completed = stats["completed"] or 0

                stats["completion_rate"] = (completed / total * 100) if total > 0 else 0
                return stats
        except sqlite3.Error as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return {"total": 0, "completed": 0, "active": 0, "completion_rate": 0}

    def search_tasks(self, keyword: str) -> List[Dict[str, Any]]:

        try:
            if not keyword.strip():
                return self.get_all_tasks()

            with self.get_connection() as conn:
                cursor = conn.cursor()
                search_term = f"%{keyword}%"
                cursor.execute("""
                    SELECT id, title, description, completed, 
                           created_at, updated_at 
                    FROM tasks 
                    WHERE title LIKE ? OR description LIKE ?
                    ORDER BY created_at DESC
                """, (search_term, search_term))

                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Ошибка поиска задач: {e}")
            return []

    def toggle_task_completion(self, task_id: int) -> Optional[Dict[str, Any]]:

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("SELECT completed FROM tasks WHERE id = ?", (task_id,))
                result = cursor.fetchone()

                if not result:
                    return None

                new_status = 0 if result["completed"] else 1

                cursor.execute("""
                    UPDATE tasks 
                    SET completed = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                """, (new_status, task_id))
                conn.commit()

                return self.get_task_by_id(task_id)
        except sqlite3.Error as e:
            logger.error(f"Ошибка переключения статуса задачи {task_id}: {e}")
            return None

db = Database()