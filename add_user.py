import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)",
               ("admin", "1234"))

conn.commit()
conn.close()

print("Usuário criado com sucesso!")