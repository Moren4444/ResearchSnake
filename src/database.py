import pyodbc
# import os
# Connection string for SQL Server
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
import json

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=26.71.121.211;"
    "DATABASE=ResearchSnake;"
    f"UID=sa;"  # Replace with your SQL username
    f"PWD=43567s9205;"  # Replace with your SQL password
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


def Select(column, table, id):
    cursor.execute(f"Select {column} from {table} where QuizID = {id}")
    select = cursor.fetchall()
    return select


def profile_info():
    cursor.execute("select UserID + 0 as new_ID, * from [user] order by new_ID")
    user = cursor.fetchall()
    return user


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


def stu_info():
    cursor.execute("Select * from [User] where Role = 'Student'")
    user = cursor.fetchall()

    return user


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
    id_exe = cursor.fetchone()[0]
    new_ID = 0
    if id_exe:
        new_ID = int(id_exe)
    cursor.execute(check)
    questions = []
    taken_id = 0
    for i in cursor.fetchall():
        questions.append(i[0])
    while f"Question {new_ID + 1 + taken_id}" in questions:
        taken_id += 1
    print(new_ID)
    cursor.execute(query, new_ID + 1, f"Question {new_ID + 1}", "A", "Option 1", "Option 2", "Option 3", "Option 4",
                   selected_id)
    cursor.commit()


def Add_QuizLVL(lvl, chapter):
    query_id = "SELECT MAX(QuizID + 0) FROM Quiz;"
    query = "Insert Into Quiz values (?, ?, ?, ?, ?, ?)"
    cursor.execute(query_id)
    quiz_id = 0
    id_exe = cursor.fetchone()[0]
    if id_exe:
        quiz_id = int(id_exe)
    cursor.execute(query, quiz_id + 1, "Quiz Name", "Description", lvl, chapter, 1)
    cursor.commit()
    return quiz_id


def Delete_Chapter(chapter_index, delete_question):
    print(chapter_index)
    query = "Delete from Chapter where ChapterID = ?"
    quiz_match_delete = "Delete from Quiz where ChapterID = ?"
    query_question = "Delete from Question where QuizID = ?"
    for i in delete_question:
        cursor.execute(query_question, i)
    cursor.execute(quiz_match_delete, chapter_index)
    cursor.execute(query, chapter_index)
    cursor.commit()


def Add_ChapterDB():
    query_id = "Select MAX(ChapterID + 0) from Chapter"
    query = "Insert Into Chapter values (?, ?)"
    cursor.execute(query_id)
    chap_id = 0
    id_exe = cursor.fetchone()[0]
    if id_exe:
        chap_id = int(id_exe)
    cursor.execute(query, chap_id + 1, f"Chapter {chap_id + 1}")

    print("Chapter update")
    cursor.commit()
    return chap_id + 1


def Update_Database():
    with open("Quiz_draft.json") as file:
        chapter = json.load(file)

    index = 1
    Q_index = 1
    Chapter_query = "Insert Into Chapter values (?, ?)"
    Quiz_query = "Insert Into Quiz values (?, ?, ?, ?, ?, ?)"
    Question_query = "Insert Into Question values (?, ?, ?, ?, ?, ?, ?, ?)"
    for keys, value in chapter.items():
        cursor.execute(Chapter_query, keys, f"Chapter {keys}")
        for quiz in value:
            cursor.execute(Quiz_query, index, quiz[0], quiz[1], quiz[2], int(quiz[3]), 1)
            for question, Q_value in quiz[4].items():
                cursor.execute(Question_query, Q_index, question, Q_value[0], Q_value[1], Q_value[2]
                               , Q_value[3], Q_value[4], index)
                Q_index += 1
            index += 1
    cursor.commit()


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


def add_new_user(name, password, level, role):
    cursor.execute("SELECT MAX(UserID) FROM [User]")
    max_id = cursor.fetchone()[0]

    new_user_id = 1 if max_id is None else int(max_id) + 1

    cursor.execute("SELECT COUNT(*) FROM [User] WHERE UserID = ?", (new_user_id,))
    if cursor.fetchone()[0] > 0:
        while True:
            new_user_id += 1
            cursor.execute("SELECT COUNT(*) FROM [User] WHERE UserID = ?", (new_user_id,))
            if cursor.fetchone()[0] == 0:
                break

    query = "INSERT INTO [User] (UserID, Name, Password, Level, Role) VALUES (?, ?, ?, ?, ?)"

    try:
        cursor.execute(query, (new_user_id, name, password, level, role))
        conn.commit()
        print(f"✅ New user '{name}' added successfully! UserID: {new_user_id}")
    except pyodbc.IntegrityError as e:
        print(f"❌ Error inserting user: {e}")


def update_user(user_id, new_username, new_password):
    """ Update the username and password of a user. """
    query = "UPDATE [User] SET Name = ?, Password = ? WHERE UserID = ?"
    cursor.execute(query, (new_username, new_password, user_id))
    conn.commit()


def update_user_role(user_id, new_role):
    query = "UPDATE [User] SET Role = ? WHERE UserID = ?"
    try:
        cursor.execute(query, (new_role, user_id))
        conn.commit()
        print(f"User {user_id} role updated to {new_role}.")
    except Exception as ex:
        print(f"Error updating user role: {ex}")
        raise ex
    cursor.execute("select UserID + 0 as new_ID, * from [user] order by new_ID")
    user = cursor.fetchall()
    return user


def delete_user(user_id):
    query = "DELETE FROM [User] WHERE UserID = ?"
    try:
        cursor.execute(query, (user_id,))
        conn.commit()
        print(f"User {user_id} deleted successfully.")
    except Exception as ex:
        print(f"Error deleting user: {ex}")
        raise ex


def Update_title(info, lvl, chapter):
    print(lvl, chapter)
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
    # question = Retrieve_Question(1, "Question")
    # result = Retrieve_Question(1, "Option1, Option2, Option3, Option4")
    # for i in Select("QuizID", "Question"):
    #     print(i)
    # print(Select("QuizID", "Question"))
    # Add_Question()
    # print(question)
    # print(Add_Question())
    # print(Update_Database())
    print("Hai" if Select("QuizID", "Question", 2) else "Bye")
