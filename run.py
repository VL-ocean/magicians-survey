import gspread
from google.oauth2.service_account import Credentials
import time
from datetime import date
import sys
import subprocess
import os
from colorama import Fore, Back, Style
from rich.console import Console
from rich.table import Table


SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]


CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('survey-data')
SHEET_DATA = SHEET.worksheet('data')
SHEET_QUESTIONS = SHEET.worksheet('questions')


# Clear the terminal from all text
def wipe_terminal():
    # Delete all text in the terminal
    if os.name == "posix":  # Identify if OS is macOS or Linux
        os.system("clear")
    elif os.name == "nt":  # Identify of OS is Windows
        os.system("cls")


def get_questons():

    # read the quantity of questions in the sheet
    questions_count = len(SHEET_QUESTIONS.col_values(1))

    # prepare new list for questions
    questions_list = []

    for index in range(1, questions_count + 1):
        original_list = SHEET_QUESTIONS.row_values(index)
        answer_options_list = original_list[1:]
        questions_list.append([original_list[0], answer_options_list])

    return questions_list


def get_date_and_time():

    user_date = time.strftime("%d %b %Y", time.gmtime())
    user_time = time.strftime("%H:%M:%S", time.gmtime())

    return [user_date, user_time]


def display_questions(questions):

    answers_list = get_date_and_time()

    for question_list in questions:

        wipe_terminal()
        # get and print a question
        question = "\n" + question_list[0] + "\n"
        print(question)

        # loop through answers and print each of them adding the option's number
        for index in (range(len(question_list[1]))):
            num = index + 1
            option_for_user = f"({Fore.YELLOW}{num}{Style.RESET_ALL}) - {question_list[1][index]}"
            print(option_for_user)

        while True:
            try:
                # get user's input
                print("")
                answer = int(input(Fore.YELLOW + "Enter your option number here: " + Style.RESET_ALL))
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
                print(Fore.RED + "Please enter a number" + Style.RESET_ALL)
            except IndexError:
                print(Fore.RED + "Please choose a number from available options" + Style.RESET_ALL)

    return answers_list 


def push_user_data(data):
    SHEET_DATA.append_row(data)
    print(Fore.BLUE + "\nThe answers has been saved.\nThank you for filling out our survey!" + Style.RESET_ALL)
    time.sleep(2)


def choice():

    print(Fore.GREEN + "\n\nWelcome to the anonymous survey for magicians!\n" + Style.RESET_ALL)
    print(Fore.BLUE + "You will go through 10 questions." + Style.RESET_ALL)
    print(Fore.BLUE + "Please choose the option that suits you the most." + Style.RESET_ALL)
    print(Fore.BLUE + "If you would like to exit the survey, please enter " + Style.RESET_ALL + Fore.RED + "0" + Style.RESET_ALL + Fore.BLUE + " anytime you feel so.\n" + Style.RESET_ALL)
    while True:
        try:
            print("Would you like to start the survey?")
            option = int(input("(" + Fore.YELLOW + "1" + Style.RESET_ALL + ") - yes or (" + Fore.YELLOW + "2" + Style.RESET_ALL + ") - no: "))
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
                print(Fore.RED + "Please choose a number from available options" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Please enter a number" + Style.RESET_ALL)


def count_keyword(keyword, data_list):
    num = 0
    for list in data_list:
        if keyword in list:
            num += 1
    return num


def count_percentage(num_of_keyword, num_of_replies):
    if num_of_keyword == 0:
        return 0
    else:
        percentage = round((num_of_keyword * 100) / num_of_replies, 2)
        return percentage


def build_statistics(questions):

    statistics_list = []
    
    list_of_lists = SHEET_DATA.get_all_values()
    data_list = list_of_lists[1:]
    num_of_replies = len(data_list)

    statistics_list.append(num_of_replies)

    for question in questions:
        question_statistics = []

        for keyword in question[1]:

            num_of_keyword = count_keyword(keyword, data_list)
            percent_of_keyword = count_percentage(num_of_keyword, num_of_replies)
            question_statistics.append(percent_of_keyword)

        statistics_list.append(question_statistics)

    return statistics_list


def show_statistics(questions, statistics):

    wipe_terminal()
    print(f"The survey was completed by {statistics[0]} people.")
    print("-" * 50)
    print("")

    table = Table(title="Statistics")

    table.add_column("Option", style="magenta", no_wrap=True)
    table.add_column("Percentage", style="green", no_wrap=True)
    
    table.add_row(questions[0][1])
    table.add_row(statistics[1])

    console = Console()
    console.print(table)

    print(statistics)



def main():

    questions = get_questons()
    # user_answer = display_questions(questions)
    # push_user_data(user_answer)
    statistics = build_statistics(questions)
    show_statistics(questions, statistics)


if choice():
    main()








