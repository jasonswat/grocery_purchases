from parse_receipt import format_date, extract_span_text
from bs4 import BeautifulSoup

def test_format_date():
    assert format_date("Sep. 10, 2025", "%b. %d, %Y") == "2025-09-10"

def test_extract_span_text():
    html = '''
    <div>
        <span class="font-bold">Order Total</span>
        <span>$123.45</span>
    </div>
    '''
    soup = BeautifulSoup(html, 'html.parser')
    total = extract_span_text(soup, "Order Total")
    assert total == "$123.45"