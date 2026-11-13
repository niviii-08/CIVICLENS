import pytest
import os
from backend.nlp.scheme_preprocessing import SchemeTextPreprocessor

def test_scheme_text_preprocessor():
    preprocessor = SchemeTextPreprocessor()
    
    raw_scheme = {
        "scheme_name": "Muthulakshmi Reddy Maternity Scheme (cid:12)",
        "department_name": "Health Department",
        "description": "Provides maternity assistance to pregnant women. ????????? ??????????? ???? ????.",
        "objectives": "Reduce maternal mortality \x00 rate.",
        "target_beneficiaries": "Pregnant women below poverty line.",
        "sector_category": "Health & Welfare"
    }
    
    processed = preprocessor.process_record(raw_scheme)
    semantic_text = processed["semantic_text"]
    
    assert processed["scheme_name"] == "Muthulakshmi Reddy Maternity Scheme (cid:12)"
    
    assert "(cid:12)" not in semantic_text
    assert "\x00" not in semantic_text
    
    assert "muthulakshmi reddy maternity scheme" in semantic_text
    assert "health & welfare" in semantic_text
    assert "maternity assistance" in semantic_text
    assert "reduce maternal mortality" in semantic_text
    assert "poverty line" in semantic_text
    
    assert "????????? ??????????? ???? ????" in semantic_text
    
    assert " to " in semantic_text
    assert " below " in semantic_text

    minimal_scheme = {
        "department_name": "Education",
        "description": None,
        "objectives": ""
    }
    
    min_processed = preprocessor.process_record(minimal_scheme)
    assert min_processed["semantic_text"] == "education"
    
    preprocessor.save_config("config/test_nlp_config.json")
    assert os.path.exists("config/test_nlp_config.json")
    os.remove("config/test_nlp_config.json")
    print("All tests passed.")

if __name__ == "__main__":
    test_scheme_text_preprocessor()
