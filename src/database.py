import os

import pyodbc
# import os
# Connection string for SQL Server
# db_user = os.getenv("DB_USER")
# db_password = os.getenv("DB_PASSWORD")
import json
from datetime import datetime
driver = pyodbc.drivers()

print("ODBC Driver 17 for SQL Server" in driver)
chosen_driver = 'ODBC Driver 17 for SQL Server' if 'ODBC Driver 17 for SQL Server' in driver else ('ODBC Driver 18 for '
                                                                                                   'SQL Server')
connection_string = (
    f"DRIVER={chosen_driver};"
    "SERVER=26.71.121.211;"
    "DATABASE=ResearchSnake;"
    f"UID=sa;"  # Replace with your SQL username
    f"PWD=43567s9205;"  # Replace with your SQL password
    f"Network=dbmssocn;"
)

# print(pyodbc.drivers())  # List available ODBC drivers
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

if os.path.exists("Quiz_draft2.json"):
    with open("Quiz_draft2.json") as file:
        chapter_quizQ = json.load(file)
else:
    chapter_quizQ = {}


def generate_quiz_id(selected_id):
    return "QIZ" + str(int(selected_id)).zfill(2) if selected_id else "QIZ01"


def generate_question_id(selected_id):
    return "Q" + str(int(selected_id)).zfill(2) if selected_id else "Q01"


def generate_user_id(selected_id, role):
    prefix = "S" if role == "Student" else "O" if role == "Owner" else "A"
    if role == "Owner":
        return prefix + str(int(selected_id)).zfill(2) if selected_id else f"{prefix}01"
    else:
        return prefix + str(int(selected_id)).zfill(4) if selected_id else f"{prefix}0001"


def generate_chapter_id(selected_id):
    return "CHA" + str(selected_id).zfill(2) if selected_id else "CHA01"


def insert(query):
    cursor.execute(query)
    conn.commit()


def resultDB(player_info, quiz_level, chapter_info, user_answer, difficulties_speed, set_time):
    print("Testing: ", player_info, chapter_info, difficulties_speed)
    Game_ID = "SELECT MAX(CAST(SUBSTRING(GameID, 3, LEN(GameID)) AS INT)) FROM Game_Session"
    cursor.execute(Game_ID)
    max_id = cursor.fetchone()[0]
    next_game_id = max_id + 1 if max_id is not None else 1
    difficulties = "Easy" if difficulties_speed == 180 else "Medium" if difficulties_speed == 150 else "Hard"
    now_str = datetime.now().strftime("%H:%M:%S")
    now_time = datetime.strptime(now_str, "%H:%M:%S")
    diff = now_time - set_time
    total_seconds = diff.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = int(total_seconds % 60)
    query = "INSERT INTO Game_Session VALUES (?, ?, ?, ?, ?)"
    cursor.execute(query, f"GA{next_game_id:04d}", quiz_level, player_info,
                   difficulties, f"{minutes} min {seconds} sec" if minutes > 0 else f"{seconds} sec")
    cursor.commit()

    for index, i in enumerate(user_answer):
        question = Retrieve_Question(chapter_info[0][3:], "QuestionID")[index]
        Result_ID = "SELECT MAX(CAST(SUBSTRING(ResultID, 3, LEN(GameID)) AS INT)) FROM Result"
        cursor.execute(Result_ID)
        max_id = cursor.fetchone()[0]
        next_id = max_id + 1 if max_id is not None else 1
        query = f"Insert into Result values (?, ?, ?, ?)"
        cursor.execute(query, f'RS{next_id:04d}', question, f"GA{next_game_id:04d}", i)
        cursor.commit()
    pass


def select(query):
    cursor.execute(query)
    return cursor.fetchall()


def update_DB(query):
    cursor.execute(query)
    conn.commit()


def last_Update(ID, role):
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(now_str)
    query = f"Update [{role}] set LastLogin = ? where {role}ID = ?"
    cursor.execute(query, now_str, ID)
    cursor.commit()


def add_new_user(name, email, password, level, role, registeredDate, lastLogin):
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

    query = ("INSERT INTO [Student] (UserID, Name, Email, Password, Level, Role, RegisteredDate, LastLogin) VALUES ("
             "?, ?,"
             "?, ?, ?, ?, ?, ?)")
    try:
        cursor.execute(query, (new_user_id, name, email, password, level, role, registeredDate, lastLogin))
        conn.commit()
        print(f"✅ New user '{name}' added successfully! UserID: {new_user_id}")
    except pyodbc.IntegrityError as e:
        print(f"❌ Error inserting user: {e}")


def admin_profile_info():
    cursor.execute("select * from [Admin]")
    user = cursor.fetchall()
    return user


def add_new_admin(name, email, password, registeredDate, lastLogin):
    # Changed UserID to AdminID to match your table structure
    cursor.execute("SELECT MAX(AdminID) FROM [Admin]")
    max_id = cursor.fetchone()[0]

    # Generate initial ID - fixed potential None issue and string conversion
    new_user_id = "A0001" if max_id is None else "A" + str(int(max_id[1:]) + 1).zfill(4)

    # Check for conflicts and generate a new ID if needed
    cursor.execute("SELECT COUNT(*) FROM [Admin] WHERE AdminID = ?", (new_user_id,))
    while cursor.fetchone()[0] > 0:
        next_num = int(new_user_id[1:]) + 1
        new_user_id = "A" + str(next_num).zfill(4)
        cursor.execute("SELECT COUNT(*) FROM [Admin] WHERE AdminID = ?", (new_user_id,))

    query = ("INSERT INTO [Admin] (AdminID, Name, Email, Password, RegisteredDate, LastLogin) VALUES ("
             "?, ?, ?, ?, ?, ?)")
    try:
        cursor.execute(query, (new_user_id, name, email, password, registeredDate, lastLogin))
        conn.commit()
        print(f"✅ New admin '{name}' added successfully! AdminID: {new_user_id}")
        return True
    except pyodbc.IntegrityError as e:
        print(f"❌ Error inserting admin: {e}")
        return False


def add_new_student(name, email, password, level, registeredDate, lastLogin):
    # Change UserID to StudentID in the query
    cursor.execute("SELECT MAX(StudentID) FROM Student")
    max_id = cursor.fetchone()[0]

    # Generate initial ID
    new_user_id = "S0001" if max_id is None else "S" + str(int(max_id[1:]) + 1).zfill(4)

    # Check for conflicts and generate a new ID if needed
    cursor.execute("SELECT COUNT(*) FROM Student WHERE StudentID = ?", (new_user_id,))
    while cursor.fetchone()[0] > 0:
        next_num = int(new_user_id[1:]) + 1
        new_user_id = "S" + str(next_num).zfill(4)
        cursor.execute("SELECT COUNT(*) FROM Student WHERE StudentID = ?", (new_user_id,))

    query = ("INSERT INTO Student (StudentID, Name, Email, Password, Level, RegisteredDate, LastLogin) VALUES ("
             "?, ?, ?, ?, ?, ?, ?)")
    try:
        cursor.execute(query, (new_user_id, name, email, password, level, registeredDate, lastLogin))
        conn.commit()
        print(f"✅ New user '{name}' added successfully! UserID: {new_user_id}")
        return True
    except pyodbc.IntegrityError as e:
        print(f"❌ Error inserting user: {e}")
        return False


def check_existing(role, new_name, new_email):
    # Fetch and flatten email lists
    cursor.execute("Select Email from [Student]")
    email_stu = [row[0] for row in cursor.fetchall()]

    cursor.execute("Select Email from [Admin]")
    email_admin = [row[0] for row in cursor.fetchall()]

    cursor.execute("Select Email from [Owner]")
    email_own = [row[0] for row in cursor.fetchall()]

    # Check if email exists in any list
    if new_email in email_stu or new_email in email_admin or new_email in email_own:
        # print("The email has been used already.")
        return False

    # Check name based on role
    if role == "Admin":
        cursor.execute("Select Name from [Student]")
        name_list = [row[0] for row in cursor.fetchall()]
        if new_name in name_list:
            # print("The name has been used already.")
            return False
        else:
            # print("Done")
            return True

    elif role == "Owner":
        cursor.execute("Select Name from [Admin]")
        name_list = [row[0] for row in cursor.fetchall()]
        if new_name in name_list:
            # print("The name has been used already.")
            return False
        else:
            # print("Done")
            return True

    return True


def stu_profile_info():
    cursor.execute("select * from [Student]")
    user = cursor.fetchall()
    return user


def user_info(role):
    cursor.execute(f"Select * from [{role}]")
    user = cursor.fetchall()
    return user


def select_user(id, role):
    print(generate_user_id(id, role))
    cursor.execute(f"Select * from [{role}] where {role}ID = '{generate_user_id(id, role)}'")
    return cursor.fetchone()


def Select():
    try:
        cursor.execute(f"""
            SELECT 
                ROW_NUMBER() OVER (
                    ORDER BY CAST(SUBSTRING(ChapterID, 4, LEN(ChapterID)) AS INT), LevelRequired
                ) AS NewID,
                * 
            FROM Quiz 
            ORDER BY CAST(SUBSTRING(ChapterID, 4, LEN(ChapterID)) AS INT), LevelRequired;
        """)
        select = cursor.fetchall()
        print("Read: ", select)
        return select
    except IndexError:
        return None


def Retrieve_Question(ids, column="*"):
    quiz_id = ids
    row = []

    num_column = len(column.split(", "))
    with pyodbc.connect(connection_string):
        print("Test: ", generate_quiz_id(quiz_id))
        query = f"SELECT {column} from Question Where QuizID = ? and IsDeleted = 0"
        cursor.execute(query, (generate_quiz_id(quiz_id),))
        if num_column > 1:
            for i in cursor.fetchall():
                row.append(i[0: num_column])
        else:
            for i in cursor.fetchall():
                row.append(i[0])
    return row


def get_last_user_Id():
    cursor.execute(f"SELECT MAX(StudentID) FROM [Student]")
    results = cursor.fetchone()[0]
    return results if results else None  # Fetch the highest ID


def update(table, column, new_value, id, role):
    cursor.execute(f"UPDATE {table} set {column} = {new_value} where {role}ID = '{id}'")
    cursor.commit()


def Chapter_Quiz():
    cursor.execute("select * from chapter where IsDeleted = 0 order by cast(SUBSTRING(ChapterID, 4, len(ChapterID) "
                   "-2) as int)")
    chapter = cursor.fetchall()
    cursor.execute("select * from Quiz where IsDeleted = 0 order by cast(SUBSTRING(ChapterID, 4, len(ChapterID) -2) "
                   "as int), LevelRequired")
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
                           new_options[3], correct_answer, generate_quiz_id(quiz_id), old_question))
    cursor.commit()


def Add_Question(selected_id, admin_name):
    query_id = "SELECT MAX(CAST(SUBSTRING(QuestionID, 2, LEN(QuestionID)) AS INT)) FROM Question"
    query = "Insert into Question values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(query_id)
    id_exe = cursor.fetchone()[0]
    print("ADD: ", id_exe)
    new_ID = 0
    if id_exe:
        new_ID = int(id_exe)
    print(generate_quiz_id(selected_id))
    print("Admin Name: ", admin_name)
    cursor.execute(query, generate_question_id(new_ID + 1), f"Question {new_ID + 1}", "A", "Option 1", "Option 2"
                   , "Option 3", "Option 4", generate_quiz_id(selected_id), admin_name, 0)
    cursor.commit()


def Add_QuizLVL(lvl, chapter):
    query_id = "SELECT MAX(CAST(SUBSTRING(QuizID, 4, LEN(QuizID)) AS INT)) FROM Quiz"
    cursor.execute(query_id)
    result = cursor.fetchone()
    print("QuizID: ", result[0])
    if select(f"Select IsDeleted from Quiz where QuizID = '{generate_quiz_id(result[0])}'")[0][0]:
        update_DB(f"Update Quiz set IsDeleted = 0 where QuizID = '{generate_quiz_id(result[0])}'")
        cursor.commit()
        return int(result[0])
    else:
        query_id = "SELECT MAX(CAST(SUBSTRING(QuizID, 4, LEN(QuizID)) AS INT)) FROM Quiz"
        cursor.execute(query_id)
        id_exe = cursor.fetchone()[0]
        query = "Insert Into Quiz values (?, ?, ?, ?, ?, ?)"
        quiz_id = 0
        print("Quiz: ", id_exe)
        if id_exe:
            quiz_id = int(id_exe)
        print("CHAPTER", chapter)
        cursor.execute(query, generate_quiz_id(quiz_id + 1), "Quiz Name", "Description", lvl, chapter, 0)
        cursor.commit()
        return quiz_id + 1


def Delete_Chapter(chapter_index, quiz_ids):
    print(chapter_index)
    try:
        query = "Delete Chapter where ChapterID = ?"
        quiz_match_delete = "Delete Quiz where ChapterID = ?"

        for i in quiz_ids:
            for questionID in select(f"Select QuestionID from Question where QuizID = '{generate_quiz_id(i)}'"):
                # Attempt to hard delete the question
                try:
                    question_delete_query = "DELETE Question WHERE QuestionID = ?"
                    cursor.execute(question_delete_query,  questionID[0])
                except Exception as e:
                    print("Error: ", e)
        cursor.execute(quiz_match_delete, generate_chapter_id(chapter_index))
        cursor.execute(query, generate_chapter_id(chapter_index))
    except pyodbc.IntegrityError as e:
        print("Delete Chapter: ", e)
        query = "Update Chapter set IsDeleted = 1 where ChapterID = ?"
        quiz_match_delete = "Update Quiz set IsDeleted = 1 where ChapterID = ?"
        question_soft_delete_query = "UPDATE Question SET IsDeleted = 1 WHERE QuizID = ?"
        for quiz in quiz_ids:
            cursor.execute(question_soft_delete_query, generate_quiz_id(quiz))
        cursor.execute(quiz_match_delete, generate_chapter_id(chapter_index))
        cursor.execute(query, generate_chapter_id(chapter_index))
    cursor.commit()


def Add_ChapterDB():
    query_id = "SELECT MAX(CAST(SUBSTRING(ChapterID, 4, LEN(ChapterID)) AS INT)) FROM Chapter"
    cursor.execute(query_id)
    result = cursor.fetchone()
    print("ChapID", result[0])
    print(select(f"Select IsDeleted from Chapter where ChapterID = '{generate_chapter_id(result[0])}'")[0][0])
    if select(f"Select IsDeleted from Chapter where ChapterID = '{generate_chapter_id(result[0])}'")[0][0]:
        update_DB(f"Update Chapter set IsDeleted = 0 where ChapterID = '{generate_chapter_id(result[0])}'")
        cursor.commit()
        return f"CHA{int(result[0]):02d}"
    else:
        query_id = "SELECT MAX(CAST(SUBSTRING(ChapterID, 4, LEN(ChapterID)) AS INT)) FROM Chapter"
        cursor.execute(query_id)
        id_exe = cursor.fetchone()[0]
        query = "Insert Into Chapter values (?, ?, ?)"
        chap_id = 0
        print("Chapter: ", id_exe)
        if id_exe:
            chap_id = int(id_exe)
        cursor.execute(query, generate_chapter_id(chap_id + 1), f"Chapter {chap_id + 1}", 0)
        cursor.commit()
        print("Chapter update")
        return f"CHA{chap_id + 1:02d}"


# def Update_Database(admin_id):
#
#     index = 1
#     Q_index = 1
#     Chapter_query = "Insert Into Chapter values (?, ?)"
#     Quiz_query = "Insert Into Quiz values (?, ?, ?, ?, ?)"
#     Question_query = "Insert Into Question values (?, ?, ?, ?, ?, ?, ?, ?, ?)"
#     for keys, value in chapter.items():
#         cursor.execute(Chapter_query, keys, f"Chapter {keys}")
#         for quiz in value:
#             cursor.execute(Quiz_query, index, quiz[0], quiz[1], quiz[2], int(quiz[3]))
#             for question, Q_value in quiz[4].items():
#                 cursor.execute(Question_query, Q_index, question, Q_value[0], Q_value[1], Q_value[2]
#                                , Q_value[3], Q_value[4], index, admin_id)
#                 Q_index += 1
#             index += 1
#     cursor.commit()

def Delete_QuizLVL(quiz_id):
    query = "Delete Quiz where QuizID = ?"
    print("Delete_QuizLVL: ", generate_quiz_id(quiz_id))
    try:
        cursor.execute(query, generate_quiz_id(quiz_id))
        cursor.commit()
    except pyodbc.IntegrityError:
        return True


def Delete_All(quiz_id):
    try:
        print(quiz_id)
        questionID = [i[0] for i in select(f"Select QuestionID from Question where QuizID = '{generate_quiz_id(quiz_id)}'")]
        question_delete_query = "Delete Question where QuestionID = ?"
        print(questionID)
        for q_id in questionID:
            cursor.execute(question_delete_query, (q_id,))
            cursor.commit()
    except pyodbc.IntegrityError:
        print("Delete All: ", generate_quiz_id(quiz_id))
        # If deletion fails, perform a soft delete: mark the question as deleted.
        # Note: Typically a soft-delete flag is set to 1.
        question_soft_delete_query = "UPDATE Question SET IsDeleted = 1 WHERE QuizID = ?"
        cursor.execute(question_soft_delete_query, generate_quiz_id(quiz_id))
        cursor.commit()
    print("Question: ", generate_quiz_id(quiz_id))


def delete_user(user_id, role):
    if role == "Admin":
        query = f"DELETE FROM Result WHERE GameID in (SELECT GameID FROM Game_Session WHERE StudentID = ?)"
        cursor.execute(query, generate_user_id(user_id[1:], "Student"))
        query = f"DELETE FROM Game_Session WHERE StudentID = ?"
        cursor.execute(query, generate_user_id(user_id[1:], "Student"))
        query = f"DELETE FROM [Student] WHERE StudentID = ?"
        cursor.execute(query, generate_user_id(user_id[1:], "Student"))
        print("HAI")
    elif role == "Owner":
        query = f"DELETE FROM AdminStudent WHERE AdminID = ?"
        cursor.execute(query, generate_user_id(user_id[1:], "Admin"))
        query = f"DELETE FROM [Admin] WHERE AdminID = ?"
        cursor.execute(query, generate_user_id(user_id[1:], "Admin"))
    try:
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
    cursor.execute(query, info[0], info[1], lvl, generate_chapter_id(chapter))
    cursor.commit()


def Delete_Question(quiz_id, questionID, filters):
    print(questionID, quiz_id)
    try:
        query = "Delete Question where QuizID = ? and QuestionID = ?"
        cursor.execute(query, generate_quiz_id(quiz_id), questionID)
    except pyodbc.IntegrityError as e:
        print("Attempt Delete: ", e)
        query = "update Question set IsDeleted = 1 where QuizID = ? and QuestionID = ?"
        cursor.execute(query, generate_quiz_id(quiz_id), questionID)
    cursor.commit()
    print("In Database: ", filters[0], filters[1])
    print(chapter_quizQ)
    if os.path.exists("Quiz_draft2.json"):
        try:
            if len(chapter_quizQ[(filters[0])][filters[1]]) == 1:
                print(chapter_quizQ[(filters[0])][filters[1]])
                os.remove("Quiz_draft2.json")
            else:
                try:
                    chapter_quizQ[filters[0]][filters[1]].pop(str(questionID))
                    with open("Quiz_draft2.json", "w") as File:
                        json.dump(chapter_quizQ, File, indent=4)
                except Exception as e:
                    print("Error", e)
        except Exception as e:
            print("Error: ", e)


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
    # print("Hai" if Select("QuizID", "Question", 2) else "Bye")
    # print(select("Select * from Game_Session where StudentID = 'S0001'"))
    print(pyodbc.drivers())

    # select(f"Select Name from {[i for i in ['Student', 'Admin', 'Owner']]}")
