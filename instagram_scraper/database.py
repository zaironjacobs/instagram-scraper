import sqlite3
import logging
import uuid

from . import constants

logger = logging.getLogger('__name__')


class Database:

    def __init__(self):
        self.__connection = sqlite3.connect(constants.LOCAL_DB)
        self.__connection.execute("PRAGMA foreign_keys = 1")

    def create_tables(self):
        cursor = self.__connection.cursor()

        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS user (id INTEGER PRIMARY KEY UNIQUE, username TEXT);")

            cursor.execute("CREATE TABLE IF NOT EXISTS tag " +
                           "(id TEXT PRIMARY KEY UNIQUE, tagname TEXT UNIQUE);")

            cursor.execute("CREATE TABLE IF NOT EXISTS post " +
                           "(id TEXT PRIMARY KEY UNIQUE, link TEXT, has_multiple_content INTEGER, " +
                           "user_id INTEGER, " +
                           "FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE SET NULL );")

            cursor.execute("CREATE TABLE IF NOT EXISTS tag_post " +
                           "(tag_id TEXT, post_id TEXT, in_top TEXT, in_recent INTEGER, " +
                           "FOREIGN KEY(tag_id) REFERENCES tag(id) ON DELETE CASCADE, " +
                           "FOREIGN KEY(post_id) REFERENCES post(id) ON DELETE CASCADE, " +
                           "PRIMARY KEY(tag_id, post_id) );")

        except sqlite3.Error as err:
            logger.error(err)
            print('SQL error at creating tables.')
        finally:
            cursor.close()

    def __execute_query_and_commit(self, query, dict_values=None):
        if dict_values is None:
            dict_values = {}

        cursor = self.__connection.cursor()
        try:
            cursor.execute(query, dict_values)
        except sqlite3.Error as err:
            logger.error('error at executing query: %s' % query)
            logger.error('error: %s' % err)
        finally:
            self.__connection.commit()
            cursor.close()

    def __execute_query_and_fetch(self, query):
        cursor = self.__connection.cursor()

        try:
            cursor.execute(query)
        except sqlite3.Error as err:
            logger.error('error at executing query: %s' % query)
            logger.error('error: %s' % err)
        finally:
            data = cursor.fetchall()
            cursor.close()
            return data

    def insert_tag(self, tag):
        query = "INSERT OR IGNORE INTO tag VALUES (:id, :tagname);"
        values = {'id': str(uuid.uuid4()), 'tagname': tag}
        self.__execute_query_and_commit(query, values)

    def insert_tag_post(self, link, tag, in_top=False, in_recent=False):
        query = "INSERT OR IGNORE INTO tag_post VALUES (:tag_id, :post_id, :in_top, :in_recent);"
        post_id = self.__get_post_id(link)
        tag_id = self.__get_tag_id(tag)
        values = {'tag_id': tag_id, 'post_id': post_id, 'in_top': in_top, 'in_recent': in_recent}
        self.__execute_query_and_commit(query, values)

    def insert_userid_and_username(self, userid, username):
        query = "INSERT OR IGNORE INTO user(id, username) VALUES (:id, :username);"
        values = {'id': userid, 'username': username}
        self.__execute_query_and_commit(query, values)

    def insert_post(self, link, has_multiple_content, userid=None):
        post_id = self.__get_post_id(link)

        if all(v is not None for v in [post_id, userid]):
            query = "UPDATE post SET user_id =" + userid + " WHERE id ='" + post_id + "';"
            self.__execute_query_and_commit(query)
        elif not post_id:
            query = "INSERT INTO post VALUES (:id, :link, :has_multiple_content, :user_id);"
            values = {'id': str(uuid.uuid4()), 'link': link, 'has_multiple_content': has_multiple_content,
                      'user_id': userid}
            self.__execute_query_and_commit(query, values)

    def retrieve_all_usernames(self):
        query = "SELECT username FROM user ORDER BY username ASC;"
        data = self.__execute_query_and_fetch(query)

        usernames = []
        for username in data:
            usernames.append(username[0])
        return sorted(usernames)

    def retrieve_all_tags(self):
        query = "SELECT tagname FROM tag ORDER BY tagname ASC;"
        data = self.__execute_query_and_fetch(query)

        tags = []
        for username in data:
            tags.append(username[0])
        return sorted(tags)

    def __get_post_id(self, link):
        query = "SELECT id FROM post WHERE link ='" + link + "';"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            return data[0][0]
        return None

    def __get_tag_id(self, tagname):
        query = "SELECT id FROM tag WHERE tagname ='" + tagname + "';"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            return data[0][0]
        return None

    def get_username_by_id(self, user_id):
        query = "SELECT username FROM user WHERE id =" + str(user_id) + ";"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            return data[0][0]
        return None

    def get_user_post_links(self, userid):
        query = "SELECT link FROM post WHERE user_id='" + userid + "';"
        data = self.__execute_query_and_fetch(query)

        post_links = []
        for row in data:
            post_links.append(row[0])
        return post_links

    def user_post_link_exists(self, username, link):
        query = "SELECT EXISTS (SELECT 1 FROM post WHERE link ='" + link + "' AND user_id=(SELECT id FROM user WHERE" \
                + " username='" + username + "') LIMIT 1);"
        data = self.__execute_query_and_fetch(query)
        result = data[0][0]

        if result == 1:
            return True
        return False

    def user_exists(self, username):
        query = "SELECT EXISTS( SELECT 1 FROM user WHERE username='" + username + "' LIMIT 1);"
        data = self.__execute_query_and_fetch(query)
        result = data[0][0]

        if result == 1:
            return True
        return False

    def tag_exists(self, tagname):
        query = "SELECT EXISTS( SELECT 1 FROM tag WHERE tagname='" + tagname + "' LIMIT 1);"
        data = self.__execute_query_and_fetch(query)
        result = data[0][0]

        if result == 1:
            return True
        return False

    def get_id_by_username(self, username):
        query = "SELECT id FROM user WHERE username ='" + username + "';"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            return data[0][0]
        return None

    def get_user_post_count(self, username):
        query = "SELECT COUNT(*) FROM post WHERE user_id =(SELECT id FROM user WHERE username ='" \
                + username + "');"
        data = self.__execute_query_and_fetch(query)
        post_count = data[0][0]
        return post_count

    def get_top_tag_post_count(self, tag):
        tag_id = self.__get_tag_id(tag)
        query = "SELECT COUNT(*) FROM tag_post WHERE tag_id ='" + tag_id + "' AND in_top=1;"
        data = self.__execute_query_and_fetch(query)
        post_count = data[0][0]
        return post_count

    def get_recent_tag_post_count(self, tag):
        tag_id = self.__get_tag_id(tag)
        query = "SELECT COUNT(*) FROM tag_post WHERE tag_id ='" + tag_id + "' AND in_recent=1;"
        data = self.__execute_query_and_fetch(query)
        post_count = data[0][0]
        return post_count

    def rename_user(self, user_id, new_username):
        query = "UPDATE user SET username ='" + new_username + "' WHERE id =" + str(user_id) + ";"
        self.__execute_query_and_commit(query)

    def remove_user(self, username):
        query = "SELECT username FROM user WHERE username='" + username + "';"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            query = "DELETE FROM user WHERE username = (:username);"
            values = {'username': username}
            self.__execute_query_and_commit(query, values)
            self.remove_unused_posts()

    def remove_all_users(self):
        query = "DELETE FROM user"
        self.__execute_query_and_commit(query)
        self.remove_unused_posts()

    def remove_tag(self, tag):
        query = "SELECT tagname FROM tag WHERE tagname='" + tag + "';"
        data = self.__execute_query_and_fetch(query)

        if len(data) > 0:
            query = "DELETE FROM tag WHERE tagname = (:tagname);"
            values = {'tagname': tag}
            self.__execute_query_and_commit(query, values)
            self.remove_unused_posts()

    def remove_all_tags(self):
        query = "DELETE FROM tag"
        self.__execute_query_and_commit(query)

        query = "DELETE FROM tag_post"
        self.__execute_query_and_commit(query)

        self.remove_unused_posts()

    def remove_unused_posts(self):
        query = "DELETE FROM post WHERE user_id is NULL and id NOT IN (SELECT post_id FROM tag_post)"
        self.__execute_query_and_commit(query)

    def close_connection(self):
        self.__connection.close()
