from unittest import TestCase
from stockmanager import StockBase

class TestStockBase(TestCase):

    def setUp(self):
        pass

    def tearDown(selfs):
        pass

    def test_attributes(self):
        sb = StockBase()
        self.assertEqual(sb.base_url, 'https://query1.finance.yahoo.com')
        self.assertEqual(sb.scrape_url, 'https://finance.yahoo.com/quote')

