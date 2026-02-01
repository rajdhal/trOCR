import sqlite3
import editdistance

def check(name: str, surname = None):
    conn = sqlite3.connect('names/names.db')
    c = conn.cursor()

    min_dist = (len(name) // 2) + 1
    min_name = None

    try:
        if surname is None:
            for row in c.execute('''SELECT name, length FROM names WHERE length > ? AND length < ?''', (len(name) - 3, len(name) + 3)):
                dist = editdistance.eval(name, row[0])
                if dist <= min_dist:
                    min_dist = dist
                    min_name = row    
        else:
            for row in c.execute('''SELECT name, length FROM names WHERE length > ? AND length < ? AND surname = ?''', (len(name) - 3, len(name) + 3, surname)):
                dist = editdistance.eval(name, row[0])
                if dist <= min_dist:
                    min_dist = dist
                    min_name = row
    finally:
        conn.close()
    
    if min_name is None:
        return name
    else:
        return min_name[0]