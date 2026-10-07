from __future__ import annotations

import csv
import math
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from data import Table, number, read_table
from plot import GraphPlot


class GraphApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Построение графиков из файла")
        self.root.geometry("1100x720")
        self.root.minsize(800, 540)
        self.table: Table | None = None

        self.file_label = tk.StringVar(value="Файл не выбран")
        self.x_column = tk.StringVar(value="Номер строки")
        self.y_column = tk.StringVar()
        self.chart_type = tk.StringVar(value="Линия")
        self.title = tk.StringVar(value="График данных")
        self.status = tk.StringVar(value="Откройте файл CSV или TXT")
        self.new_x = tk.StringVar()
        self.new_y = tk.StringVar()

        controls = ttk.Frame(root, padding=10)
        controls.pack(fill=tk.X)
        ttk.Button(controls, text="Открыть файл", command=self.open_file).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(controls, text="Новая таблица", command=self.new_table).grid(row=0, column=1, padx=(0, 8))
        ttk.Label(controls, textvariable=self.file_label).grid(row=0, column=2, columnspan=4, sticky="w")

        ttk.Label(controls, text="Ось X:").grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.x_combo = ttk.Combobox(controls, textvariable=self.x_column, state="readonly", width=19)
        self.x_combo.grid(row=2, column=0, sticky="ew", padx=(0, 8))
        ttk.Label(controls, text="Ось Y:").grid(row=1, column=1, sticky="w", pady=(12, 0))
        self.y_combo = ttk.Combobox(controls, textvariable=self.y_column, state="readonly", width=19)
        self.y_combo.grid(row=2, column=1, sticky="ew", padx=(0, 8))
        ttk.Label(controls, text="Вид графика:").grid(row=1, column=2, sticky="w", pady=(12, 0))
        ttk.Combobox(
            controls, textvariable=self.chart_type, values=("Линия", "Точки", "Столбцы"),
            state="readonly", width=15,
        ).grid(row=2, column=2, sticky="ew", padx=(0, 8))
        ttk.Label(controls, text="Заголовок:").grid(row=1, column=3, sticky="w", pady=(12, 0))
        ttk.Entry(controls, textvariable=self.title, width=26).grid(row=2, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(controls, text="Построить", command=self.plot).grid(row=2, column=4, padx=(0, 8))
        ttk.Button(controls, text="Сохранить PNG", command=self.save_plot).grid(row=2, column=5)
        ttk.Label(controls, text="Новая точка — X:").grid(row=3, column=0, sticky="w", pady=(12, 0))
        ttk.Label(controls, text="Y:").grid(row=3, column=1, sticky="w", pady=(12, 0))
        self.x_entry = ttk.Entry(controls, textvariable=self.new_x, width=19)
        self.x_entry.grid(row=4, column=0, sticky="ew", padx=(0, 8))
        ttk.Entry(controls, textvariable=self.new_y, width=19).grid(row=4, column=1, sticky="ew", padx=(0, 8))
        ttk.Button(controls, text="Добавить точку", command=self.add_point).grid(row=4, column=2, sticky="w")
        self.x_column.trace_add("write", self.update_x_entry)
        self.update_x_entry()
        controls.columnconfigure(3, weight=1)

        pane = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))
        table_frame = ttk.LabelFrame(pane, text="Данные (последние 100 строк)", padding=4)
        pane.add(table_frame, weight=1)
        self.preview = ttk.Treeview(table_frame, show="headings")
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.preview.yview)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.preview.xview)
        self.preview.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        self.preview.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        graph_frame = ttk.LabelFrame(pane, text="График", padding=4)
        pane.add(graph_frame, weight=3)
        self.graph = GraphPlot(graph_frame)

        ttk.Label(root, textvariable=self.status, anchor="w", padding=(10, 3)).pack(fill=tk.X)

    def open_file(self) -> None:
        filename = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Таблицы", "*.csv *.txt *.tsv"), ("Все файлы", "*.*")],
        )
        if not filename:
            return
        try:
            table = read_table(Path(filename))
        except (OSError, UnicodeError, ValueError, csv.Error) as exc:
            messagebox.showerror("Не удалось открыть файл", str(exc))
            return

        self.set_table(table, Path(filename).name)
        self.plot()

    def new_table(self) -> None:
        self.set_table(Table(["X", "Y"], [], [0, 1]), "Новая таблица")
        self.graph.axes.clear()
        self.graph.canvas.draw_idle()
        self.status.set("Введите X и Y, затем нажмите «Добавить точку».")

    def set_table(self, table: Table, label: str) -> None:
        self.table = table
        self.file_label.set(label)
        column_names = [f"{i + 1}: {table.headers[i]}" for i in table.numeric_columns]
        self.x_combo["values"] = ["Номер строки", *column_names]
        self.y_combo["values"] = column_names
        self.x_column.set(column_names[0] if len(column_names) > 1 else "Номер строки")
        self.y_column.set(column_names[1] if len(column_names) > 1 else column_names[0])
        self.new_x.set("")
        self.new_y.set("")

        keys = [str(i) for i in range(len(table.headers))]
        self.preview["columns"] = keys
        for i, header in enumerate(table.headers):
            self.preview.heading(str(i), text=header)
            self.preview.column(str(i), width=115, minwidth=75)
        self.refresh_preview()

    def refresh_preview(self) -> None:
        if self.table is None:
            return
        self.preview.delete(*self.preview.get_children())
        for row in self.table.rows[-100:]:
            self.preview.insert("", tk.END, values=row)

    def update_x_entry(self, *_args: object) -> None:
        row_number = self.x_column.get() == "Номер строки"
        self.x_entry.configure(state="disabled" if row_number else "normal")
        if row_number:
            self.new_x.set("")

    def add_point(self) -> None:
        if self.table is None:
            messagebox.showinfo("Нет таблицы", "Откройте файл или создайте новую таблицу.")
            return
        y_index = int(self.y_column.get().split(":", 1)[0]) - 1
        x_index = None if self.x_column.get() == "Номер строки" else int(self.x_column.get().split(":", 1)[0]) - 1
        if x_index == y_index:
            messagebox.showwarning("Выбор осей", "Выберите разные столбцы для осей X и Y.")
            return
        try:
            y_value = number(self.new_y.get())
            x_value = None if x_index is None else number(self.new_x.get())
            if not math.isfinite(y_value) or (x_value is not None and not math.isfinite(x_value)):
                raise ValueError
        except ValueError:
            messagebox.showwarning("Неверная точка", "Введите конечные числовые значения X и Y.")
            return

        row = [""] * len(self.table.headers)
        row[y_index] = self.new_y.get().strip()
        if x_index is not None:
            row[x_index] = self.new_x.get().strip()
        self.table.rows.append(row)
        self.refresh_preview()
        self.new_x.set("")
        self.new_y.set("")
        self.plot()

    def plot(self) -> None:
        if self.table is None:
            messagebox.showinfo("Нет данных", "Сначала откройте файл с данными.")
            return
        table = self.table
        y_index = int(self.y_column.get().split(":", 1)[0]) - 1
        x_index = None if self.x_column.get() == "Номер строки" else int(self.x_column.get().split(":", 1)[0]) - 1
        if x_index == y_index:
            messagebox.showwarning("Выбор осей", "Выберите разные столбцы для осей X и Y.")
            return

        point_count = self.graph.draw(table, x_index, y_index, self.chart_type.get(), self.title.get())
        if not point_count:
            messagebox.showwarning("Нет точек", "В выбранных столбцах нет полных пар чисел.")
            return
        self.status.set(f"Загружено строк: {len(table.rows)}. Построено точек: {point_count}.")

    def save_plot(self) -> None:
        if self.table is None:
            messagebox.showinfo("Нет графика", "Сначала откройте файл и постройте график.")
            return
        filename = filedialog.asksaveasfilename(
            title="Сохранить график", defaultextension=".png",
            filetypes=[("Изображение PNG", "*.png")],
        )
        if filename:
            try:
                self.graph.save(filename)
            except OSError as exc:
                messagebox.showerror("Не удалось сохранить график", str(exc))
            else:
                self.status.set(f"График сохранён: {filename}")


