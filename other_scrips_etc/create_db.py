import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    passwd="yourpassword",
)

my_cursor = mydb.cursor()
# my_cursor.execute("CREATE DATABASE IF NOT EXISTS users")
my_cursor.execute("SHOW DATABASES")

for db in my_cursor:
    print(db)
