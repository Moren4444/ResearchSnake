import pyodbc

# Connection string for SQL Server
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-RBGOM9O;"
    "DATABASE=ResearchSnake;"
    "UID=sa;"  # Replace with your SQL username
    "PWD=43567s9205;"  # Replace with your SQL password
)

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


def insert(query):
    cursor.execute(query)
    conn.commit()


def user_info():
    cursor.execute("Select * from [User]")
    user = cursor.fetchall()

    return user


def Select(column, table):
    cursor.execute(f"Select {column} from {table}")
    select = cursor.fetchall()
    for index, i in enumerate(select):
        if index + 1 == int(i[0]):
            return index + 1


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


def Chapter_Quiz():
    cursor.execute("Select ChapterID from Chapter")
    chapter = cursor.fetchall()
    cursor.execute("Select * from Quiz order by ChapterID, LevelRequired")
    quiz = cursor.fetchall()
    return len(chapter), quiz


if __name__ == "__main__":
    question = Retrieve_Question(1, "CorrectAnswer")
    result = Retrieve_Question(1, "Option1, Option2, Option3, Option4")
    # for i in Select("QuizID", "Question"):
    #     print(i)
    print(Select("QuizID", "Question"))
    print(Chapter_Quiz()[1])
    print(question)

