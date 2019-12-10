# test-mysql-connection.py
# Largely taken from https://pynative.com/python-mysql-database-connection/

from mysql.connector import connect, Error
import os


def main():
    try:
        con = connect(
            database=os.getenv('MYSQL_DB'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASS'),
        )
        if con.is_connected():
            print("Connected to MySQL server version %s" % con.get_server_info())
            cur = con.cursor()
            cur.execute("select database();")
            print("Connected to database: %s" % cur.fetchone())
            cur.close()

    except Error as e:
        con = None
        print("Error while connecting to MySQL: %s" % e)
        exit(1)

    finally:
        if con is not None and con.is_connected():
            con.close()
            print("Closed connection.")


if __name__ == "__main__":
    main()
