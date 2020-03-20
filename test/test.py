from ystocks import StockBase

sb = StockBase(ticker="0777.HK")

# result = sb.get_stock_info(start='2020-01-29', end='2020-01-31', interval="30m")

sb.get_general_info()

print(sb.company_info)
