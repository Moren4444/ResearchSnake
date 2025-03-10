import pyodbc
# import os
# Connection string for SQL Server
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-RBGOM9O;"
    "DATABASE=ResearchSnake;"
    f"UID=sa;"  # Replace with your SQL username
    f"PWD=43567s9205;"  # Replace with your SQL password
)

# print(pyodbc.drivers())  # List available ODBC drivers
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


def insert(query):
    cursor.execute(query)
    conn.commit()


def user_info():
    cursor.execute("Select * from [User]")
    user = cursor.fetchall()
    print(user)
    return user


def select_user(id):
    cursor.execute(f"Select * from [User] where UserID = {id}")
    return cursor.fetchone()


def Select(column, table):
    cursor.execute(f"Select {column} from {table}")
    select = cursor.fetchall()
    return int(select[-1][0])


def Retrieve_Question(ids, column="*"):
    quiz_id = ids
    row = []

    num_column = len(column.split(", "))
    with pyodbc.connect(connection_string):
        query = f"SELECT {column} from Question Where QuizID = ?"
        cursor.execute(query, (quiz_id,))
        if num_column > 1:
            for i in cursor.fetchall():
                row.append(i[0: num_column])
        else:
            for i in cursor.fetchall():
                row.append(i[0])
    return row


def get_last_user_Id():
    cursor.execute("SELECT MAX(UserID) FROM [User]")
    results = cursor.fetchone()[0]
    return results if results else None  # Fetch the highest ID


def update(table, column, new_value, id):
    cursor.execute(f"UPDATE {table} set {column} = {new_value} where UserID = {id}")
    cursor.commit()


def Chapter_Quiz():
    cursor.execute("Select ChapterID from Chapter")
    chapter = cursor.fetchall()
    cursor.execute("Select * from Quiz order by ChapterID, LevelRequired")
    quiz = cursor.fetchall()
    return len(chapter), quiz


def Update_Question(question_id, new_question, new_options, correct_answer="A"):
    query = """
    UPDATE Question 
    SET Question = ?, 
        Option1 = ?, 
        Option2 = ?, 
        Option3 = ?, 
        Option4 = ?,
        CorrectAnswer = ?
    WHERE QuestionID = ?
    """
    cursor.execute(query, (new_question, new_options[0], new_options[1], new_options[2],
                           new_options[3], correct_answer, question_id))
    cursor.commit()


def Delete_Question(question_id):
    cursor.execute(f"Delete from Question where QuestionID = {question_id}")
    cursor.commit()


if __name__ == "__main__":
    question = Retrieve_Question(1, "Question")
    result = Retrieve_Question(1, "Option1, Option2, Option3, Option4")
    # for i in Select("QuizID", "Question"):
    #     print(i)
    print(Select("QuizID", "Question"))

    print(question)
