import os, sys, json
sys.path.insert(0, os.path.abspath('.'))
from backend.ingestion.readers import PDFBudgetReader

reader = PDFBudgetReader()

pdf_path = 'data/raw/budget/2026-2027/DemandBook_39-2.pdf'

records = []
try:
    for r in reader.extract_records(pdf_path):
        records.append(r)
except Exception as e:
    print(e)

for r in records[:5]:
    print(r)
