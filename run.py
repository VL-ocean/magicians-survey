import gspread
from google.oauth2.service_account import Credentials
import time
from datetime import date


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

    # for list in questions:

    #     # get and print a question
    #     question = "\n" + list[0] + "\n"
    #     print(question)

    #     # loop through answers and print each of them adding the option's number
    #     for option in range(1, len(list)):
    #         option = f"({option}) - {list[option]}"
    #         print(option)

    #     # get user's input
    #     print("")
    #     answer = int(input("Enter your option number here: "))
    #     print("")

    #     # save the answer in a list
    #     answers_list.append(list[answer])

    return answers_list 


def main():

    questions = get_questons()
    user_answer = display_questions(questions)
    print(user_answer)



main()

