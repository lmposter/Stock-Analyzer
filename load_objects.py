""""
CSC111 Winter 2022 Project: Stockify - Stock Recommender

This python module contains the functions necessary to load our decision tree with data from our dataset files.

Copyright and Usage Information
===============================
This file is provided solely for the personal and private use. All forms of distribution of this code, whether as given
or with any changes, are expressly prohibited.

This file is Copyright (c) 2023 Matthew Yu, Mahe Chen, Aarya Bhardawaj and Daniel Cheng
"""
from decision_computation import DecisionTree
from rw_csv import *


def load_stock_name_list(filename: str) -> list[str]:
    """
    Return a list of stock names from a given csv file. filename must be a csv file
    where the first cell of each row is a stock symbol.
    """
    symbol_list = []
    with open(filename) as file:
        reader = csv.reader(file)

        for row in reader:
            symbol_list.append(row[0])
    return symbol_list


def get_sector_averages_dict(stocks: list[StockData]) -> dict[str, SectorAverage]:
    """
    Return a dictionary mapping sector to its SectorAverage for each company stock.
    """
    stocks_in_sector_dict = {}
    sector_averages_dict = {}

    for stock in stocks:
        if stock.sector not in stocks_in_sector_dict:
            stocks_in_sector_dict[stock.sector] = [stock]
        else:
            stocks_in_sector_dict[stock.sector].append(stock)

    for sector in stocks_in_sector_dict:
        sector_averages_dict[sector] = SectorAverage(stocks_in_sector_dict[sector])

    return sector_averages_dict


def get_stock_values_dict(stocks: list[StockData]) -> dict[str, StockScore]:
    """
    Return a dictionary mapping company stocks symbols to StockScore for each company stock.
    """
    stock_values_dict = {}
    for stock in stocks:
        stock_values_dict[stock.symbol] = StockScore(stock)
    return stock_values_dict


def get_decision_tree(filename: str) -> DecisionTree:
    """
    Return a decision tree with every stock in filename.
    filename must be a csv file with stock symbols and each stock's attributes (i.e. same format as the file
    generated from write_stock_data function).
    """
    stock_data = read_stock_data(filename)
    sector_averages = get_sector_averages_dict(list(stock_data.values()))  # dict

    for stock in stock_data.values():
        stock.update_sector_average(sector_averages)

    stock_scores = get_stock_values_dict(list(stock_data.values()))
    tree = DecisionTree(0)
    tree.insert_stock_sequence(list(stock_scores.values()))
    return tree


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9999', 'W0401', 'E9998']
    })
