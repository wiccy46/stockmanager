from stockmanager import StockBase

def test_attribute():
    sb = StockBase('MSFT')
    assert sb.base_url == 'https://query1.finance.yahoo.com'
    assert sb.scrape_url == 'https://finance.yahoo.com/quote'