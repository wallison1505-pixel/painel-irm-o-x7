import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM usuarios")
dados = cursor.fetchall()

for d in dados:
    print(d)

conn.close()