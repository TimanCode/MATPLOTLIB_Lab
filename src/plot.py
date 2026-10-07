from __future__ import annotations

import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from data import Table, number


class GraphPlot:
    def __init__(self, parent: tk.Widget) -> None:
        self.figure = Figure(figsize=(7, 5), dpi=100, layout="constrained")
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        toolbar = NavigationToolbar2Tk(self.canvas, parent, pack_toolbar=False)
        toolbar.update()
        toolbar.pack(fill=tk.X)

    def draw(
        self, table: Table, x_index: int | None, y_index: int, kind: str, title: str
    ) -> int:
        x_values: list[float | int] = []
        y_values: list[float] = []
        for row_number, row in enumerate(table.rows, start=1):
            if not row[y_index] or (x_index is not None and not row[x_index]):
                continue
            x_values.append(row_number if x_index is None else number(row[x_index]))
            y_values.append(number(row[y_index]))
        if not x_values:
            return 0

        self.axes.clear()
        if kind == "Точки":
            self.axes.scatter(x_values, y_values, color="#2563eb")
        elif kind == "Столбцы":
            self.axes.bar(x_values, y_values, color="#2563eb")
        else:
            self.axes.plot(x_values, y_values, marker="o", markersize=3, color="#2563eb")
        self.axes.set_title(title)
        self.axes.set_xlabel("Номер строки" if x_index is None else table.headers[x_index])
        self.axes.set_ylabel(table.headers[y_index])
        self.axes.grid(True, alpha=0.3)
        self.canvas.draw_idle()
        return len(x_values)

    def save(self, filename: str) -> None:
        self.figure.savefig(filename, dpi=150)
