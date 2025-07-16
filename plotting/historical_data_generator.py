
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime
import threading

from candle_stick_data import generate_candlestick_csv

def run_csv_generation(product_id, start, end, interval):
    try:
        generate_candlestick_csv(product_id, start, end, interval)
        messagebox.showinfo("Success", "CSV file generated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate CSV:\n{e}")


def on_generate():
    print("Generating CSV...")
    product_id = product_id_var.get()
    start_date = start_cal.get_date()
    end_date = end_cal.get_date()
    interval = interval_var.get()
    print(f"Product ID: {product_id}, Start Date: {start_date}, End Date: {end_date}, Interval: {interval}")
    start_epoch = int(datetime.strptime(start_date.strftime('%Y-%m-%d'), '%Y-%m-%d').timestamp())
    end_epoch = int(datetime.strptime(end_date.strftime('%Y-%m-%d'), '%Y-%m-%d').timestamp())

    try:
        threading.Thread(target=run_csv_generation, args=(product_id, start_epoch, end_epoch, interval)).start()
    except Exception as e:
        print(f"Error starting thread: {e}")

root = tk.Tk()
root.title("Candlestick CSV Generator")

ttk.Label(root, text="Product ID (e.g. BTC-USD):").grid(row=0, column=0, sticky="w")
product_id_var = tk.StringVar(value="BTC-USD")
ttk.Entry(root, textvariable=product_id_var).grid(row=0, column=1)

ttk.Label(root, text="Start Date:").grid(row=1, column=0, sticky="w")
start_cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
start_cal.grid(row=1, column=1)

ttk.Label(root, text="End Date:").grid(row=2, column=0, sticky="w")
end_cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2)
end_cal.grid(row=2, column=1)

ttk.Label(root, text="Granularity (levls):").grid(row=3, column=0, sticky="w")
interval_var = tk.StringVar(value="4")
ttk.Entry(root, textvariable=interval_var).grid(row=3, column=1)

ttk.Button(root, text="Generate CSV", command=on_generate).grid(row=4, column=0, columnspan=2, pady=10)

root.mainloop()