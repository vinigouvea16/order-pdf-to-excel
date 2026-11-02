import re

import pdfplumber

from config import SELLER_CNPJ, BUYER_COMPANY_MARKER
from products import PRODUCT_MAPPING

# These patterns match literal text in the purchase-order PDFs, in Portuguese.
ORDER_NUMBER_PATTERN = re.compile(r'PEDIDO DE COMPRAS (\d+/\w+)')
CNPJ_PATTERN = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
PRODUCT_LINE_PATTERN = re.compile(r'(\d+)\s+(\d+)([A-Z]+.*?)\s+UN\s+\d+\s+([\d,.]+)\s+([\d,.]+)')
ORDER_SECTION_END_MARKERS = ("DADOS ADICIONAIS", "ADVERTÊNCIA")


def extract_cnpj(text):
    matches = [cnpj for cnpj in CNPJ_PATTERN.findall(text) if cnpj != SELLER_CNPJ]
    return matches[0] if matches else ""


def parse_quantity(value):
    """Parse a number that may be in BR (1.234,56) or EN (1,234.56) format."""
    value = value.strip()
    comma_pos = value.rfind(',')
    dot_pos = value.rfind('.')
    if comma_pos > dot_pos:
        value = value.replace('.', '').replace(',', '.')
    elif dot_pos > comma_pos and comma_pos != -1:
        value = value.replace(',', '')
    elif value.count('.') > 1:
        parts = value.split('.')
        value = ''.join(parts[:-1]) + '.' + parts[-1]
    return float(value)


def extract_product_info(line):
    match = PRODUCT_LINE_PATTERN.match(line)
    if not match:
        return None
    code, seq, name, quantity, price = match.groups()
    return {
        "code": code,
        "seq": int(seq),
        "name": name.strip(),
        "quantity": int(parse_quantity(quantity)),
        "price": parse_quantity(price),
    }


def extract_products_from_lines(lines, products, found_seqs):
    for line in lines:
        line = line.strip()
        if any(marker in line for marker in ORDER_SECTION_END_MARKERS):
            break

        info = extract_product_info(line)
        if not info:
            continue

        found_seqs.add(info["seq"])
        name = PRODUCT_MAPPING.get(info["seq"], info["name"])
        products[name] = {
            "name": name,
            "quantity": info["quantity"],
            "price": info["price"],
            "seq": info["seq"],
        }


def extract_store_name(lines, cnpj):
    for i, line in enumerate(lines):
        if cnpj not in line:
            continue
        for j in range(i - 1, max(i - 4, -1), -1):
            if BUYER_COMPANY_MARKER in lines[j]:
                _, _, store_name = lines[j].partition(BUYER_COMPANY_MARKER)
                store_name = store_name.strip()
                if store_name:
                    return store_name
    return "Unknown store"


def validate_seqs(found_seqs):
    """Warn about product SEQs found in the PDF that aren't in the catalog."""
    unknown_seqs = found_seqs - set(PRODUCT_MAPPING)
    if unknown_seqs:
        print("\nWarning: the following SEQs are not mapped and were ignored:")
        for seq in sorted(unknown_seqs):
            print(f"- SEQ: {seq}")
        print("\nUpdate products.py to include them.\n")


def extract_data_from_pdf(pdf_path):
    orders = []
    current_order = None
    found_seqs = set()

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split("\n")

            order_matches = ORDER_NUMBER_PATTERN.findall(text)
            if order_matches:
                order_number = order_matches[0]
                if current_order and current_order["order_number"] != order_number:
                    orders.append(current_order)

                if not current_order or current_order["order_number"] != order_number:
                    current_order = {
                        "order_number": order_number,
                        "cnpj": "",
                        "store_name": "",
                        "products": {},
                    }

            if current_order and not current_order["cnpj"]:
                current_order["cnpj"] = extract_cnpj(text)
                current_order["store_name"] = extract_store_name(lines, current_order["cnpj"])

            if current_order:
                extract_products_from_lines(lines, current_order["products"], found_seqs)

    if current_order:
        orders.append(current_order)

    validate_seqs(found_seqs)
    return orders
