import pyodbc
# import os
# Connection string for SQL Server
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=26.71.121.211;"
    "DATABASE=ResearchSnake;"
    f"UID=sa;"  # Replace with your SQL username
    f"PWD=43567s9205;" # Replace with your SQL password
    f"Network=dbmssocn;"
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


def Update_Question(quiz_id, old_question, new_question, new_options, correct_answer="A"):
    query = """
    UPDATE Question 
    SET Question = ?, 
        Option1 = ?, 
        Option2 = ?, 
        Option3 = ?, 
        Option4 = ?,
        CorrectAnswer = ?
    WHERE QuizID = ? and Question = ?
    """
    cursor.execute(query, (new_question, new_options[0], new_options[1], new_options[2],
                           new_options[3], correct_answer, quiz_id, old_question))
    cursor.commit()


def Add_Question(selected_id):
    query_id = "SELECT MAX(QuestionID + 0) FROM Question;"
    query = "Insert into Question values (?, ?, ?, ?, ?, ?, ?, ?)"
    check = "Select Question from Question where QuizID = 1"
    cursor.execute(query_id)
    new_ID = int(cursor.fetchone()[0])
    cursor.execute(check)
    questions = []
    taken_id = 0
    for i in cursor.fetchall():
        questions.append(i[0])
    while f"Question {new_ID + 1 + taken_id}" in questions:
        taken_id += 1
    print(new_ID)
    cursor.execute(query, new_ID + 1, f"Question {new_ID + 1}", "A", "Option 1", "Option 2", "Option 3", "Option 4", selected_id)
    cursor.commit()


def Add_QuizLVL(lvl, chapter):
    query_id = "SELECT MAX(QuizID + 0) FROM Quiz;"
    query = "Insert Into Quiz values (?, ?, ?, ?, ?, ?)"
    cursor.execute(query_id)
    quiz_id = int(cursor.fetchone()[0])
    print("Quiz ID: ", quiz_id + 1)
    cursor.execute(query, quiz_id + 1, "Quiz Name", "Description", lvl, chapter, 1)
    cursor.commit()
    return quiz_id


def Delete_QuizLVL(quiz_id):
    query = "Delete from Quiz where QuizID = ?"
    try:
        cursor.execute(query, quiz_id)

        cursor.commit()
    except pyodbc.IntegrityError:
        return True


def Delete_All(quiz_id):
    query = "Delete from Question where QuizID = ?"
    cursor.execute(query, quiz_id)
    cursor.commit()


def Update_title(info, lvl, chapter):
    query = """
        UPDATE Quiz 
        SET Name = ?, 
            Description = ?
        WHERE LevelRequired = ? and ChapterID = ?
        """
    cursor.execute(query, info[0], info[1], lvl, chapter)
    cursor.commit()


def Delete_Question(quiz_id, question):
    query = "Delete from Question where QuizID = ? and Question = ?"
    cursor.execute(query, quiz_id, question)
    cursor.commit()


def Delete_Quiz(lvl):
    query = "Delete from "


if __name__ == "__main__":
    question = Retrieve_Question(1, "Question")
    result = Retrieve_Question(1, "Option1, Option2, Option3, Option4")
    # for i in Select("QuizID", "Question"):
    #     print(i)
    # print(Select("QuizID", "Question"))
    Add_Question()
    # print(question)
    # print(Add_Question())
