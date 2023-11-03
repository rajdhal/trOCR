import sqlite3
import editdistance

def check(name: str):
    conn = sqlite3.connect('names/names.db')
    c = conn.cursor()

    min = 4
    min_name = None

    for row in c.execute('''SELECT name, length FROM names WHERE length > ? AND length < ?''', (len(name) - 3, len(name) + 3)):
        if editdistance.eval(name, row[0]) < min:
            min = editdistance.eval(name, row[0])
            min_name = row
    
    if min_name == None:
        return name
    else:
        return min_name[0]