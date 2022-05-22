import pyodbc
from database.Singleton import Singleton


@Singleton
class DBConnection(object):

    def __init__(self):
        self.server = 'proiectcccloud.database.windows.net'
        self.database = 'cloud'
        self.username = 'admincc'
        self.password = '{Password8}'
        self.driver = '{ODBC Driver 17 for SQL Server}'

    def create_connection(self):
        return pyodbc.connect(
            'DRIVER=' + self.driver + ';SERVER=tcp:' + self.server + ';PORT=1433;DATABASE=' + self.database + ';UID=' + self.username + ';PWD=' + self.password)
