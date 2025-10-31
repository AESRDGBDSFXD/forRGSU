import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from database import TaskManagerDB

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.root.geometry("800x600")
        
        # Инициализация базы данных
        self.db = TaskManagerDB()
        
        # Создание виджетов
        self.create_widgets()
        
        # Загрузка задач
        self.load_tasks()
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка весов строк и столбцов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Менеджер задач", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # Поле поиска
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(0, weight=1)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        search_entry.insert(0, "Поиск задач...")
        search_entry.bind("<FocusIn>", lambda args: search_entry.delete('0', 'end'))
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(button_frame, text="Добавить задачу", 
                  command=self.add_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Редактировать", 
                  command=self.edit_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Удалить", 
                  command=self.delete_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Обновить", 
                  command=self.load_tasks).pack(side=tk.LEFT)
        
        # Таблица задач
        columns = ("ID", "Название", "Приоритет", "Статус", "Создана", "Срок")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        # Настройка колонок
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Приоритет", text="Приоритет")
        self.tree.heading("Статус", text="Статус")
        self.tree.heading("Создана", text="Создана")
        self.tree.heading("Срок", text="Срок")
        
        self.tree.column("ID", width=50)
        self.tree.column("Название", width=200)
        self.tree.column("Приоритет", width=100)
        self.tree.column("Статус", width=100)
        self.tree.column("Создана", width=150)
        self.tree.column("Срок", width=150)
        
        self.tree.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Полоса прокрутки для таблицы
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=3, column=3, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Фрейм с деталями задачи
        details_frame = ttk.LabelFrame(main_frame, text="Детали задачи", padding="5")
        details_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        details_frame.columnconfigure(1, weight=1)
        
        self.details_text = tk.Text(details_frame, height=6, wrap=tk.WORD)
        self.details_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Привязка события выбора задачи
        self.tree.bind('<<TreeviewSelect>>', self.on_task_select)
    
    def load_tasks(self, tasks=None):
        """Загрузка задач в таблицу"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Получение задач
        if tasks is None:
            tasks = self.db.get_all_tasks()
        
        # Заполнение таблицы
        for task in tasks:
            # Форматирование дат для отображения
            created_date = task[5][:16] if task[5] else ""
            due_date = task[6][:10] if task[6] else ""
            
            self.tree.insert("", "end", values=(
                task[0],  # ID
                task[1],  # Название
                task[3],  # Приоритет
                task[4],  # Статус
                created_date,
                due_date
            ))
    
    def on_task_select(self, event):
        """Обработка выбора задачи"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            task_id = item['values'][0]
            
            # Получение полной информации о задаче
            task = self.db.get_task_by_id(task_id)
            if task:
                self.show_task_details(task)
    
    def show_task_details(self, task):
        """Отображение деталей выбранной задачи"""
        self.details_text.delete(1.0, tk.END)
        
        details = f"Название: {task[1]}\n"
        details += f"Описание: {task[2]}\n"
        details += f"Приоритет: {task[3]}\n"
        details += f"Статус: {task[4]}\n"
        details += f"Создана: {task[5][:16]}\n"
        details += f"Срок выполнения: {task[6] if task[6] else 'Не установлен'}\n"
        
        if task[7]:  # completed_date
            details += f"Завершена: {task[7][:16]}"
        
        self.details_text.insert(1.0, details)
    
    def add_task(self):
        """Добавление новой задачи"""
        dialog = TaskDialog(self.root, "Добавить задачу")
        if dialog.result:
            title, description, priority, due_date = dialog.result
            self.db.add_task(title, description, priority, due_date)
            self.load_tasks()
            messagebox.showinfo("Успех", "Задача успешно добавлена!")
    
    def edit_task(self):
        """Редактирование выбранной задачи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для редактирования!")
            return
        
        item = self.tree.item(selection[0])
        task_id = item['values'][0]
        task = self.db.get_task_by_id(task_id)
        
        if task:
            dialog = TaskDialog(self.root, "Редактировать задачу", task)
            if dialog.result:
                title, description, priority, due_date = dialog.result
                status = task[4]  # Сохраняем текущий статус
                self.db.update_task(task_id, title, description, priority, status, due_date)
                self.load_tasks()
                messagebox.showinfo("Успех", "Задача успешно обновлена!")
    
    def delete_task(self):
        """Удаление выбранной задачи"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите задачу для удаления!")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить задачу?"):
            item = self.tree.item(selection[0])
            task_id = item['values'][0]
            self.db.delete_task(task_id)
            self.load_tasks()
            self.details_text.delete(1.0, tk.END)
            messagebox.showinfo("Успех", "Задача успешно удалена!")
    
    def on_search_change(self, *args):
        """Обработка изменения поискового запроса"""
        keyword = self.search_var.get()
        if keyword and keyword != "Поиск задач...":
            tasks = self.db.search_tasks(keyword)
            self.load_tasks(tasks)
        else:
            self.load_tasks()


class TaskDialog(simpledialog.Dialog):
    def __init__(self, parent, title, task=None):
        self.task = task
        self.result = None
        super().__init__(parent, title)
    
    def body(self, frame):
        """Создание тела диалогового окна"""
        ttk.Label(frame, text="Название:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(frame, width=40)
        self.title_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Описание:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.desc_text = tk.Text(frame, width=40, height=4)
        self.desc_text.grid(row=1, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Приоритет:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(value="Средний")
        priority_combo = ttk.Combobox(frame, textvariable=self.priority_var, 
                                     values=["Низкий", "Средний", "Высокий"])
        priority_combo.grid(row=2, column=1, pady=5, padx=5)
        
        ttk.Label(frame, text="Срок выполнения (ГГГГ-ММ-ДД):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.due_entry = ttk.Entry(frame, width=40)
        self.due_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Если редактируем существующую задачу, заполняем поля
        if self.task:
            self.title_entry.insert(0, self.task[1])
            self.desc_text.insert(1.0, self.task[2])
            self.priority_var.set(self.task[3])
            if self.task[6]:
                self.due_entry.insert(0, self.task[6])
        
        return self.title_entry
    
    def apply(self):
        """Обработка нажатия OK"""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
            return
        
        description = self.desc_text.get(1.0, tk.END).strip()
        priority = self.priority_var.get()
        due_date = self.due_entry.get().strip() or None
        
        # Проверка формата даты
        if due_date:
            try:
                datetime.strptime(due_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Ошибка", "Неверный формат даты! Используйте ГГГГ-ММ-ДД")
                return
        
        self.result = (title, description, priority, due_date)


def main():
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()