import sqlite3

conexion = sqlite3.connect("todolist.db")
cursor = conexion.cursor() 
conexion.execute("PRAGMA foreign_keys = ON")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS todolist (
       id  INTEGER PRIMARY KEY AUTOINCREMENT,
       name TEXT NOT NULL,
       days TEXT NOT NULL,
       streak INTEGER DEFAULT 0,
       last_done TEXT
)
""")
cursor.execute("""
    CREATE TABLE IF NOT EXISTS checks (
       id  INTEGER PRIMARY KEY AUTOINCREMENT,
       todo_id INTEGER NOT NULL,
       date TEXT NOT NULL,
       FOREIGN KEY (todo_id)REFERENCES todolist(id) ON DELETE CASCADE,
       UNIQUE(todo_id,date)
)
""")

conexion.commit()
conexion.close()

print ("Database ready.")