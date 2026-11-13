from backend.ingestion.models import RawSchemeRecord
from backend.ingestion.scheme_normalizer import SchemeNormalizer

records = [
    RawSchemeRecord(
        record_id="1",
        department_name="Health",
        scheme_name="Muthulakshmi Reddy Scheme (cid:12)",
        financial_year="2023-2024",
        source_document_id="doc1",
        description="Provides maternity assistance.",
        allocation_amount="Rs. 1,500.50 crores"
    ),

    RawSchemeRecord(
        record_id="2",
        department_name="",
        scheme_name="Unknown Scheme",
        financial_year="2023-24",
        source_document_id="doc2"
    ),

    RawSchemeRecord(
        record_id="1",
        department_name="Health",
        scheme_name="Muthulakshmi Reddy Scheme (cid:12)",
        financial_year="2023-2024",
        source_document_id="doc1",
        description="Provides maternity assistance.",
        allocation_amount="Rs. 1,500.50 crores"
    ),

    RawSchemeRecord(
        record_id="3",
        department_name="Health",
        scheme_name="Muthulakshmi Reddy Scheme (cid:12)",
        financial_year="2023-24",
        source_document_id="doc1",
        description="Slightly different description."
    )
]

normalizer = SchemeNormalizer()
valid, unresolved, report = normalizer.process_records(records)
print("Valid:", len(valid))
print("Unresolved:", len(unresolved))
print("Report:", report)

assert valid[0]["financial_year"] == "2023-24"
assert valid[0]["allocation_numeric"] == 1500.50
assert valid[0]["scheme_name"] == "Muthulakshmi Reddy Scheme"
assert valid[0]["original_scheme_name"] == "Muthulakshmi Reddy Scheme (cid:12)"
assert valid[1]["is_potential_duplicate"] == True           
print("All checks passed.")
