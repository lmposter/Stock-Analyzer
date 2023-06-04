"""CSC111 Winter 2023 Course Project: InvestWise

This file contains the functions and classes to create our decision tree.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Department at the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.

This file is Copyright (c) 2023 Mahe Chen.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Union
import pandas as pd
import numpy as np
from stock_classes import StockScore

STOCK_ROOT = '*'


@dataclass
class DecisionTree:
    """A DecisionTree Class
    The class has two attributes:

    value: It can be either an integer or a set.
    - This attribute holds the value of the decision node of the tree.
    - If the value is an integer, it represents a decision that is made at that node.
    - If the value is a set, it represents all the possible stocks corresponding to the decisions made.

    _subtrees:
    - This is a private dictionary that holds the child nodes of the current node.
    - The keys of the dictionary are the value of Decision made..
    """
    value: int
    _subtrees: Union[dict[int, DecisionTree], StockGraph]

    def __init__(self, value: Union[int, set]) -> None:
        self.value = value
        self._subtrees = {}

    def insert_stock_sequence(self, stocks: list[StockScore]) -> None:
        """A function that inserts a sequence of stocks into self.
        The seven variables correspond to our user preferences, named:
        value_scales, growth_scales, quality_scales, consistency_scales, risk_scales, dividend_scales, and esg_scales.
        We will get the matching scales for each of them by calling scale_calculator on our list of stocks.
        Then, insert the sequence using our helper function: insert_stock to add each stock to the DecisionTree.
        """
        value_scales = scale_calculator(stocks, 'value_score')
        growth_scales = scale_calculator(stocks, 'growth_score')
        quality_scales = scale_calculator(stocks, 'quality_score')
        consistency_scales = scale_calculator(stocks, 'consistency_score')
        risk_scales = scale_calculator(stocks, 'risk_score')
        dividend_scales = scale_calculator(stocks, 'dividend_score')
        esg_scales = scale_calculator(stocks, 'esg_score')

        for stock in stocks:
            moves = [
                self.scaled(stock, value_scales),
                self.scaled(stock, growth_scales),
                self.scaled(stock, quality_scales),
                self.scaled(stock, consistency_scales),
                self.scaled(stock, risk_scales),
                self.scaled(stock, dividend_scales),
                self.scaled(stock, esg_scales)
            ]
            self.insert_stock(moves, stock)

    @staticmethod
    def scaled(stock: StockScore, scales: tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]) -> int:
        """A function that returns a scale.
        Given a stock and a tuple of scales, return the matching scale.
        """
        if stock in scales[0].values:
            return 1
        elif stock in scales[1].values:
            return 2
        elif stock in scales[2].values:
            return 3
        else:
            raise ValueError

    def insert_stock(self, moves: list[int], stock: StockScore, index: int = 0) -> None:
        """A function that insert 1 stock into self.
        This method takes an extra "current index" argument to keep track of the next move in the list to add.
        This method will keep recursing until it reaches the last level, where we put the name of the stock.
        """
        if index == len(moves):
            if isinstance(self._subtrees, StockGraph):
                self._subtrees.add_connection(self._subtrees.first, stock)
            else:
                self._subtrees = StockGraph()
                self._subtrees.first = stock
                self._subtrees.add_stock(stock)
        else:
            if moves[index] not in self._subtrees:
                self.add_subtree(DecisionTree(moves[index]))

            self._subtrees[moves[index]].insert_stock(moves, stock, index + 1)

    def find_stock(self, preferences: list[int]) -> Union[set[StockScore], str]:
        """A function that finds a desired stock for the user.
        This method takes a list of user preferences, recurse until it's last level, and
        Return a list of company symbols based on users preferences.
        If there is no stock, return no stock found.
        """
        curr = self
        for preference in preferences:
            for key in curr._subtrees:
                if preference == key:
                    curr = curr._subtrees[key]
                    break

        if isinstance(curr._subtrees, StockGraph):
            return curr._subtrees.values[curr._subtrees.first].get_recommendations()
        else:
            return 'No Stock Found'

    def add_subtree(self, subtree: DecisionTree) -> None:
        """A function that adds a subtree to this game tree.
        """
        self._subtrees[subtree.value] = subtree


def scale_calculator(stocks: list[StockScore], atr: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """A scale calculator that automatically map stocks into a scale of 3.
        This function pass in a list of stocks, sort them by the given attribute and separate them into 3 equal parts
        based on their score of their given attribute. It returns a tuple that consists 3 dataframes of stocks matching each
        scale.

        Preconditions:
        - attribute is a valid attribute under the Stock dataclass.
        - len(stocks) > 2
    """
    df = pd.DataFrame(stocks)
    sorted_stocks = df.sort_values(atr)[atr].to_numpy()
    median1 = np.median(sorted_stocks[:len(stocks) // 3])
    median2 = np.median(sorted_stocks[2 * (len(stocks) // 3):])
    scales = (
        df[df[atr] < median1],
        df[(df[atr] >= median1) & (df[atr] < median2)],
        df[df[atr] >= median2]
    )
    return scales


class _StockValue:
    """A stock in a StockGraph.
    """
    value: StockScore
    recommendations: set[_StockValue]

    def __init__(self, value: StockScore, recommendations: set[_StockValue]) -> None:
        """Initialize a new vertex with the given stock and recommendations"""
        self.value = value
        self.recommendations = recommendations

    def get_recommendations(self) -> set[StockScore]:
        """Get a set of recommended stocks from the current stock"""
        return {self.value}.union({x.value for x in self.recommendations})


class StockGraph:
    """A StockGraph Class
    """
    first: StockScore
    values: dict[StockScore, _StockValue]

    def __init__(self) -> None:
        """Initialize a new StockGraph"""
        self.values = {}

    def add_stock(self, stock: StockScore) -> None:
        """Add a new stock to StockGraph"""
        self.values[stock] = _StockValue(stock, set())

    def add_connection(self, stock1: StockScore, stock2: StockScore) -> None:
        """Connect the given two stocks in StockGraph
        Preconditions:
            - stock1 != stock2
        """
        if stock1 not in self.values:
            self.add_stock(stock1)
        if stock2 not in self.values:
            self.add_stock(stock2)
        self.values[stock1].recommendations.add(self.values[stock2])
        self.values[stock2].recommendations.add(self.values[stock1])

    def is_empty(self) -> bool:
        """Check if this StockGraph is empty"""
        return len(self.values) == 0
