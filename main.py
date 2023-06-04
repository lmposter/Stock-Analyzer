"""CSC111 Winter 2023 Course Project: InvestWise

Run this file to start our program.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Department at the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited.

This file is Copyright (c) 2023 Aarya Bhardawaj.
"""
import gui


def run_InvestWise() -> None:
    """Run the program"""
    gui.run_program()


if __name__ == '__main__':
    run_InvestWise()
    import doctest
    doctest.testmod(verbose=True)
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9999']
    })
