import sqlite3
from datetime import datetime

class TaskManagerDB:
    def __init__(self, db_name='task_manager.db'):
        self.db_name = db_name
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных и создание таблицы"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT DEFAULT 'Средний',
                status TEXT DEFAULT 'Не начата',
                created_date TEXT NOT NULL,
                due_date TEXT,
                completed_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_task(self, title, description="", priority="Средний", due_date=None):
        """Добавление новой задачи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, status, created_date, due_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, description, priority, "Не начата", created_date, due_date))
        
        conn.commit()
        conn.close()
    
    def get_all_tasks(self):
        """Получение всех задач"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks ORDER BY created_date DESC
        ''')
        
        tasks = cursor.fetchall()
        conn.close()
        return tasks
    
    def get_task_by_id(self, task_id):
        """Получение задачи по ID"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM tasks WHERE id = ?', (task_id,))
        task = cursor.fetchone()
        conn.close()
        return task
    
    def update_task(self, task_id, title, description, priority, status, due_date):
        """Обновление задачи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        if status == "Завершена":
            completed_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            completed_date = None
        
        cursor.execute('''
            UPDATE tasks 
            SET title = ?, description = ?, priority = ?, status = ?, due_date = ?, completed_date = ?
            WHERE id = ?
        ''', (title, description, priority, status, due_date, completed_date, task_id))
        
        conn.commit()
        conn.close()
    
    def delete_task(self, task_id):
        """Удаление задачи"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        
        conn.commit()
        conn.close()
    
    def search_tasks(self, keyword):
        """Поиск задач по ключевому слову"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY created_date DESC
        ''', (f'%{keyword}%', f'%{keyword}%'))
        
        tasks = cursor.fetchall()
        conn.close()
        return tasks