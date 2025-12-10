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