import gspread
from google.oauth2.service_account import Credentials
import time
from datetime import date
import sys
import subprocess
import os
from colorama import Fore, Back, Style


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
    """
        Delete all text in the terminal
    """
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

def main():

    questions = get_questons()
    user_answer = display_questions(questions)
    push_user_data(user_answer)


if choice():
    main()

