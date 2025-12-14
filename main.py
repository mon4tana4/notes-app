"""Лабораторная работа номер 3 вариант 14"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog, filedialog
import json
import os
import sys
from datetime import datetime


class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер заметок")
        self.root.geometry("900x650")
        self.root.minsize(600, 400)
        self.center_window()

        self.notes = []
        self.current_note_index = -1
        self.notes_file = "notes_data.json"
        self.font_size = 12

        self.load_notes()
        self.setup_exception_handling()
        self.create_widgets()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.update_status(f"Заметок: {len(self.notes)}")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_exception_handling(self):
        def handle_exception(exc_type, exc_value, exc_traceback):
            error_msg = f"Ошибка:\n\n{exc_value}\n\nПриложение продолжит работу."
            messagebox.showerror("Ошибка", error_msg)
            return True

        sys.excepthook = handle_exception
        self.root.report_callback_exception = lambda *args: handle_exception(*args)

    def update_status(self, message):
        if hasattr(self, 'status_var'):
            self.status_var.set(message)

    def create_widgets(self):
        self.create_menu()

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        left_frame = ttk.LabelFrame(main_frame, text="Список заметок", padding="5")
        left_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10))

        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", pady=(0, 5))

        ttk.Button(btn_frame, text="Новая", command=self.new_note).pack(side="left", fill="x", expand=True, padx=(0, 2))
        ttk.Button(btn_frame, text="Удалить", command=self.delete_note).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btn_frame, text="Экспорт", command=self.export_note).pack(side="left", fill="x", expand=True,
                                                                             padx=(2, 0))

        self.notes_listbox = tk.Listbox(left_frame, height=20, font=("Arial", 10))
        self.notes_listbox.pack(fill="both", expand=True)
        self.notes_listbox.bind('<<ListboxSelect>>', self.on_note_select)

        right_frame = ttk.LabelFrame(main_frame, text="Редактор заметки", padding="5")
        right_frame.grid(row=1, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        ttk.Label(right_frame, text="Заголовок:").grid(row=0, column=0, sticky="w", pady=(0, 5))
        self.title_entry = ttk.Entry(right_frame, font=("Arial", 11))
        self.title_entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ttk.Label(right_frame, text="Текст заметки:").grid(row=1, column=0, sticky="w")
        self.text_area = scrolledtext.ScrolledText(right_frame, wrap="word", font=("Arial", self.font_size))
        self.text_area.grid(row=2, column=0, sticky="nsew", pady=(0, 10))

        btn_save_frame = ttk.Frame(right_frame)
        btn_save_frame.grid(row=3, column=0, sticky="e")

        ttk.Button(btn_save_frame, text="Сохранить", command=self.save_note).pack(side="right", padx=(5, 0))
        ttk.Button(btn_save_frame, text="Очистить", command=self.clear_note).pack(side="right", padx=5)

        self.status_var = tk.StringVar()
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        self.update_notes_list()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Новая заметка", command=self.new_note, accelerator="Ctrl+N")
        file_menu.add_command(label="Сохранить", command=self.save_note, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Экспорт заметки", command=self.export_note)
        file_menu.add_command(label="Импорт заметки", command=self.import_note)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)

        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Вид", menu=view_menu)

        size_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Размер окна", menu=size_menu)
        size_menu.add_command(label="Маленький (600x400)", command=lambda: self.resize_window(600, 400))
        size_menu.add_command(label="Средний (800x600)", command=lambda: self.resize_window(800, 600))
        size_menu.add_command(label="Большой (1000x700)", command=lambda: self.resize_window(1000, 700))
        size_menu.add_command(label="Полный экран", command=self.toggle_fullscreen)

        font_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Размер шрифта", menu=font_menu)
        font_menu.add_command(label="Маленький (10)", command=lambda: self.change_font_size(10))
        font_menu.add_command(label="Средний (12)", command=lambda: self.change_font_size(12))
        font_menu.add_command(label="Большой (14)", command=lambda: self.change_font_size(14))
        font_menu.add_command(label="Огромный (16)", command=lambda: self.change_font_size(16))

        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Инструкция", command=self.show_help)

        self.root.bind('<Control-n>', lambda e: self.new_note())
        self.root.bind('<Control-s>', lambda e: self.save_note())

    def resize_window(self, width, height):
        self.root.geometry(f"{width}x{height}")
        self.center_window()
        self.update_status(f"Размер окна: {width}x{height}")

    def toggle_fullscreen(self):
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)
        if not is_fullscreen:
            self.update_status("Полноэкранный режим")
        else:
            self.update_status("Оконный режим")

    def change_font_size(self, size):
        self.font_size = size
        self.text_area.config(font=("Arial", self.font_size))
        self.update_status(f"Размер шрифта: {size}")

    def load_notes(self):
        try:
            if os.path.exists(self.notes_file):
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    self.notes = json.load(f)
            else:
                self.notes = []
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заметки: {e}")
            self.notes = []

    def save_notes(self):
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заметки: {e}")
            return False

    def update_notes_list(self):
        self.notes_listbox.delete(0, "end")
        for i, note in enumerate(self.notes):
            title = note.get('title', 'Без названия')
            self.notes_listbox.insert("end", f"{i + 1}. {title}")
        self.update_status(f"Заметок: {len(self.notes)}")

    def on_note_select(self, event):
        try:
            selection = self.notes_listbox.curselection()
            if selection:
                self.current_note_index = selection[0]
                note = self.notes[self.current_note_index]
                self.title_entry.delete(0, "end")
                self.title_entry.insert(0, note.get('title', ''))
                self.text_area.delete(1.0, "end")
                self.text_area.insert(1.0, note.get('content', ''))
                self.update_status(f"Редактирование заметки {self.current_note_index + 1}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заметку: {e}")

    def new_note(self):
        self.current_note_index = -1
        self.title_entry.delete(0, "end")
        self.text_area.delete(1.0, "end")
        self.title_entry.insert(0, f"Новая заметка {len(self.notes) + 1}")
        self.text_area.focus()
        self.update_status("Создание новой заметки")

    def save_note(self):
        try:
            title = self.title_entry.get().strip()
            content = self.text_area.get(1.0, "end").strip()

            if not title:
                messagebox.showwarning("Внимание", "Введите заголовок заметки")
                return

            note_data = {
                'title': title,
                'content': content,
                'created': datetime.now().strftime("%d.%m.%Y %H:%M"),
                'modified': datetime.now().strftime("%d.%m.%Y %H:%M")
            }

            if self.current_note_index >= 0:
                self.notes[self.current_note_index] = note_data
                self.update_status(f"Заметка обновлена: {title}")
            else:
                self.notes.append(note_data)
                self.current_note_index = len(self.notes) - 1
                self.update_status(f"Заметка создана: {title}")

            self.save_notes()
            self.update_notes_list()
            self.notes_listbox.selection_set(self.current_note_index)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заметку: {e}")

    def delete_note(self):
        try:
            if self.current_note_index >= 0:
                note_title = self.notes[self.current_note_index].get('title', '')
                if messagebox.askyesno("Подтверждение", f"Удалить заметку '{note_title}'?"):
                    del self.notes[self.current_note_index]
                    self.save_notes()
                    self.update_notes_list()
                    self.new_note()
                    self.update_status("Заметка удалена")
            else:
                messagebox.showinfo("Информация", "Выберите заметку для удаления")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить заметку: {e}")

    def clear_note(self):
        self.title_entry.delete(0, "end")
        self.text_area.delete(1.0, "end")
        self.update_status("Редактор очищен")

    def export_note(self):
        if self.current_note_index >= 0:
            note = self.notes[self.current_note_index]
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                initialfile=f"{note['title']}.txt"
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(f"Заголовок: {note['title']}\n")
                        f.write(f"Дата создания: {note['created']}\n")
                        f.write(f"Дата изменения: {note['modified']}\n")
                        f.write("\n" + "=" * 50 + "\n\n")
                        f.write(note['content'])
                    messagebox.showinfo("Экспорт", f"Заметка сохранена в файл:\n{file_path}")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось экспортировать: {e}")
        else:
            messagebox.showinfo("Информация", "Выберите заметку для экспорта")

    def import_note(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                title = os.path.basename(file_path).replace('.txt', '')
                note_data = {
                    'title': title,
                    'content': content,
                    'created': datetime.now().strftime("%d.%m.%Y %H:%M"),
                    'modified': datetime.now().strftime("%d.%m.%Y %H:%M")
                }
                self.notes.append(note_data)
                self.save_notes()
                self.update_notes_list()
                messagebox.showinfo("Импорт", "Заметка успешно импортирована")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать: {e}")

    def show_about(self):
        about_text = """Менеджер заметок
Версия 1.0

Лабораторная работа по программированию

Функции:
- Создание, редактирование и удаление заметок
- Сохранение данных в JSON формате
- Настройка размеров окна приложения
- Обработка исключений
- Экспорт и импорт заметок"""
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        help_text = """Инструкция по использованию:

1. Создание новой заметки: Файл → Новая заметка (Ctrl+N)
2. Сохранение заметки: Файл → Сохранить (Ctrl+S)
3. Изменение размера окна: Вид → Размер окна
4. Изменение размера шрифта: Вид → Размер шрифта
5. Экспорт заметки: Файл → Экспорт заметки
6. Импорт заметки: Файл → Импорт заметки

Все данные автоматически сохраняются в файл notes_data.json"""
        messagebox.showinfo("Инструкция", help_text)

    def on_closing(self):
        if messagebox.askokcancel("Выход", "Сохранить изменения перед выходом?"):
            if self.save_notes():
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    try:
        root = tk.Tk()
        app = NotesApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Не удалось запустить приложение: {e}")


if __name__ == "__main__":
    main()