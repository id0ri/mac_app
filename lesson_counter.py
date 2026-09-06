import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import sys
import os
from tkcalendar import DateEntry
import locale

try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Russian_Russia.1251')
    except:
        pass


class LessonCounterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Подсчет уроков по дням недели")
        self.root.geometry("500x400")
        self.root.resizable(False, False)

        self.days_vars = {
            "Пн": tk.IntVar(value=0),
            "Вт": tk.IntVar(value=0),
            "Ср": tk.IntVar(value=0),
            "Чт": tk.IntVar(value=0),
            "Пт": tk.IntVar(value=0),
            "Сб": tk.IntVar(value=0),
            "Вс": tk.IntVar(value=0),
        }

        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self.use_today = tk.IntVar(value=1)
        self.include_start = tk.IntVar(value=1)
        self.include_end = tk.IntVar(value=1)

        self.today = datetime.now().date()
        self.start_date.set(self.today.strftime("%d.%m.%Y"))

        end_of_may = datetime(self.today.year, 5, 31).date()
        if self.today > end_of_may:
            end_of_may = datetime(self.today.year + 1, 5, 31).date()
        self.end_date.set(end_of_may.strftime("%d.%m.%Y"))

        self.create_widgets()

    def create_widgets(self):
        days_frame = ttk.LabelFrame(self.root, text="Выберите дни недели для подсчета", padding=10)
        days_frame.pack(fill="x", padx=10, pady=5)

        days_list = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days_list):
            cb = ttk.Checkbutton(
                days_frame,
                text=day,
                variable=self.days_vars[day],
                width=6
            )
            cb.grid(row=0, column=i, padx=3, pady=2, sticky="w")

        dates_frame = ttk.LabelFrame(self.root, text="Период", padding=10)
        dates_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(dates_frame, text="Начальная дата:").grid(row=0, column=0, sticky="w", pady=(5, 0))

        self.start_date_entry = DateEntry(
            dates_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy',
            state='normal' if not self.use_today.get() else 'disabled',
            locale='ru_RU',
            firstweekday='monday',
            mindate=None,
            maxdate=None,
            showweeknumbers=False
        )

        self.start_date_entry.set_date(self.today)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=(5, 0), sticky="w")

        self.start_date_entry.bind('<<DateEntrySelected>>', self.on_start_date_change)

        ttk.Checkbutton(
            dates_frame,
            text="Включать начальную дату",
            variable=self.include_start
        ).grid(row=0, column=3, padx=(20, 0), pady=(5, 0), sticky="w")

        ttk.Checkbutton(
            dates_frame,
            text="Использовать сегодняшний день",
            variable=self.use_today,
            command=self.toggle_today
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        ttk.Label(dates_frame, text="Конечная дата:").grid(row=2, column=0, sticky="w", pady=(10, 0))

        self.end_date_entry = DateEntry(
            dates_frame,
            width=15,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='dd.mm.yyyy',
            locale='ru_RU',
            firstweekday='monday',
            mindate=None,
            maxdate=None,
            showweeknumbers=False
        )

        end_date_obj = datetime.strptime(self.end_date.get(), "%d.%m.%Y").date()
        self.end_date_entry.set_date(end_date_obj)
        self.end_date_entry.grid(row=2, column=1, padx=5, pady=(10, 0), sticky="w")

        self.end_date_entry.bind('<<DateEntrySelected>>', self.on_end_date_change)

        ttk.Checkbutton(
            dates_frame,
            text="Включать конечную дату",
            variable=self.include_end
        ).grid(row=2, column=3, padx=(20, 0), pady=(10, 0), sticky="w")

        calc_button = ttk.Button(self.root, text="Подсчитать количество уроков", command=self.calculate)
        calc_button.pack(pady=15)

        result_frame = ttk.LabelFrame(self.root, text="Результат", padding=10)
        result_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.result_label = ttk.Label(result_frame, text="", font=("Arial", 12, "bold"))
        self.result_label.pack(pady=10)

        self.detail_label = ttk.Label(result_frame, text="", font=("Arial", 10), foreground="gray")
        self.detail_label.pack()

        if self.use_today.get():
            self.start_date_entry.config(state="disabled")

    def on_start_date_change(self, event):
        """Обновляет строковую переменную при выборе даты в календаре"""
        date_obj = self.start_date_entry.get_date()
        self.start_date.set(date_obj.strftime("%d.%m.%Y"))

    def on_end_date_change(self, event):
        """Обновляет строковую переменную при выборе даты в календаре"""
        date_obj = self.end_date_entry.get_date()
        self.end_date.set(date_obj.strftime("%d.%m.%Y"))

    def toggle_today(self):
        """Обновляет начальную дату при включении/выключении 'Сегодня'"""
        if self.use_today.get():
            today = datetime.now().date()
            self.start_date.set(today.strftime("%d.%m.%Y"))
            self.start_date_entry.set_date(today)
            self.start_date_entry.config(state="disabled")
        else:
            self.start_date_entry.config(state="normal")

    def parse_date(self, date_str):
        """Парсит дату в формате дд.мм.гггг"""
        try:
            return datetime.strptime(date_str.strip(), "%d.%m.%Y").date()
        except ValueError:
            return None

    def calculate(self):
        """Основной подсчет"""
        if not any(var.get() for var in self.days_vars.values()):
            messagebox.showwarning("Внимание", "Выберите хотя бы один день недели!")
            return

        start = self.start_date_entry.get_date()
        end = self.end_date_entry.get_date()

        self.start_date.set(start.strftime("%d.%m.%Y"))
        self.end_date.set(end.strftime("%d.%m.%Y"))

        if start > end:
            messagebox.showerror("Ошибка", "Начальная дата не может быть позже конечной!")
            return

        selected_days = []
        day_map = {"Пн": 0, "Вт": 1, "Ср": 2, "Чт": 3, "Пт": 4, "Сб": 5, "Вс": 6}
        for day_name, var in self.days_vars.items():
            if var.get():
                selected_days.append(day_map[day_name])

        count = 0
        current = start
        one_day = timedelta(days=1)

        if not self.include_start.get():
            current += one_day

        end_date_for_count = end
        if not self.include_end.get():
            end_date_for_count -= one_day

        while current <= end_date_for_count:
            # В Python: 0=пн, 6=вс
            if current.weekday() in selected_days:
                count += 1
            current += one_day

        days_names = [name for name, var in self.days_vars.items() if var.get()]
        days_str = ", ".join(days_names)

        self.result_label.config(text=f"Всего уроков: {count}")

        detail = f"С {start.strftime('%d.%m.%Y')} по {end.strftime('%d.%m.%Y')}"
        if not self.include_start.get():
            detail += " (без начальной)"
        if not self.include_end.get():
            detail += " (без конечной)"
        detail += f"\nДни: {days_str}"
        self.detail_label.config(text=detail)


def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    root = tk.Tk()
    app = LessonCounterApp(root)
    root.mainloop()

