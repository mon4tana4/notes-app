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