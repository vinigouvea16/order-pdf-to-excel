import os
import tkinter as tk
from tkinter import filedialog, messagebox

from pdf_reader import extract_data_from_pdf
from excel_writer import update_excel_with_orders


def display_summary(orders):
    totals = {}
    for order in orders:
        for name, product in order["products"].items():
            totals[name] = totals.get(name, 0) + product["quantity"]

    print("\nConsolidated product summary:")
    for name, quantity in sorted(totals.items()):
        print(f"- {name}: {quantity}x")
    print("\n" + "=" * 50 + "\n")


def select_pdf():
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_entry.delete(0, tk.END)
    pdf_entry.insert(0, file_path)


def select_excel():
    file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    excel_entry.delete(0, tk.END)
    excel_entry.insert(0, file_path)


def start_processing():
    pdf_path = pdf_entry.get()
    excel_path = excel_entry.get()

    if not pdf_path or not excel_path:
        messagebox.showwarning("Warning", "Please select both the PDF and the Excel file.")
        return

    if not os.path.isfile(pdf_path) or not os.path.isfile(excel_path):
        messagebox.showwarning("Warning", "Check that the selected files exist.")
        return

    orders = extract_data_from_pdf(pdf_path)
    if not orders:
        messagebox.showwarning("Warning", "No data was extracted from the PDF.")
        return

    output_file = f"{os.path.splitext(os.path.basename(pdf_path))[0]}_updated.xlsx"
    display_summary(orders)
    result = update_excel_with_orders(orders, excel_path, output_file)

    if result:
        messagebox.showinfo("Done", f"Updated Excel file saved as: {result}")
    else:
        messagebox.showwarning(
            "Missing CNPJs",
            "Some CNPJs in the order are missing from the spreadsheet. Check the console log.",
        )


root = tk.Tk()
root.title("Order Processor")
root.geometry("400x300")

tk.Label(root, text="Select the order PDF:").pack(pady=(10, 0))
pdf_entry = tk.Entry(root, width=50)
pdf_entry.pack(pady=5)
tk.Button(root, text="Choose PDF", command=select_pdf).pack(pady=5)

tk.Label(root, text="Select the input spreadsheet:").pack(pady=(10, 0))
excel_entry = tk.Entry(root, width=50)
excel_entry.pack(pady=5)
tk.Button(root, text="Choose Excel", command=select_excel).pack(pady=5)

tk.Button(root, text="Process", command=start_processing).pack(pady=20)

root.mainloop()
