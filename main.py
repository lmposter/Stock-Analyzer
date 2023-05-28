"""CSC111 Winter 2023 Course Project: Stockify

This file is where the program runs.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Departmentat the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited. For more information on copyright for CSC111 materials, please consult our Course Syllabus.

This file is Copyright (c) 2023 Mahe Chen, Aarya Bhardawaj, Matthew Yu, and Daniel Cheng.
"""
import gui


def open_stockify() -> None:
    """Run the program"""
    gui.run_program()


if __name__ == '__main__':
    open_stockify()
    import doctest
    doctest.testmod(verbose=True)
    import python_ta
    python_ta.check_all(config={
        'max-line-length': 120,
        'disable': ['E9999']
    })
