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