from openpyxl import load_workbook


def load_seq_to_column_mapping(ws):
    """Row 1 holds each product's SEQ code as the column header."""
    mapping = {}
    for col in range(1, ws.max_column + 1):
        seq = ws.cell(row=1, column=col).value
        if isinstance(seq, int):
            mapping[seq] = col
    return mapping


def update_excel_with_orders(orders, input_file, output_file):
    """Write each order's quantities into the matching CNPJ row and SEQ column.

    Returns the output path on success, or None if some order CNPJ has no
    matching row in the spreadsheet (the caller is expected to report that).
    """
    if not orders:
        print("No data to process.")
        return None

    wb = load_workbook(input_file)
    ws = wb.active
    seq_to_column = load_seq_to_column_mapping(ws)

    cnpj_rows = {ws.cell(row=row, column=1).value: row for row in range(2, ws.max_row + 1)}
    missing_cnpjs = {order["cnpj"] for order in orders} - set(cnpj_rows)
    if missing_cnpjs:
        print("\nError: the following CNPJs are in the orders but not in the spreadsheet:")
        for cnpj in missing_cnpjs:
            print(f"- {cnpj}")
        return None

    for order in orders:
        row = cnpj_rows[order["cnpj"]]
        ws.cell(row=row, column=2, value=order["order_number"])

        for product in order["products"].values():
            column = seq_to_column.get(product["seq"])
            if column:
                ws.cell(row=row, column=column, value=product["quantity"])

    wb.save(output_file)
    return output_file
