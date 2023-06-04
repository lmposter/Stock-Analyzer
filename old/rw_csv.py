"""CSC111 Winter 2023 Course Project: Stockify

This file contains the functions and data types to convert our webscraped data to a csv file.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Departmentat the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited. For more information on copyright for CSC111 materials, please consult our Course Syllabus.

This file is Copyright (c) 2023 Mahe Chen, Aarya Bhardawaj, Matthew Yu, and Daniel Cheng.
"""
from __future__ import annotations
import csv
from typing import Any

import requests
from stock_classes import *


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}


def write_stock_data(stocks_list: list[str]) -> None:
    """A function which webscrapes company stock data off of yahoo finance using a list of stock symbols and creates a
    new csv file storing all the extracted information.
    """
    with open('data/stock_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["symbol",
                         "sector",
                         "companyname",
                         "address",
                         "previousclose",
                         "dividend_yield",
                         "fifty_two_week_high",
                         "fifty_two_week_low",
                         "two_hundered_day_average",
                         "market_cap",
                         "environment_score",
                         "social_score",
                         "governance_score",
                         "profit_margins",
                         "book_value",
                         "trailing_eps",
                         "shares_outstanding",
                         "total_cash",
                         "debt_to_equity",
                         "return_on_equity",
                         "earnings_growth",
                         "ebitda",
                         "current_liabilities",
                         "revenue"])

        for stock in stocks_list:
            # https://query2.finance.yahoo.com/v10/finance/quoteSummary/ + stock + ?modules=summaryProfile
            # %2CsummaryDetail%2CesgScores%2CincomeStatementHistory%2CdefaultKeyStatistics%2CfinancialData
            # %2CbalanceSheetHistory%2Cprice

            link = "https://query2.finance.yahoo.com/v10/finance/quoteSummary/" + stock + "?"
            link += "modules=summaryProfile%2CsummaryDetail%2CesgScores%2CincomeStatementHistory"
            link += "%2CdefaultKeyStatistics%2CfinancialData%2CbalanceSheetHistory%2Cprice"

            # Get data from website
            # If there is a connection error, then skip this stock
            try:
                r = requests.get(link, headers=HEADERS)
            except ConnectionError:
                continue

            # Required Information
            # If any of the required information are missing, skip the stock
            try:
                data = r.json()['quoteSummary']['result'][0]
            except TypeError:
                continue

            try:
                sector = data["summaryProfile"]["sector"]
                if sector == "":
                    continue

                company_name = data["price"]["longName"]

                address = data["summaryProfile"]["address1"] + ", " + data["summaryProfile"]["city"] + ", "
                try:  # Companies with a headquarters in other countries don't have a state value
                    address += data["summaryProfile"]["state"]
                except KeyError:
                    address += data["summaryProfile"]["country"]

                previous_close = float(data["summaryDetail"]["previousClose"]["raw"])
                fifty_two_week_high = float(data["summaryDetail"]["fiftyTwoWeekHigh"]["raw"])
                fifty_two_week_low = float(data["summaryDetail"]["fiftyTwoWeekLow"]["raw"])
                two_hundred_day_average = float(data["summaryDetail"]["twoHundredDayAverage"]['raw'])
                market_cap = float(data["summaryDetail"]["marketCap"]["raw"])
                shares_outstanding = int(data["defaultKeyStatistics"]["sharesOutstanding"]["raw"])
            except KeyError:
                continue

            # Optional Information
            dividend_yield = get_data(data, ["summaryDetail", "dividendYield", "raw"])
            environment_score = get_data(data, ["esgScores", "environmentScore", "raw"])
            social_score = get_data(data, ["esgScores", "socialScore", "raw"])
            governance_score = get_data(data, ["esgScores", "governanceScore", "raw"])
            profit_margins = get_data(data, ["defaultKeyStatistics", "profitMargins", "raw"])
            book_value = get_data(data, ["defaultKeyStatistics", "bookValue", "raw"])
            trailing_eps = get_data(data, ["defaultKeyStatistics", "trailingEps", "raw"])
            total_cash = get_data(data, ["financialData", "totalCash", "raw"])
            debt_to_equity = get_data(data, ["financialData", "debtToEquity", "raw"])
            return_on_equity = get_data(data, ["financialData", "returnOnEquity", "raw"])
            earnings_growth = get_data(data, ["financialData", "earningsGrowth", "raw"])
            ebitda = get_data(data, ["financialData", "ebitda", "raw"])
            current_liabilities = get_data(data, ["balanceSheetHistory", "balanceSheetStatements", 0,
                                                  "totalCurrentLiabilities", "raw"])
            revenue = get_data(data, ["incomeStatementHistory", "incomeStatementHistory", 0,
                                      "totalRevenue", "raw"])

            writer.writerow([stock,
                             sector,
                             company_name,
                             address,
                             previous_close,
                             dividend_yield,
                             fifty_two_week_high,
                             fifty_two_week_low,
                             two_hundred_day_average,
                             market_cap,
                             environment_score,
                             social_score,
                             governance_score,
                             profit_margins,
                             book_value,
                             trailing_eps,
                             shares_outstanding,
                             total_cash,
                             debt_to_equity,
                             return_on_equity,
                             earnings_growth,
                             ebitda,
                             current_liabilities,
                             revenue])


def read_stock_data(filename: str) -> dict[str, StockData]:
    """Return a dictionary mapping of a company stock symbol to all of its attributes in the form of StockData from a
    given csv file.

    filename must be a csv file of approriate format.
    """
    raw_stocks_to_dict = {}
    with open(filename) as file:
        reader = csv.reader(file)

        # Skip first code
        next(reader)

        for row in reader:
            symbol = str(row[0])
            sector = str(row[1])
            company_name = str(row[2])
            address = str(row[3])
            previous_close = float(row[4])
            fifty_two_week_high = float(row[6])
            fifty_two_week_low = float(row[7])
            two_hundred_day_average = float(row[8])
            market_cap = float(row[9])
            shares_outstanding = int(row[16])

            dividend_yield = get_data(row, [5])
            environment_score = get_data(row, [10])
            social_score = get_data(row, [11])
            governance_score = get_data(row, [12])
            profit_margins = get_data(row, [13])
            book_value = get_data(row, [14])
            trailing_eps = get_data(row, [15])
            total_cash = get_data(row, [17])
            debt_to_equity = get_data(row, [18])
            return_on_equity = get_data(row, [19])
            earnings_growth = get_data(row, [20])
            ebitda = get_data(row, [21])
            current_liabilities = get_data(row, [22])
            revenue = get_data(row, [23])

            raw_stocks_to_dict[symbol] = StockData(symbol=symbol,
                                                   sector=sector,
                                                   company_name=company_name,
                                                   address=address,
                                                   previous_close=previous_close,
                                                   dividend_yield=dividend_yield,
                                                   fifty_two_week_high=fifty_two_week_high,
                                                   fifty_two_week_low=fifty_two_week_low,
                                                   two_hundred_day_average=two_hundred_day_average,
                                                   market_cap=market_cap,
                                                   environment_score=environment_score,
                                                   social_score=social_score,
                                                   governance_score=governance_score,
                                                   profit_margins=profit_margins,
                                                   book_value=book_value,
                                                   trailing_eps=trailing_eps,
                                                   shares_outstanding=shares_outstanding,
                                                   total_cash=total_cash,
                                                   debt_to_equity=debt_to_equity,
                                                   return_on_equity=return_on_equity,
                                                   earnings_growth=earnings_growth,
                                                   ebitda=ebitda,
                                                   current_liabilities=current_liabilities,
                                                   revenue=revenue)

    return raw_stocks_to_dict


def get_data(data: dict | list, keys: list[Any]) -> float | None:
    """
    Return the data stored at data[keys[0][keys[1]][keys[2]]... while checking
    for KeyError, ValueError, TypeError  and IndexError (which might result from
    missing/inadequate data)

    Return None if any of the above error is encountered.
    """
    current_key = keys[0]

    try:
        if len(keys) == 1:
            return float(data[current_key])
        return get_data(data[current_key], keys[1:])
    except KeyError:
        return None
    except ValueError:
        return None
    except TypeError:
        return None
    except IndexError:
        return None


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9999', 'W0401', 'E9998', 'R0914']
    })
