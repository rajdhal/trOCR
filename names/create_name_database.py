import sqlite3
import csv

def create_name_database():
    conn = sqlite3.connect('names.db')
    c = conn.cursor()

    data = []
    c.execute('''CREATE TABLE IF NOT EXISTS names(name TEXT, length INTEGER, surname INTEGER)''')

    with open('499_first_names_lengths.csv', 'r') as f:
        data = list(csv.reader(f))
    for row in data:
        c.execute('''INSERT INTO names VALUES(?,?, FALSE)''', (row[0], row[1]))
    
    with open('499_last_names_lengths.csv', 'r') as f:
        data = list(csv.reader(f))
    for row in data:
        c.execute('''INSERT INTO names VALUES(?,?, TRUE)''', (row[0], row[1]))

    conn.commit()
    conn.close()

create_name_database()