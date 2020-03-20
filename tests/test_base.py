from stockmanager import StockBase


sb = StockBase('MSFT')

def test_attribute():
    assert sb.base_url == 'https://query1.finance.yahoo.com'
    assert sb.scrape_url == 'https://finance.yahoo.com/quote'

def test_get_stock_info():
    #
    sb.get_stock_info()