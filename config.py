"""Buyer/seller identifiers used to match orders in the PDF, overridable via environment variables or a .env file."""
import os

from dotenv import load_dotenv

load_dotenv()

# The distributor's own CNPJ, excluded when scanning the PDF for the buyer's CNPJ.
SELLER_CNPJ = os.environ.get("SELLER_CNPJ", "00.000.000/0001-00")

# Text that marks the buyer's company line right above its CNPJ in the PDF.
# The store name is whatever follows this marker on that line.
BUYER_COMPANY_MARKER = os.environ.get("BUYER_COMPANY_MARKER", "COMPANY NAME LTDA")
