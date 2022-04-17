import sqlite3

print("\nsetting up database")

conn = sqlite3.connect("prefixes.db")
print("connected")

conn.execute("""CREATE TABLE PREFIXES
    (guildID INT PRIMARY KEY NOT NULL,
     prefix CHAR(10) NOT NULL);""")
print("table created")

conn.close()
