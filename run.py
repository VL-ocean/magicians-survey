import gspread
from google.oauth2.service_account import Credentials
import time
import os
from colorama import Fore, Back, Style
from rich.console import Console
from rich.table import Table


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


CREDS = Credentials.from_service_account_file("creds.json")
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open("survey-data")
SHEET_DATA = SHEET.worksheet("data")
SHEET_QUESTIONS = SHEET.worksheet("questions")


# source: https://github.com/DennisSchenkel/PP3
def wipe_terminal():
    """
    Clears the terminal from all text
    """
    if os.name == "posix":  # Identify if OS is macOS or Linux
        os.system("clear")
    elif os.name == "nt":  # Identify of OS is Windows
        os.system("cls")


def get_questons():
    """
    Gets data from questions worksheet
    and return them for next function
    """
    questions_count = len(SHEET_QUESTIONS.col_values(1))
    questions_list = []

    for index in range(1, questions_count + 1):
        original_list = SHEET_QUESTIONS.row_values(index)
        answer_options_list = original_list[1:]
        questions_list.append([original_list[0], answer_options_list])

    return questions_list


def get_date_and_time():
    """
    Gets current date and time in readable format,
    return them in a list
    """
    user_date = time.strftime("%d %b %Y", time.gmtime())
    user_time = time.strftime("%H:%M:%S", time.gmtime())

    return [user_date, user_time]


def display_questions(questions):
    """
    Reads data from the questions list,
    prints them out for the user one by one,
    takes user`s answer and saves it in a list
    """
    answers_list = get_date_and_time()

    for question_list in questions:

        wipe_terminal()
        # get and print a question
        question = (
            Style.BRIGHT
            + "\n"
            + " "
            + question_list[0]
            + "\n"
            + Style.RESET_ALL
        )
        print(question)

        # loop through answers
        # and print each of them adding the option's number
        for index in range(len(question_list[1])):
            num = index + 1
            option_for_user = (
                f"{Style.BRIGHT} ({Fore.YELLOW}{num}{Style.RESET_ALL}"
                f"{Style.BRIGHT}) - {question_list[1][index]}{Style.RESET_ALL}"
            )
            print(option_for_user)

        while True:
            try:
                # get user's input
                print("")
                answer = int(
                    input(
                        Fore.YELLOW
                        + Style.BRIGHT
                        + " Enter your option number here: "
                        + Style.RESET_ALL
                    )
                )
                if answer == 0:
                    wipe_terminal()
                    raise SystemExit
                elif answer < 0:
                    raise IndexError
                else:
                    # save the answer in a list
                    answer_index = answer - 1
                    answers_list.append(question_list[1][answer_index])
                    wipe_terminal()
                    break
            except ValueError:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + " Please enter a number"
                    + Style.RESET_ALL
                )
            except IndexError:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + " Please choose a number from available options"
                    + Style.RESET_ALL
                )
            except KeyboardInterrupt:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + "\n Please enter a number"
                    + Style.RESET_ALL
                )

    return answers_list


def push_user_data(data):
    """
    Transfers user's answers into the worksheet
    """
    SHEET_DATA.append_row(data)
    print(
        Style.BRIGHT
        + Fore.BLUE
        + "\n The answers has been saved."
        + "\n Thank you for filling out our survey!"
        + Style.RESET_ALL
    )
    time.sleep(2)


def choice():
    """
    Prints out the welcome screen to the user with some info,
    asks to start the survey
    """
    print(
        Style.BRIGHT
        + Fore.GREEN
        + "\n\n Welcome to the anonymous survey for magicians!\n"
        + Style.RESET_ALL
    )
    print(
        Style.BRIGHT
        + Fore.BLUE
        + " You will go through 10 questions."
        + Style.RESET_ALL
    )
    print(
        Style.BRIGHT
        + Fore.BLUE
        + " Please choose the option that suits you the most."
        + Style.RESET_ALL
    )
    print(
        Style.BRIGHT
        + Fore.BLUE
        + " If you would like to exit the survey, please enter "
        + Style.RESET_ALL
        + Style.BRIGHT
        + Fore.RED
        + "0"
        + Style.RESET_ALL
        + Style.BRIGHT
        + Fore.BLUE
        + " anytime you feel so.\n"
        + Style.RESET_ALL
    )

    while True:
        try:
            print("\n Would you like to start the survey?")
            option = int(
                input(
                    Style.BRIGHT
                    + " ("
                    + Fore.YELLOW
                    + "1"
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + ") - yes or ("
                    + Fore.YELLOW
                    + "2"
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + ") - no: "
                    + Style.RESET_ALL
                )
            )
            if option == 0:
                wipe_terminal()
                raise SystemExit
            elif option == 2:
                wipe_terminal()
                raise SystemExit
            elif option == 1:
                return True
                break
            else:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + " Please choose a number from available options"
                    + Style.RESET_ALL
                )
        except ValueError:
            print(
                Style.BRIGHT
                + Fore.RED
                + " Please enter a number"
                + Style.RESET_ALL
            )
        except KeyboardInterrupt:
            print(
                Style.BRIGHT
                + Fore.RED
                + "\n Please enter a number"
                + Style.RESET_ALL
            )


def count_keyword(keyword, data_list):
    """
    Counts how many of the keyword (answer option) is
    in provided list (list of all user answers for one question)
    """
    num = 0
    for list in data_list:
        if keyword in list:
            num += 1
    return num


def count_percentage(num_of_keyword, num_of_replies):
    """
    Counts percentage of one answer option compared to
    total number of answers for one question
    """
    if num_of_keyword == 0:
        return 0
    else:
        percentage = round((num_of_keyword * 100) / num_of_replies, 1)
        return percentage


def build_statistics(questions):
    """
    Controls several functions that build statistics list,
    calls them for each question and answer option from the survey
    """
    statistics_list = []
    list_of_lists = SHEET_DATA.get_all_values()
    data_list = list_of_lists[1:]
    num_of_replies = len(data_list)
    statistics_list.append(num_of_replies)

    for question in questions:
        question_statistics = []

        for keyword in question[1]:

            num_of_keyword = count_keyword(keyword, data_list)
            percent_of_keyword = count_percentage(
                num_of_keyword, num_of_replies
            )
            question_statistics.append(percent_of_keyword)

        statistics_list.append(question_statistics)

    return statistics_list


def show_statistics(questions, statistics):
    """
    Builds a table to display the user overall percentage
    calculated based on the total number of replies
    """
    wipe_terminal()
    print(
        (
            f"{Style.BRIGHT}\n The survey was completed by "
            f"{Fore.CYAN}{statistics[0]}"
            f"{Style.RESET_ALL}{Style.BRIGHT} people."
            f"\n You can see the overall statistics below{Style.RESET_ALL}"
        )
    )
    print("-" * 79)
    print("")
    time.sleep(3)

    for question, stats in zip(questions, statistics[1:]):

        table = Table(title=question[0], title_style="cyan", highlight="True")

        table.add_column("Option", style="magenta", no_wrap=True)
        table.add_column(
            "Percentage", style="green", justify="right", no_wrap=True
        )

        for option, percent in zip(question[1], stats):
            table.add_row(option, str(percent) + " %")

        console = Console()
        console.print(table)
        print("")
        time.sleep(2)


def exit_or_restart():
    """
    Offers the user an option to complete the survey again or exit the app
    """
    while True:
        try:
            print(
                Style.BRIGHT
                + "\n Would you like to start the survey again or exit?"
                + Style.RESET_ALL
            )
            option = int(
                input(
                    Style.BRIGHT
                    + " ("
                    + Fore.YELLOW
                    + "1"
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + ") - survey or ("
                    + Fore.YELLOW
                    + "2"
                    + Style.RESET_ALL
                    + Style.BRIGHT
                    + ") - exit: "
                    + Style.RESET_ALL
                )
            )
            if option == 0:
                wipe_terminal()
                raise SystemExit
            elif option == 2:
                wipe_terminal()
                raise SystemExit
            elif option == 1:
                return True
                break
            else:
                print(
                    Style.BRIGHT
                    + Fore.RED
                    + "Please choose a number from available options"
                    + Style.RESET_ALL
                )
        except ValueError:
            print(
                Style.BRIGHT
                + Fore.RED
                + "Please enter a number"
                + Style.RESET_ALL
            )
        except KeyboardInterrupt:
            print(
                Style.BRIGHT
                + Fore.RED
                + "\n Please enter a number"
                + Style.RESET_ALL
            )


def main():
    """
    Controls the app flow
    """
    try:
        questions = get_questons()
        user_answer = display_questions(questions)
        push_user_data(user_answer)
        statistics = build_statistics(questions)
        show_statistics(questions, statistics)
        if exit_or_restart():
            main()
    except KeyboardInterrupt:
        wipe_terminal()
        print(
            Style.BRIGHT
            + Fore.RED
            + "\n The app flow was interrupted.\n"
            + " Please click on "
            + Style.RESET_ALL
            + Style.BRIGHT
            + Fore.YELLOW
            + "Run program"
            + Style.RESET_ALL
            + Style.BRIGHT
            + Fore.RED
            + " to restart it"
            + Style.RESET_ALL
        )


# Starts the survey, offers the exit option
if choice():
    main()
