from parse_receipt import format_date

def test_format_date():
    assert format_date("Sep. 10, 2025", "%b. %d, %Y") == "2025-09-10"
