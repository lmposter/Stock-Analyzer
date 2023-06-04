"""CSC111 Winter 2023 Course Project: InvestWise

This file contains the functions and data types to convert our webscraped data to a csv file.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Departmentat the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.

This file is Copyright (c) 2023 Mahe Chen and Daniel Cheng.
"""
from __future__ import annotations
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from stock_classes import StockData


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}


def write_stock_data(stocks_list: list[str]) -> None:
    """A function which webscrapes company stock data off of yahoo finance using a list of stock symbols and creates a
    new csv file storing all the extracted information.
    """
    data = []
    for stock in stocks_list:
        link = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{stock}?modules=summaryProfile%2CsummaryDetail%2CesgScores%2CincomeStatementHistory%2CdefaultKeyStatistics%2CfinancialData%2CbalanceSheetHistory%2Cprice"
        try:
            r = requests.get(link, headers=HEADERS)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            continue

        soup = BeautifulSoup(r.content, 'html.parser')
        quote_data = soup.find_all('td', class_='Ta(end)')

        if len(quote_data) < 24:  # Skip if data is incomplete
            continue

        stock_data = [stock]
        for i in range(1, len(quote_data)):
            text = quote_data[i].text.strip()
            try:
                value = float(text)
            except ValueError:
                value = np.nan
            stock_data.append(value)

        data.append(stock_data)

    columns = ["symbol", "previousclose", "open", "bid", "ask", "daysrange", "52weekrange", "volume",
               "avgvolume", "marketcap", "beta", "pe_ratio", "eps", "earningsdate", "forwarddividend",
               "exdividenddate", "yield", "dividenddate", "exdividenddate", "yield", "marketcap", "beta",
               "pe_ratio", "eps", "earningsdate", "forwarddividend", "exdividenddate"]

    df = pd.DataFrame(data, columns=columns)
    df.to_csv('data/stock_data.csv', index=False)


def read_stock_data(filename: str) -> dict[str, StockData]:
    """Return a dictionary mapping of a company stock symbol to all of its attributes in the form of StockData from a
    given csv file.

    filename must be a csv file of appropriate format.
    """
    df = pd.read_csv(filename)
    stocks_dict = {}
    for _, row in df.iterrows():
        symbol = str(row["symbol"])
        sector = ""
        company_name = ""
        address = ""
        previous_close = row["previousclose"]
        dividend_yield = row["yield"]
        fifty_two_week_high = np.nan
        fifty_two_week_low = np.nan
        two_hundred_day_average = np.nan
        market_cap = row["marketcap"]
        shares_outstanding = np.nan

        stock_data = StockData(symbol=symbol,
                               sector=sector,
                               company_name=company_name,
                               address=address,
                               previous_close=previous_close,
                               dividend_yield=dividend_yield,
                               fifty_two_week_high=fifty_two_week_high,
                               fifty_two_week_low=fifty_two_week_low,
                               two_hundred_day_average=two_hundred_day_average,
                               market_cap=market_cap,
                               shares_outstanding=shares_outstanding)

        stocks_dict[symbol] = stock_data

    return stocks_dict


def main():
    stocks_list = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'FB']  # Example list of stock symbols
    write_stock_data(stocks_list)
    stocks_dict = read_stock_data('data/stock_data.csv')
    for stock_symbol, stock_data in stocks_dict.items():
        print(stock_symbol, stock_data)


if __name__ == '__main__':
    main()
    import doctest
    doctest.testmod(verbose=True)
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9999', 'W0401', 'E9998', 'R0914']
    })
