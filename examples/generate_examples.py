"""Builds the fictional PDF order and spreadsheet template used in the README,
then runs the real pipeline against them so examples/order_updated.xlsx
is an actual output of this tool, not a hand-edited mockup.

All names, CNPJs and quantities below are made up for demonstration purposes.
"""
import os
import sys

from openpyxl import Workbook
from reportlab.pdfgen import canvas

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_reader import extract_data_from_pdf
from excel_writer import update_excel_with_orders

EXAMPLES_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_PATH = os.path.join(EXAMPLES_DIR, "order_example.pdf")
TEMPLATE_PATH = os.path.join(EXAMPLES_DIR, "order_template.xlsx")
OUTPUT_PATH = os.path.join(EXAMPLES_DIR, "order_updated.xlsx")

SELLER_CNPJ = "00.000.000/0001-00"
BUYER_CNPJ = "11.222.333/0001-44"

ORDER_LINES = [
    "PEDIDO DE COMPRAS 123456/2026",
    "",
    f"CNPJ: {SELLER_CNPJ}",
    "RAZAO SOCIAL: EXEMPLO FORNECEDOR ORGANICO LTDA",
    "",
    "COMPANY NAME LTDA LOJA CENTRO",
    f"CNPJ: {BUYER_CNPJ}",
    "",
    "Codigo  Seq      Descricao                          Unid  Qtd  Preco",
    "000123  1557009ABACAXI ORGANICOS DO SUL             UN    01   10,00   25,50",
    "000124  1414119ABOBRINHA ORGANICOS DO SUL            UN    01   20,00   8,90",
    "000125  1364707ACELGA ORGANICOS DO SUL               UN    01   5,00    6,20",
    "",
    "DADOS ADICIONAIS",
    "Pedido gerado automaticamente para fins de exemplo.",
]


def build_pdf():
    c = canvas.Canvas(PDF_PATH, pagesize=(595, 842))
    c.setFont("Courier", 10)
    y = 800
    for line in ORDER_LINES:
        c.drawString(40, y, line)
        y -= 18
    c.save()


def build_template():
    wb = Workbook()
    ws = wb.active
    ws.title = "Harvest Plan"
    ws.append(["CNPJ", "Pedido", 1557009, 1414119, 1364707])
    ws.append([BUYER_CNPJ, "", "", "", ""])
    wb.save(TEMPLATE_PATH)


def run_pipeline():
    orders = extract_data_from_pdf(PDF_PATH)
    update_excel_with_orders(orders, TEMPLATE_PATH, OUTPUT_PATH)


if __name__ == "__main__":
    build_pdf()
    build_template()
    run_pipeline()
    print(f"Generated:\n- {PDF_PATH}\n- {TEMPLATE_PATH}\n- {OUTPUT_PATH}")
