import sqlite3
import editdistance

def check(name: str, surname = None):
    conn = sqlite3.connect('names/names.db')
    c = conn.cursor()

    min = (len(name) // 2) + 1
    min_name = None

    if surname == None:
        for row in c.execute('''SELECT name, length FROM names WHERE length > ? AND length < ?''', (len(name) - 3, len(name) + 3)):
            if editdistance.eval(name, row[0]) <= min:
                min = editdistance.eval(name, row[0])
                min_name = row    
    else:
        for row in c.execute('''SELECT name, length FROM names WHERE length > ? AND length < ? AND surname = ?''', (len(name) - 3, len(name) + 3, surname)):
            if editdistance.eval(name, row[0]) <= min:
                min = editdistance.eval(name, row[0])
                min_name = row
    
    if min_name == None:
        return name
    else:
        return min_name[0]