from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Configuration for MySQL connection
mysql_config = {
    "host": "localhost",
    "user": "root",
    "password": "Dine@2003",
    "db": "bike",
    "cursorclass": pymysql.cursors.DictCursor  # Set cursor class to DictCursor
}

# Function to connect to MySQL database
def connect_to_database():
    return pymysql.connect(**mysql_config)

# Route for home page
@app.route("/")
def home():
    con = connect_to_database()
    with con.cursor() as cur:
        sql = "SELECT * FROM cardetails"
        cur.execute(sql)
        res = cur.fetchall()
    con.close()
    return render_template("home.html", datas=res)

# Route to add user
@app.route('/adduser', methods=['GET', 'POST'])
def adduser():
    if request.method == 'POST':
        name = request.form['Name']
        dob = request.form['DOB']
        age = request.form['Age']
        phonenumber = request.form['PhoneNumber']
        con = connect_to_database()
        with con.cursor() as cur:
            sql = "INSERT INTO cardetails(Name,DOB,Age,PhoneNumber) VALUES (%s,%s,%s,%s)"
            cur.execute(sql, (name, dob, age, phonenumber))
            con.commit()
        con.close()
        flash('User details added successfully')
        return redirect(url_for("home"))
    return render_template("adduser.html")

# Route to edit user details
@app.route("/edit/<string:id>", methods=['GET', 'POST'])
def edit(id):
    con = connect_to_database()
    with con.cursor() as cur:
        if request.method == 'POST':
            name = request.form['Name']
            dob = request.form['DOB']
            age = request.form['Age']
            phonenumber = request.form['PhoneNumber']
            sql = "UPDATE cardetails SET Name=%s, DOB=%s, Age=%s, PhoneNumber=%s WHERE ID=%s"
            cur.execute(sql, (name, dob, age, phonenumber, id))
            con.commit()
            flash('User details updated successfully')
            return redirect(url_for("home"))

        sql = "SELECT * FROM cardetails WHERE ID=%s"
        cur.execute(sql, (id,))
        res = cur.fetchone()
    con.close()
    return render_template("edit.html", datas=res)

# Route to delete user
@app.route("/deleteUser/<string:id>", methods=['GET', 'POST'])
def deleteUser(id):
    con = connect_to_database()
    with con.cursor() as cur:
        sql = "DELETE FROM cardetails WHERE id=%s"
        cur.execute(sql, (id,))
        con.commit()
        flash('User details deleted successfully')
    con.close()
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
