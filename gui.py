"""CSC111 Winter 2023 Course Project: Stockify

This file contains functions and classes for an interactive user interface.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of the Computer Science Departmentat the
University of Toronto St. George campus. All forms of distribution of this code, whether as given or with any changes,
are expressly prohibited. For more information on copyright for CSC111 materials, please consult our Course Syllabus.

This file is Copyright (c) 2023 Mahe Chen, Aarya Bhardawaj, Matthew Yu, and Daniel Cheng.
"""
from __future__ import annotations
from load_objects import *

import pygame

# UI will resize to fill user's screen, provided that the user's screen is equal or larger than these min values. If
# not, user screen will be set to default size of 1400 x 800
MIN_WIDTH = 1000
MIN_HEIGHT = 600
# colors
PALETTE = {'black': (0, 0, 0), 'red': (255, 0, 0), 'green': (0, 255, 0), 'white': (255, 255, 255), 'blue': (0, 0, 255),
           'yellow': (255, 255, 0), 'pink': (255, 192, 203), 'gray': (128, 128, 128), 'orange': (255, 95, 31)}
BACKGROUND_IMAGE = 'menu_image.jpg'


def run_program() -> None:
    """Run user interface and program"""
    # Set up
    dim_variables = _set_dimension_variables()  # set dimensions of UI screen and items on screen
    # Initialize main screen
    screen = init_screen(dim_variables['screen_width'], dim_variables['screen_height'])
    pygame.display.set_caption('StockifyPro')  # Set title on window
    read_csv(dim_variables, screen)  # read in tree

    #  initialize all panels(do this only once!) and store each pannel's buttons in dict
    background = _load_in_image(BACKGROUND_IMAGE, dim_variables['screen_width'], dim_variables['screen_height'], 100)

    screen_buttons = {}  # dict of panel identifier to list of buttons on panel
    screen_buttons['menu'] = init_main_menu(dim_variables)
    select_one_info = init_select_one(dim_variables)
    screen_buttons['select_one'], select_one_button_groups, next_button = select_one_info[0], select_one_info[1], \
        select_one_info[2]
    select_many_info = init_select_many(dim_variables)
    screen_buttons['select_many'], button_column = select_many_info[0], select_many_info[1]
    results_info = init_results(dim_variables, button_column, next_button)
    screen_buttons['results'], next_stock_buttons = results_info[0], results_info[1]
    screen_buttons['re_results'], screen_buttons['compute'] = [], []  # no buttons for loading
    screen_buttons['instruct'] = init_instructions(dim_variables)
    screen_buttons['credits'] = init_credits(dim_variables)
    screen_buttons['warning'] = init_warning(dim_variables)

    # panel identifier, 'menu' - menu panel, 'select_one' - select one panel, 'select_many' - select all panel,
    # 'results' - results panel, 're-results' - redisplay results, 'compute' - caclulate results, 'instruct' -
    # instructions panel, 'quit' - quit, 'credits' - credits panel, 'warning' - warning to continue with update files
    game_state = 'menu'
    new_game_state = 'menu'

    # set screen to start
    update_screen(dim_variables, screen, background, new_game_state, screen_buttons, select_one_button_groups,
                  button_column, next_stock_buttons[0])

    run = True
    while run:  # display loop
        # since this UI has limited animation, only change screen when necessary(when user potentially clicks a button),
        # not for every loop animation. More efficient!
        for event in pygame.event.get():  # grab events from queue and handles them
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # if user does left mouse click
                # Moved code below to 2 helper functions to reduce some nesting
                # check if clicked on a button
                new_game_state = _check_button_action(pygame.mouse.get_pos(), screen_buttons[game_state], game_state,
                                                      screen)
                # potentially update screen and get whether to keep running and new game state
                run, game_state = _check_update(game_state, new_game_state, dim_variables, screen, background,
                                                screen_buttons,
                                                select_one_button_groups, button_column, next_stock_buttons[0])
        pygame.display.update()  # like pygame.display.flip but only updates portion of screen, or entire screen if no
        # argument passed
    pygame.quit()  # ends pygame


def _check_button_action(pos: tuple[int, int], current_group: list[Button], game_state: str,
                         screen: pygame.Surface) -> str:
    """Check if user clicked on a button and return new game state"""
    for button in current_group:
        if button.rect.collidepoint(pos):
            return button.action(game_state, screen)  # perform button action
            # early return as no overlapping buttons, only single button can be clicked at once
    return game_state  # otherwise no button clicked so keep game state same


def _check_update(game_state: str, new_game_state: str, dim: dict[str: int], screen: pygame.Surface,
                  background: pygame.Surface, screen_buttons: dict[str: list[Button]],
                  select_one_button_groups: list[ButtonGroup], button_column: list[Checkbox],
                  next_stock_button: NextStockButton) -> tuple[bool, str]:
    """Check whether to update screen. Return tuple with whether to keep running, and updated game state."""
    if new_game_state != game_state:
        _fade_out(dim, screen, 0.4)  # fade out animation for transition
        new_game_state = update_screen(dim, screen, background, new_game_state, screen_buttons,
                                       select_one_button_groups, button_column, next_stock_button)
        if new_game_state == 'quit':  # want to end program, return any string
            return (False, '')
        else:  # update game state
            return (True, new_game_state)
    else:  # new_game_state same as current, do nothing
        return (True, game_state)


def read_csv(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Read in csv file of stock information
    """
    _loading_screen(dim, screen)
    read_stock_data("data/stock_data.csv")


def update_csv(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Update csv file with new information
    """
    _loading_screen(dim, screen)
    write_stock_data(load_stock_name_list("data/stock_symbols.csv"))
    read_csv(dim, screen)


def get_recommended_stocks(choices: list[int], sectors: set[str]) -> list[StockScore]:
    """
    Given user responses, use tree to calculate recommended stocks and display them on screen
    user_responses[0] is a list of 7 integers, one for each question, each integer either 0(low), 1(medium), or 2(high)
    Question order: Growth, quality, consistency, dividend, social, risk, sentiment
    user_responses[1] is a list of 11 bools, one for if include each sector or not
    Sector Order: healthcare, materials, real estate, consumer staples, consumer discretionary, utilities, energy,
    industrials, consumer services, financials, technology
    """
    tree = get_decision_tree("data/stock_data.csv")
    set_stocks = tree.find_stock(choices)
    if isinstance(set_stocks, str):
        return []
    else:
        lst_stock_so_far = []
        for stock in set_stocks:
            if stock.stock_data.sector in sectors:
                lst_stock_so_far.append(stock)

        return lst_stock_so_far


def _set_dimension_variables() -> dict[str: int]:
    """Set dimension variables that determine positioning of text and buttons on screen"""
    # Set dimensions relative to user screen size. If user screen not large enough, then the UI won't display/work
    # properly so just set dimensions to minimum screen dimensions
    pygame.display.init()
    x, y = pygame.display.set_mode().get_size()
    variables = {}
    if x >= MIN_WIDTH and y >= MIN_HEIGHT:
        variables['screen_width'] = x
        variables['screen_height'] = y
    else:
        variables['screen_width'] = MIN_WIDTH
        variables['screen_height'] = MIN_HEIGHT
    variables['bottom_margin'] = variables['screen_height'] // 8
    variables['side_margin'] = variables['screen_width'] // 10
    variables['select_one_start_in_x'] = variables['screen_width'] // 2
    variables['select_one_spacing_x'] = variables['side_margin'] * 2
    variables['select_one_start_in_y'] = variables['bottom_margin'] * 2
    variables['select_one_spacing_y'] = (variables['bottom_margin'] * 3) // 4
    variables['select_many_start_in_x'] = variables['side_margin']
    variables['select_many_spacing_x'] = variables['screen_width'] // 2
    variables['select_many_start_in_y'] = (variables['bottom_margin'] * 8) // 5
    variables['select_many_spacing_y'] = variables['bottom_margin']
    variables['checkbox_size'] = variables['screen_height'] // 20
    variables['navi_button_font_size'] = variables['screen_height'] // 30
    variables['navi_button_spacing'] = variables['checkbox_size'] * 2
    variables['warning_buttons_start_in'] = (variables['screen_height']) // 2
    return variables


def init_screen(screen_width: int, screen_height: int) -> pygame.Surface:
    """
    Initialize pygame screen to use for UI
    """
    pygame.font.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.flip()
    pygame.event.clear()  # clear event queue
    return screen


def init_main_menu(dim: dict[str: int]) -> list[Button]:
    """
    Initialize main menu panel buttons
    """
    default_font = pygame.font.SysFont("serif", 50)

    word = 'Search'
    start_button = NaviButton(word, 'select_one', 20, default_font,
                              _center_coordinates((0, (dim['screen_height']) // 4), dim['screen_width'],
                                                  (dim['bottom_margin'] * 3) // 2, default_font, word))
    word = 'Instructions'
    instructions_button = NaviButton(word, 'instruct', 20, default_font,
                                     _center_coordinates(
                                         (0, start_button.rect.topleft[1] + start_button.rect.height),
                                         dim['screen_width'], (dim['bottom_margin'] * 3) // 2, default_font, word))
    word = 'Credits'
    credits_button = NaviButton(word, 'credits', 20, default_font, _center_coordinates(
        (0, instructions_button.rect.topleft[1] + instructions_button.rect.height),
        dim['screen_width'], (dim['bottom_margin'] * 3) // 2, default_font, word))

    word = 'Update Stocks'
    update_button = NaviButton(word, 'warning', 20, default_font, _center_coordinates(
        (0, credits_button.rect.topleft[1] + credits_button.rect.height),
        dim['screen_width'], (dim['bottom_margin'] * 3) // 2, default_font, word))

    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack",
                                                                     dim['navi_button_font_size']), 'QUIT'))
    buttons_on_screen = [instructions_button, start_button, credits_button, update_button, quit_button]
    return buttons_on_screen


def init_instructions(dim: dict[str: int]) -> list[Button]:
    """
    Initialize instructions panel buttons
    """
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'])
    word = 'Back'
    menu_button = NaviButton(word, 'menu', 10, default_font,
                             _center_coordinates((0, dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'], default_font, word))
    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    buttons_on_screen = [menu_button, quit_button]
    return buttons_on_screen


def init_credits(dim: dict[str: int]) -> list[Button]:
    """
    Initialize credits panel buttons
    """
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'])
    word = 'Back'
    menu_button = NaviButton(word, 'menu', 10, default_font,
                             _center_coordinates((0, dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'], default_font, word))
    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    buttons_on_screen = [menu_button, quit_button]
    return buttons_on_screen


def init_warning(dim: dict[str: int]) -> list[Button]:
    """Initialize warning screen buttons"""
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'] * 2)

    word = 'Confirm'
    confirm_button = NaviButton(word, 'update', 20, default_font,
                                _center_coordinates((0, dim['warning_buttons_start_in']), dim['screen_width'],
                                                    dim['bottom_margin'] * 2, default_font, word))

    word = 'Back'
    menu_button = NaviButton(word, 'menu', 20, default_font, _center_coordinates(
        (0, dim['warning_buttons_start_in'] + confirm_button.rect.height + dim['bottom_margin'] // 2),
        dim['screen_width'], dim['bottom_margin'] * 2, default_font, word))

    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                                 dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    buttons_on_screen = [confirm_button, menu_button, quit_button]
    return buttons_on_screen


def init_select_one(dim: dict[str: int]) -> tuple[list[Button], list[ButtonGroup], SelectOneNextButton]:
    """
    Initialize select one panel buttons
    """
    # navigation buttons
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'])
    word = 'Menu'
    corner = _center_coordinates((0, dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                 dim['bottom_margin'], default_font, word)
    menu_button = NaviButton(word, 'menu', 10, default_font, corner)
    word = 'Next'
    next_button = SelectOneNextButton(word, 'select_many', 10, default_font,
                                      (corner[0] + menu_button.rect.width + dim['navi_button_spacing'], corner[1]))
    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']),
                                                 dim['side_margin'], dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    # Checkboxes
    buttons_so_far = []
    button_groups_so_far = []
    y_coor = dim['select_one_start_in_y']
    for _ in range(7):  # format checkboxes into 7 rows, each row with 3 columns
        x_coor = dim['select_one_start_in_x']
        buttons = []
        new_button_group = ButtonGroup()
        for _ in range(3):
            new_checkbox = SelectOneCheckbox(new_button_group, next_button, (x_coor, y_coor), dim['checkbox_size'],
                                             dim['checkbox_size'])
            buttons.append(new_checkbox)
            buttons_so_far.append(new_checkbox)
            x_coor += dim['select_one_spacing_x']

        new_button_group.add_buttons(buttons)
        button_groups_so_far.append(new_button_group)
        y_coor += dim['select_one_spacing_y']

    # add buttons to button lists
    next_button.add_button_groups(button_groups_so_far)
    buttons_so_far.extend([menu_button, quit_button, next_button])
    return (buttons_so_far, button_groups_so_far, next_button)


def init_select_many(dim: dict[str: int]) -> tuple[list[Button], list[Checkbox]]:
    """
    Initialize select many panel buttons
    """
    # Checkboxes
    buttons_so_far = []
    checkboxes_so_far = []
    x_coor, y_coor = dim['select_many_start_in_x'], dim['select_many_start_in_y']
    for i in range(2):  # format checkboxes into 2 columns
        for _ in range(6 - i):
            new_checkbox = Checkbox((x_coor, y_coor), dim['checkbox_size'], dim['checkbox_size'])
            checkboxes_so_far.append(new_checkbox)
            buttons_so_far.append(new_checkbox)
            y_coor += dim['select_many_spacing_y']
        y_coor = dim['select_many_start_in_y']
        x_coor += dim['select_many_spacing_x']

    # navigation buttons
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'])
    word = 'Back'
    corner = _center_coordinates((0, dim['screen_height'] - dim['bottom_margin']), dim['side_margin'],
                                 dim['bottom_margin'], default_font, word)
    back_button = NaviButton(word, 'select_one', 10, default_font, corner)
    select_all_button = SelectAllButton(checkboxes_so_far, 10, default_font,
                                        (corner[0] + back_button.rect.width + dim['navi_button_spacing'], corner[1]))
    deselect_all_button = DeselectAllButton(checkboxes_so_far, 10, default_font, (
        select_all_button.rect.topleft[0] + select_all_button.rect.width + dim['navi_button_spacing'], corner[1]))
    word = 'Results!'
    results_button = NaviButton(word, 'compute', 10, default_font, (
        deselect_all_button.rect.topleft[0] + deselect_all_button.rect.width + dim['navi_button_spacing'], corner[1]))
    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']),
                                                 dim['side_margin'], dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    buttons_so_far.extend([back_button, select_all_button, deselect_all_button, results_button, quit_button])
    return (buttons_so_far, checkboxes_so_far)


def init_results(dim: dict[str: int], button_column: list[Checkbox], next_button: SelectOneNextButton) -> \
        tuple[list[Button], tuple[NextStockButton, NextStockButton]]:
    """
    Initialize results panel buttons
    """
    default_font = pygame.font.SysFont("serif", dim['navi_button_font_size'])
    # next and previous stock buttons
    corner = _center_coordinates((0, dim['screen_height'] - dim['bottom_margin']), (dim['side_margin'] * 3) // 2,
                                 dim['bottom_margin'], default_font, 'Previous')
    prev_stock_button = NextStockButton([], '←', -1, 10, default_font, corner)
    next_stock_button = NextStockButton([], '→', 1, 10, default_font, (prev_stock_button.rect.topleft[0]
                                                                       + prev_stock_button.rect.width
                                                                       + dim['navi_button_spacing'] // 3, corner[1]))
    prev_stock_button.set_other_button(next_stock_button)
    next_stock_button.set_other_button(prev_stock_button)

    # restart and quit buttons
    restart_button = ResetButton(button_column, next_button, (prev_stock_button, next_stock_button), 'Restart', 10,
                                 default_font, (next_stock_button.rect.topleft[0] + next_stock_button.rect.width
                                                + dim['navi_button_spacing'], corner[1]))
    quit_button = QuitButton(10, pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                             _center_coordinates((dim['screen_width'] - dim['side_margin'],
                                                  dim['screen_height'] - dim['bottom_margin']),
                                                 dim['side_margin'], dim['bottom_margin'],
                                                 pygame.font.SysFont("arialblack", dim['navi_button_font_size']),
                                                 'QUIT'))
    buttons_so_far = [restart_button, prev_stock_button, next_stock_button, quit_button]
    return (buttons_so_far, (prev_stock_button, next_stock_button))


def display_menu(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Display menu panel text
    """
    word = 'StockifyPro'
    font = pygame.font.SysFont("serif", 150)
    _draw_text(screen, word, _center_coordinates((0, 0), dim['screen_width'], dim['bottom_margin'] * 2, font, word),
               font, PALETTE['white'])


def display_instructions(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Display text for instruction screen
    """
    # convert pararaph into list of strings that will fit on screen
    paragraph = 'Welcome to StockifyPro, the stock recommender! You input the attributes for your preferred stock, ' \
                'and we will return the best, up to date stocks for you to purchase. You will have the option to ' \
                'select your preferences for many stock attributes, and narrow your recommendations to stock sector. ' \
                'Use buttons to navigate through the program. You may also choose to update our stock database. To ' \
                'get started, simply return to menu and click Start!'

    font = pygame.font.SysFont("serif", 20)
    lst_string = _split_str_to_paragraph(paragraph, dim['side_margin'] // 2,
                                         dim['screen_width'] - dim['side_margin'], font)
    y_pos = dim['bottom_margin'] // 2
    for sentence in lst_string:
        _draw_text(screen, sentence, (dim['side_margin'] // 2, y_pos), font, PALETTE['white'])
        y_pos += (font.size(sentence)[1] * 3) // 2

    lst_desc = ['Stock Attribute Descriptions:', 'Value: Value of stock, calculated with price earning ratios and'
                + ' price to book value ratios', 'Growth: Growth potential of stock',
                'Quality: Quality of company\'s operations, calculated with profitability, cash flow, and debt levels',
                'Consistency: Predicted stability of company\'s financial performance',
                'Risk: risk involved with investing in stock, calculated with volatility, market and financial risk',
                'Dividend: Distribution of company\'s earnings to shareholders',
                'ESG: Environmental, social and governance factors. Company\'s social responsibility and impact']
    y_pos += (dim['bottom_margin']) // 2
    for sentence in lst_desc:
        _draw_text(screen, sentence, (dim['side_margin'] // 2, y_pos), font, PALETTE['white'])
        y_pos += (font.size(sentence)[1] * 3) // 2


def display_credits(dim: dict[str: int], screen: pygame.Surface) -> None:
    """Display credits screen"""
    paragraph = 'Copyright and Usage Information: This file is provided solely for the personal and private use. All ' \
                'forms of distribution of this code, whether as given or with any changes, are expressly prohibited. ' \
                'This file is Copyright (c) 2023 Matthew Yu, Mahe Chen, Aarya Bhardawaj and Daniel Cheng'
    font = pygame.font.SysFont("serif", 20)
    lst_string = _split_str_to_paragraph(paragraph, dim['side_margin'] // 2,
                                         dim['screen_width'] - dim['side_margin'], font)
    y_pos = dim['bottom_margin'] // 2
    for sentence in lst_string:
        _draw_text(screen, sentence, (dim['side_margin'] // 2, y_pos), font, PALETTE['white'])
        y_pos += (font.size(sentence)[1] * 3) // 2

    y_pos += dim['bottom_margin'] // 2
    additional_info = ['Developers: Matthew Yu, Mahe Chen, Aarya Bhardawaj, Daniel Cheng',
                       'Additional Resources: ', 'Testing: python-ta~=2.4.2', 'Graphics: pygame==2.1.3.dev8',
                       'Webscraping: requests==2.28.2', 'Background Image Link: https://www.freepik.com/free-vector'
                       + '/5g-networking-technology-background-with-blue-digital-line_16406299.htm']
    for sentence in additional_info:
        _draw_text(screen, sentence, (dim['side_margin'] // 2, y_pos), font, PALETTE['white'])
        y_pos += (font.size(sentence)[1] * 3) // 2


def display_warning(dim: dict[str: int], screen: pygame.Surface) -> None:
    """Display text for warning screen"""
    word = 'Are you sure you want to continue? This may take a while!'
    font = pygame.font.SysFont('cambria', 40)
    _draw_text(screen, word,
               _center_coordinates((0, 0), dim['screen_width'], dim['warning_buttons_start_in'] // 2, font, word), font,
               PALETTE['white'])
    word = 'Please do not exit during the process'
    _draw_text(screen, word,
               _center_coordinates((0, dim['warning_buttons_start_in'] // 2), dim['screen_width'],
                                   dim['warning_buttons_start_in'] // 2, font, word), font, PALETTE['white'])


def display_select_one(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Display text for select one screen
    """
    title_margin = dim['bottom_margin']
    label_margin = dim['select_one_start_in_y']

    # Format column headers
    word = 'Select One From Each Category'
    font = pygame.font.SysFont('cambria', 60)
    _draw_text(screen, word, _center_coordinates((0, 0), dim['screen_width'], title_margin, font, word), font,
               PALETTE['green'])
    half_space = (dim['select_one_spacing_x'] - dim['checkbox_size']) // 2
    font = pygame.font.SysFont('cambria', 50)
    startx, starty, span = dim['select_one_start_in_x'] - half_space, title_margin, (2 * half_space) + dim[
        'checkbox_size']
    word = 'Low'
    _draw_text(screen, word, _center_coordinates((startx, starty), span, label_margin - title_margin, font, word), font,
               PALETTE['white'])
    word = 'Medium'
    _draw_text(screen, word,
               _center_coordinates((startx + span, starty), span, label_margin - title_margin, font, word), font,
               PALETTE['white'])
    word = 'High'
    _draw_text(screen, word,
               _center_coordinates((startx + 2 * span, starty), span, label_margin - title_margin, font, word),
               font, PALETTE['white'])

    # format row labels
    lst_options = ['Value', 'Growth', 'Quality', 'Consistency', 'Risk', 'Dividend', 'ESG']
    font = pygame.font.SysFont("playfair", 50)
    x_coor = dim['side_margin'] // 2
    y_coor = label_margin
    for option in lst_options:
        _draw_text(screen, option, (x_coor, y_coor), font, PALETTE['orange'])
        y_coor += dim['select_one_spacing_y']


def display_select_many(dim: dict[str: int], screen: pygame.Surface) -> None:
    """
    Display select many screen text
    """
    word = 'Select All Sectors Desired'
    font = pygame.font.SysFont('cambria', 70)
    _draw_text(screen, word,
               _center_coordinates((0, 0), dim['screen_width'], dim['select_many_start_in_y'], font, word),
               font,
               PALETTE['green'])

    # format checkbox text beside-labels
    lst_options = ['Healthcare', 'Basic Materials', 'Real Estate', 'Consumer Defensive', 'Consumer Cyclical',
                   'Utilities', 'Energy', 'Industrials', 'Consumer Services', 'Financial Services', 'Technology']
    font = pygame.font.SysFont("playfair", 50)
    x_coor = dim['select_many_start_in_x'] + 2 * dim['checkbox_size']
    for i in range(2):
        y_coor = dim['select_many_start_in_y']
        for j in range(6 - i):
            option = lst_options[(i * 6) + j]
            _draw_text(screen, option, (x_coor, y_coor), font, PALETTE['orange'])
            y_coor += dim['select_many_spacing_y']
        x_coor += dim['select_many_spacing_x']


def display_results(dim: dict[str: int], screen: pygame.Surface, stock_button: NextStockButton) -> None:
    """
    Display results to user. Since NextStockButtons linked to each other, only need 1
    """
    font = pygame.font.SysFont("serif", 40)
    if stock_button.stocks != []:  # if at least 1 stock recommendation
        # recommended stocks title
        title_start_in = dim['bottom_margin']
        title_font = pygame.font.SysFont('cambria', 75)
        word = 'Recommended Stock ' + str(stock_button.get_current_stock_index() + 1)
        corner = _center_coordinates((0, 0), dim['screen_width'], title_start_in, title_font, word)
        _draw_text(screen, word, corner, title_font, PALETTE['green'])

        # get information for current stock
        current_stock = stock_button.get_current_stock()
        x_coor = dim['side_margin'] // 2
        y_coor = title_start_in + (dim['bottom_margin'] // 4)
        lst_info = ['Symbol: ' + current_stock.stock_data.symbol,
                    'Company Name: ' + current_stock.stock_data.company_name,
                    'Sector: ' + current_stock.stock_data.sector,
                    'Address: ' + current_stock.stock_data.address,
                    'Market Cap: ' + str(round(current_stock.stock_data.market_cap)),
                    'Stock Price: ' + str(round(current_stock.stock_data.previous_close, 2))]

        # display info for current stock
        for info in lst_info:
            _draw_text(screen, info, (x_coor, y_coor), font, PALETTE['white'])
            y_coor += (dim['bottom_margin'] * 2) // 3

        # display description for current stock
        desc_info = _split_str_to_paragraph(current_stock.stock_data.company_name, x_coor, dim['screen_width']
                                            - dim['side_margin'], font)
        for info in desc_info:
            _draw_text(screen, info, (x_coor, y_coor), font, PALETTE['white'])
            y_coor += (dim['bottom_margin'] * 2) // 3
    else:  # if no stock recommendations
        _draw_text(screen, 'Sorry, no recommendations', (dim['side_margin'], dim['bottom_margin']), font,
                   PALETTE['white'])


def _get_user_response(button_groups: list[ButtonGroup], button_column: list[Checkbox]) -> tuple[list[int], list[bool]]:
    """
    Helper method, converts user's input into format to be used in search
    """
    # user's inputs from select one page become a list of integers, where each element corresponds to each question and
    # is either 0 for low, 1 for medium or 2 for high
    button_group_results_so_far = []
    # user's inputs from select many page become a list of bools, where each element corresponds to a sector and if that
    # sector was selected
    button_column_results_so_far = []

    for button_group in button_groups:
        button_group_results_so_far.append(button_group.get_selected_index() + 1)
    for checkbox in button_column:
        button_column_results_so_far.append(checkbox.is_selected())
    return (button_group_results_so_far, button_column_results_so_far)


def convert_bool_to_sectors(sectors: list[bool]) -> set[str]:
    """
    Given list of sectors to include as bool, return sectors to narrow search by
    Preconditions:
        - len(sectors) == 7
    """
    sectors_names = set()
    if sectors[0]:
        sectors_names.add("Healthcare")
    if sectors[1]:
        sectors_names.add("Basic Materials")
    if sectors[2]:
        sectors_names.add("Real Estate")
    if sectors[3]:
        sectors_names.add("Consumer Defensive")
    if sectors[4]:
        sectors_names.add("Consumer Cyclical")
    if sectors[5]:
        sectors_names.add("Utilities")
    if sectors[6]:
        sectors_names.add("Energy")
    if sectors[7]:
        sectors_names.add("Industrials")
    if sectors[8]:
        sectors_names.add("Communication Services")
    if sectors[9]:
        sectors_names.add("Financial Services")
    if sectors[10]:
        sectors_names.add("Technology")
    return sectors_names


def set_up_results(button_groups: list[ButtonGroup], button_column: list[Checkbox],
                   stock_button: NextStockButton) -> None:
    """
    Given user input, get recommended stocks and update stock button accordingly
    """
    user_responses = _get_user_response(button_groups, button_column)
    sector_names = convert_bool_to_sectors(user_responses[1])
    lst_stocks = get_recommended_stocks(user_responses[0], sector_names)
    if lst_stocks != []:
        stock_button.update_stocks(lst_stocks)


def update_screen(dim: dict[str: int], screen: pygame.Surface, background: pygame.Surface, next_screen: str,
                  screen_buttons: dict[int: list[Button]], button_groups: list[ButtonGroup],
                  button_column: list[Checkbox], stock_button: NextStockButton) -> str:
    """
    Update screen to next one, and return whether to continue simulating. Do a fade in animation too! This function
    crucial for moving between panels, and brings whole program together!
    Preconditions:
        - next_screen in {'menu', 'select_one', 'select_many', 'results', 're-results', 'compute', 'instruct', 'quit'}
    """
    if next_screen == 'quit':  # signal for quit
        return next_screen
    elif next_screen == 'compute':  # compute results once(its time-consuming!)
        _loading_screen(dim, screen)  # display loading screen(may take a while)
        set_up_results(button_groups, button_column, stock_button)
        # then display results screen with recommended stocks
        update_screen(dim, screen, background, 'results', screen_buttons, button_groups, button_column, stock_button)
        return 'results'
    elif next_screen == 're-results':
        # display results screen with recommended stocks. Re-results indicate new stock's information to be displayed
        # in results
        update_screen(dim, screen, background, 'results', screen_buttons, button_groups, button_column, stock_button)
        return 'results'
    elif next_screen == 'update':  # update csv file with new info
        update_csv(dim, screen)
        update_screen(dim, screen, background, 'menu', screen_buttons, button_groups, button_column, stock_button)
        return 'menu'
    else:
        screen.fill(PALETTE['black'])
        transition_screen = pygame.Surface((dim['screen_width'], dim['screen_height']))
        transition_screen.fill(PALETTE['black'])

        for i in range(255, 0, -6):  # redisplay screen for fade in animation
            screen.blit(background, (0, 0))
            buttons = screen_buttons[next_screen]
            if next_screen == 'menu':
                display_menu(dim, screen)
            elif next_screen == 'select_one':
                display_select_one(dim, screen)
            elif next_screen == 'select_many':
                display_select_many(dim, screen)
            elif next_screen == 'results':
                display_results(dim, screen, stock_button)
            elif next_screen == 'credits':
                display_credits(dim, screen)
            elif next_screen == 'warning':
                display_warning(dim, screen)
            else:  # next_screen == 'instruct'
                display_instructions(dim, screen)
            for button in buttons:
                button.draw(screen)

            transition_screen.set_alpha(i)
            screen.blit(transition_screen, (0, 0))
            pygame.display.update()

        return next_screen


def _draw_text(screen: pygame.Surface, word: str, coor: tuple[int, int], font: pygame.font,
               color: tuple[int, int, int] = PALETTE['black']) -> None:
    """
    Display text on given screen
    """
    word = font.render(word, True, color)
    screen.blit(word, coor)


def _split_str_to_paragraph(paragraph: str, x_start: int, width: int, font: pygame.font) -> list[str]:
    """Split paragraph to list of strings, such that each string is a sentence that fits in area"""
    str_so_far = []
    words = paragraph.split(' ')  # get each word
    x_end = x_start + width
    x_pos = x_start
    index = 0
    while index < len(words):
        line = ''
        while index < len(words) and x_pos + font.size(words[index] + ' ')[0] < x_end:  # sentence still within area
            x_pos += font.size(words[index] + ' ')[0]
            line += (words[index] + ' ')
            index += 1
        str_so_far.append(line)
        x_pos = x_start

    return str_so_far


def _center_coordinates(top_left: tuple[int, int], length: int, height: int, font: pygame.font, word: str = '') -> \
        tuple[int, int]:
    """
    Given the coordinate of the top left corner of a rectangle area, its width, its height, and the word and its size,
    return the coordinates to display word such that word appears centered in the rectangular area.
    """
    text_length, text_height = font.size(word)
    midpointx = (top_left[0] + length // 2) - (text_length // 2)
    midpointy = (top_left[1] + height // 2) - (text_height // 2)
    return (midpointx, midpointy)


def _loading_screen(dim: dict[str: int], screen: pygame.Surface) -> None:
    """Loading screen to display as file loads in"""
    screen.fill(PALETTE['black'])
    font = pygame.font.SysFont("arialblack", 100)
    word = 'LOADING...'
    _draw_text(screen, word, _center_coordinates((0, 0), dim['screen_width'], dim['screen_height'], font, word), font,
               PALETTE['green'])
    pygame.display.update()


def _load_in_image(image_path: str, width: int, height: int, transparency: int = 255) -> pygame.Surface:
    """
    Load in image and adjust size and transparency
    """
    img = pygame.image.load(image_path)
    img = pygame.transform.scale(img, (width, height))
    img.set_alpha(transparency)
    return img


def _fade_out(dim: dict[str: int], screen: pygame.Surface, time: float) -> None:
    """
    Fade out animation
    Time is the total time it takes for animation, in seconds
    """
    transition_screen = pygame.Surface((dim['screen_width'], dim['screen_height']))
    transition_screen.fill(PALETTE['black'])
    stall = int(time * 1000 // 50)
    for i in range(50):
        transition_screen.set_alpha(i)
        screen.blit(transition_screen, (0, 0))
        pygame.display.update()
        pygame.time.wait(stall)


###################
# BUTTON CLASSES
##################

class Button:
    """
    Abstract class to create buttons

    Instance Attributes:
        - color: color of button
        - rect: button's physical/image representation on screen
    """
    color: tuple[int, int, int]
    rect: pygame.Rect

    def __init__(self, corner: tuple[int, int], width: int = 0, height: int = 0,
                 color: tuple[int, int, int] = PALETTE['green']) -> None:
        self.rect = pygame.Rect(corner[0], corner[1], width, height)
        self.color = color

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on given surface"""
        raise NotImplementedError

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Action when button clicked, return the game state that button induces
        """
        raise NotImplementedError


class NaviButton(Button):
    """
    Button that changes panels

    Instance Attributes:
        - label: text in button's display
        - next: integer representation of next panel program goes to when button clicked
        - margin: distance between button text and edge of rectangle in pixels
        - font: font of text in button's display
    """
    label: str
    next: str
    margin: int
    font: pygame.font

    def __init__(self, label: str, next_panel: str, margin: int, font: pygame.font, corner: tuple[int, int],
                 width: int = 0, height: int = 0, color: tuple[int, int, int] = PALETTE['green']) -> None:
        Button.__init__(self, corner, width, height, color)
        self.label = label
        self.next = next_panel
        self.margin = margin
        self.font = font
        text_length, text_height = self.font.size(self.label)
        self.rect.update(self.rect.topleft[0] - self.margin, self.rect.topleft[1] - self.margin,
                         text_length + 2 * self.margin, text_height + 2 * self.margin)  # update rectangle with margins

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on screen"""
        pygame.draw.rect(surface, self.color, self.rect)
        _draw_text(surface, self.label, (self.rect.topleft[0] + self.margin, self.rect.topleft[1] + self.margin),
                   self.font)

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Signify panel to go to next by its identifying number
        """
        return self.next


class SelectOneNextButton(NaviButton):
    """
    The next button for the select one screen
    Instance Attributes:
        - enabled: if this button has behaviour when clicked
        - button_groups: list of button groups this button moniters to determine enability
    """
    enabled: bool
    button_groups: list[ButtonGroup]

    def __init__(self, label: str, next_panel: str, margin: int, font: pygame.font, corner: tuple[int, int],
                 width: int = 0, height: int = 0, color: tuple[int, int, int] = PALETTE['gray']) -> None:
        NaviButton.__init__(self, label, next_panel, margin, font, corner, width, height, color)
        self.enabled = False
        self.button_groups = []

    def add_button_groups(self, button_groups: list[ButtonGroup]) -> None:
        """
        Add a button group to list of button groups this button moniters
        """
        self.button_groups.extend(button_groups)

    def set_enabled(self) -> None:
        """
        Set button enabled(has behaviour)
        """
        self.color = PALETTE['green']
        self.enabled = True

    def set_disabled(self) -> None:
        """
        Set button disabled(has no behaviour)
        """
        self.color = PALETTE['gray']
        self.enabled = False

    def update_enabled(self) -> bool:
        """
        Update enability of self and return if enability was changed
        """
        old_enabled = self.enabled
        if all(group.selected is not None for group in self.button_groups):
            self.set_enabled()
        else:
            self.set_disabled()

        return old_enabled == self.enabled

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Move to next panel if button enable only. Otherwise, do nothing.
        """
        if self.enabled:
            return self.next
        else:
            return game_state


class SelectAllButton(Button):
    """
    Button to select all checkboxes
    Instance Attributes:
        - margin: distance between text('Select All') and edge of rectangle in pixels
        - font: font type to display text in
        - buttons: list of Checkboxes to activate
    """
    margin: int
    font: pygame.font
    buttons: list[Checkbox]

    def __init__(self, buttons: list[Checkbox], margin: int, font: pygame.font, corner: tuple[int, int], width: int = 0,
                 height: int = 0, color: tuple[int, int, int] = PALETTE['yellow']) -> None:
        Button.__init__(self, corner, width, height, color)
        self.margin = margin
        self.font = font
        text_length, text_height = self.font.size('Select All')
        self.rect.update(self.rect.topleft[0] - self.margin, self.rect.topleft[1] - self.margin,
                         text_length + 2 * self.margin, text_height + 2 * self.margin)
        self.buttons = buttons

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on screen"""
        pygame.draw.rect(surface, self.color, self.rect)
        _draw_text(surface, 'Select All', (self.rect.topleft[0] + self.margin, self.rect.topleft[1] + self.margin),
                   self.font)

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """Select all checkboxes"""
        for button in self.buttons:
            if not button.is_selected():
                button.action(game_state, surface)
        return game_state


class DeselectAllButton(Button):
    """
    Button to deselect all checkboxes. Very similar to SelectAllButton
    Instance Attributes:
        - margin: distance between text('Select All') and edge of rectangle in pixels
        - font: font type to display text in
        - buttons: list of Checkboxes to activate
    """
    margin: int
    font: pygame.font
    buttons: list[Checkbox]

    def __init__(self, buttons: list[Checkbox], margin: int, font: pygame.font, corner: tuple[int, int], width: int = 0,
                 height: int = 0, color: tuple[int, int, int] = PALETTE['yellow']) -> None:
        # must have parent class of Button and not SelectAllButton initializer as rectangle can only be formatted once,
        # relative to Button's text
        Button.__init__(self, corner, width, height, color)
        self.margin = margin
        self.font = font
        text_length, text_height = self.font.size('Deselect All')
        self.rect.update(self.rect.topleft[0] - self.margin, self.rect.topleft[1] - self.margin,
                         text_length + 2 * self.margin, text_height + 2 * self.margin)
        self.buttons = buttons

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on screen"""
        pygame.draw.rect(surface, self.color, self.rect)
        _draw_text(surface, 'Deselect All', (self.rect.topleft[0] + self.margin, self.rect.topleft[1] + self.margin),
                   self.font)

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Deselect all checkboxes.
        """
        for button in self.buttons:
            if button.is_selected():
                button.action(game_state, surface)
        return game_state


class QuitButton(Button):
    """
    Button to end program
    Instance Attributes:
        - margin: distance between text('Quit') and edge of rectangle in pixels
        - font: font to display text in
    """
    margin: int
    font: pygame.font

    def __init__(self, margin: int, font: pygame.font, corner: tuple[int, int], width: int = 0, height: int = 0,
                 color: tuple[int, int, int] = PALETTE['red']) -> None:
        Button.__init__(self, corner, width, height, color)
        self.margin = margin
        self.font = font
        text_length, text_height = self.font.size('QUIT')
        self.rect.update(self.rect.topleft[0] - self.margin, self.rect.topleft[1] - self.margin,
                         text_length + 2 * self.margin, text_height + 2 * self.margin)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on screen"""
        pygame.draw.rect(surface, self.color, self.rect)
        _draw_text(surface, 'QUIT', (self.rect.topleft[0] + self.margin, self.rect.topleft[1] + self.margin), self.font)

    def action(self, game_state: int, surface: pygame.Surface) -> str:
        """Signal that user wants to leave by returning game state of 6(quit)"""
        return 'quit'


class ResetButton(NaviButton):
    """
    Button that resets a search, clears all information from last search and brings you back to main panel
    Instance Attributes:
        - button_column: list of all checkboxes from the select all page
        - next_button: the SelectOneNextButton from the select one page
    """
    button_column: list[Checkbox]
    next_button: SelectOneNextButton
    next_stock_buttons: tuple[NextStockButton, NextStockButton]

    def __init__(self, button_column: list[Checkbox], next_button: SelectOneNextButton,
                 next_stock_buttons: tuple[NextStockButton, NextStockButton], label: str, margin: int,
                 font: pygame.font, corner: tuple[int, int], width: int = 0, height: int = 0,
                 color: tuple[int, int, int] = PALETTE['green']) -> None:
        # always bring you to main menu
        NaviButton.__init__(self, label, 'menu', margin, font, corner, width, height, color)
        self.button_column = button_column
        self.next_button = next_button
        self.next_stock_buttons = next_stock_buttons

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Clear all button selections and return to main page
        """
        for button_group in self.next_button.button_groups:
            button_group.deselect_all()
        for checkbox in self.button_column:
            checkbox.deselect()
        for button in self.next_stock_buttons:
            button.reset()
        self.next_button.update_enabled()
        return NaviButton.action(self, game_state, surface)  # then do same as navigation button


class NextStockButton(Button):
    """Button to display next stock in list of recommended stocks
    Instance Attributes:
        - stocks: list of recommended stocks this button holds
        - label: text in button's display
        - next_stock: index amount to add to current index to get index of next stock(loops to beginning when over
        length)
        - margin: distance between button text and edge of rectangle in pixels
        - font: font of text in button's display
        - current: current index of stock to display
        - enabled: if this button can be
    """

    stocks: list[StockScore]
    label: str
    next_stock: int
    margin: int
    font: pygame.font
    current: int
    enabled: bool
    other_button: Optional[NextStockButton]

    def __init__(self, stocks: list[StockScore], label: str, next_stock: int, margin: int, font: pygame.font,
                 corner: tuple[int, int],
                 width: int = 0, height: int = 0, color: tuple[int, int, int] = PALETTE['green']) -> None:
        Button.__init__(self, corner, width, height, color)
        self.label = label
        self.next_stock = next_stock
        self.margin = margin
        self.font = font
        text_length, text_height = self.font.size(self.label)
        self.rect.update(self.rect.topleft[0] - self.margin, self.rect.topleft[1] - self.margin,
                         text_length + 2 * self.margin, text_height + 2 * self.margin)  # update rectangle with margins
        self.stocks = stocks
        self.current = 0
        self.other_button = None  # set no current other button to start
        self.update_enabled()

    def set_other_button(self, button: NextStockButton) -> None:
        """
        Link this next stock button to another NextStock button
        """
        self.other_button = button

    def update_stocks(self, stocks: list[StockScore]) -> None:
        """
        Update the list of stocks this NextStock button moniters
        """
        self.stocks = stocks
        self.update_enabled()
        if self.other_button.stocks != self.stocks:
            self.other_button.update_stocks(stocks)

    def is_enabled(self) -> bool:
        """Return if this NextStock button has behaviour when clicked"""
        return self.enabled

    def set_enabled(self) -> None:
        """
        Set button enabled(has behaviour)
        """
        self.color = PALETTE['green']
        self.enabled = True

    def set_disabled(self) -> None:
        """
        Set button disabled(has no behaviour)
        """
        self.color = PALETTE['gray']
        self.enabled = False

    def update_enabled(self) -> None:
        """
        Update if this NextStockButton has behaviour when clicked. In order to have behaviour, this button must moniter
        more than 1 stock(if 1 or less stock, makes no sense to have a next stock)
        """
        if len(self.stocks) <= 1:
            self.set_disabled()
        else:
            self.set_enabled()

    def update_current_stock(self) -> None:
        """
        Update current monitered stock to next stock, which depends on how this button navigates(self.next_stock)
        through the list of buttons it moniters.
        """
        self.current = (self.current + self.next_stock) % len(self.stocks)
        self.other_button.set_current_stock(self.current)

    def get_current_stock_index(self) -> int:
        """
        Get current index of the monitered stock
        """
        return self.current

    def get_current_stock(self) -> StockScore:
        """
        Get actual stock at the current index of monitered stock. Raise index error if no stock exists at that index
        (only called internally by program so should never be the case)
        """
        if 0 <= self.get_current_stock_index() < len(self.stocks):
            return self.stocks[self.get_current_stock_index()]
        else:
            raise IndexError

    def set_current_stock(self, i: int) -> None:
        """
        Set index of current monitered stock to given index
        """
        self.current = i
        if self.other_button.get_current_stock_index() != self.current:
            self.other_button.set_current_stock(self.current)

    def reset(self) -> None:
        """
        Clear this button's stocks it moniters and update its enability
        """
        self.set_current_stock(0)
        self.stocks = []
        self.update_enabled()

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Update the new current stock if applicable and return if a stock is being displayed
        """
        if self.is_enabled():
            self.update_current_stock()
            return 're-results'
        else:
            return game_state

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button on screen"""
        pygame.draw.rect(surface, self.color, self.rect)
        _draw_text(surface, self.label, (self.rect.topleft[0] + self.margin, self.rect.topleft[1] + self.margin),
                   self.font)


class Checkbox(Button):
    """
    Button representing a checkbox(can be selected or not, and stays that way unless clicked again)
    Instance Attributes:
        - selected: if this button is selected
    """
    selected: bool

    def __init__(self, corner: tuple[int, int], width: int, height: int,
                 color: tuple[int, int, int] = PALETTE['white']) -> None:
        Button.__init__(self, corner, width, height, color)
        self.selected = False

    def is_selected(self) -> bool:
        """
        Return if this checkbox is selected
        """
        return self.selected

    def select(self) -> None:
        """
        Select this checkbox
        """
        self.selected = True
        self.color = PALETTE['yellow']

    def deselect(self) -> None:
        """Deselect this checkbox"""
        self.selected = False
        self.color = PALETTE['white']

    def draw(self, surface: pygame.Surface) -> None:
        """Draw this checkbox on screen"""
        pygame.draw.rect(surface, self.color, self.rect)

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Convert checkbox's selected status to the opposite. Return same game state
        """
        if self.is_selected():
            self.deselect()
        else:
            self.select()
        self.draw(surface)
        return game_state


class SelectOneCheckbox(Checkbox):
    """
    Checkbox for select one page, must belong to a button group
    Instance Attributes:
        - button_group: button group this checkbox belongs to
        - next_button: next button this checkbox is monitered by
    """
    button_group: ButtonGroup
    next_button: SelectOneNextButton

    def __init__(self, button_group: ButtonGroup, next_button: SelectOneNextButton, corner: tuple[int, int],
                 width: int, height: int, color: tuple[int, int, int] = PALETTE['white']) -> None:
        Checkbox.__init__(self, corner, width, height, color)
        self.button_group = button_group
        self.next_button = next_button

    def action(self, game_state: str, surface: pygame.Surface) -> str:
        """
        Convert checkbox's selected status to the opposite, and update its button group accordingly. Return same game
        state
        """
        if self.is_selected():
            self.deselect()
        else:
            self.select()
        self.button_group.change_selection(self)
        self.button_group.draw(surface)
        # redraw button to new color if enability changed
        same = self.next_button.update_enabled()
        if not same:
            self.next_button.draw(surface)
        return game_state


class ButtonGroup:
    """
    Group of SelectOneCheckbox. Only one of the checkboxes in a button group may be selected.
    Instance Attributes:
        - buttons: list of SelectOneCheckbox in this group
        - selected: the SelectOneCheckbox that is currently selected(all may be unselected)
    """
    buttons: list[SelectOneCheckbox]
    selected: Optional[SelectOneCheckbox]

    def __init__(self) -> None:
        self.buttons = []  # can have empty button group
        self.selected = None

    def add_buttons(self, buttons: list[SelectOneCheckbox]) -> None:
        """Add buttons to button group"""
        self.buttons.extend(buttons)

    def change_selection(self, button: SelectOneCheckbox) -> bool:
        """Update which button in the button group is selected. Return if button was in self.buttons"""
        if button not in self.buttons:
            return False
        else:
            for curr_button in self.buttons:
                if curr_button is not button:
                    curr_button.deselect()

            if button.is_selected():
                self.selected = button
                self.selected.select()
            else:
                self.selected = None
            return True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Redraw all buttons in this button group
        """
        for button in self.buttons:
            button.draw(surface)

    def deselect_all(self) -> None:
        """
        Deselect all buttons in this button group, and set selected back to None
        """
        for button in self.buttons:
            button.deselect()
        self.selected = None

    def get_selected_index(self) -> int:
        """Get index of selected button"""
        return self.buttons.index(self.selected)


if __name__ == '__main__':
    import doctest

    doctest.testmod(verbose=True)
    import python_ta

    python_ta.check_all(config={
        'max-line-length': 120,
        'extra-imports': ['pygame', 'load_objects'],
        'allowed-io': ['run_program'],
        'max-nested-blocks': 4,
        'disable': ['C0302', 'R0913', 'R0902', 'R0912', 'W0401', 'W0622', 'E9999'],
        'generated-members': ['pygame.*']
    })
