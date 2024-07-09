import MySQLdb

try:
    con = MySQLdb.connect(host="localhost", user="root", password="Dine@2003", db="bike")
    cur = con.cursor()
    cur.execute("SELECT VERSION()")
    data = cur.fetchone()
    print("Database version:", data)
    con.close()
except MySQLdb.Error as e:
    print(f"Error: {e}")
