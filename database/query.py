from database.connection import DBConnection


class Query:

    def __init__(self):
        pass

    def return_all(self):
        Dbinstance = DBConnection.Instance()
        conn = Dbinstance.create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM test")
            # cursor.execute("INSERT INTO test VALUES(68)")
            # conn.commit()
        row = cursor.fetchone()
        result = str(row[0])
        while row:
            print(str(row[0]))
            row = cursor.fetchone()
        return result