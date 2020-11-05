from .database import Database


def rename_user(user_id, username):
    database = Database()
    database.rename_user(user_id, username)
    database.close_connection()
