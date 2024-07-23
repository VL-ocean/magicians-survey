import gspread
from google.oauth2.service_account import Credentials


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

    # get insight on how many questions are in the sheet
    all_questions = SHEET_QUESTIONS.get_all_values()

    # based on row count, get each question with answers as a list and add into overall list of questions
    questions_list = []
    for index in range(len(all_questions)):
        # since index starts at 0, but row should start from 1, we increase index by 1 before getting values
        index = index + 1
        # add each row values into the general list
        questions_list.append(SHEET_QUESTIONS.row_values(index))

    return questions_list


def display_questions(questions):

    answers_list = []

    for list in questions:

        # get and print a question
        question = list[0] + "\n"
        print(question)

        # loop through answers and print each of them adding the option's number
        for option in range(1, len(list)):
            option = f"({option}) - {list[option]}"
            print(option)

        # get user's input and save the answer in a list
        print("\n")
        answer = int(input("Enter your option number here: "))
        answers_list.append(list[answer])
        print("\n\n")

    return answers_list


def main():

    questions = get_questons()
    answers = display_questions(questions)
    print(answers)


main()