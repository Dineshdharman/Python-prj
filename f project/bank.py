from MySQLdb._mysql import escape_string
from flask import Flask, session, render_template, redirect, request, url_for
import mysql.connector

# --------------------------------------------------------------------------------------------------------------------
app = Flask(__name__)


def get_db_cursor():
    con = mysql.connector.connect(host="localhost", user="root", password="password", database="bank")
    cursor = con.cursor()
    return con, cursor


@app.route('/')
def home():
    if 'username' in session:
        return redirect('/')
    return render_template('blogin.html')


@app.route('/choice')
def choice():
    account_type = request.args.get('account_type')
    if account_type == 'savings':
        session['account_type'] = 'savings'
        return redirect(url_for('sav_dashboard'))
    elif account_type == 'current':
        session['account_type'] = 'current'
        return redirect(url_for('cur_dashboard'))
    else:
        return render_template("choice1.html")


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    con, cursor = get_db_cursor()
    cursor.execute('SELECT * FROM userdetails WHERE username=%s AND password=%s', (username, password))
    user = cursor.fetchone()
    cursor.close()
    con.close()
    if user:
        session['username'] = username
        session['password'] = password
        return redirect('/choice')
    else:
        return render_template('/blogin.html', message='Invalid username or password')


@app.route('/sav_dashboard')
def sav_dashboard():
    if 'username' not in session:
        return redirect('/')
    con, cursor = get_db_cursor()
    cursor.execute('SELECT * FROM bankdetails')
    res = cursor.fetchall()
    cursor.close()
    con.close()
    username1 = session['username']
    return render_template('sav_dashboard.html', username=username1, datas=res)


@app.route('/cur_dashboard')
def cur_dashboard():
    if 'username' not in session:
        return redirect('/')
    con, cursor = get_db_cursor()
    cursor.execute('SELECT * FROM curbankdetails')
    res = cursor.fetchall()
    cursor.close()
    con.close()
    username1 = session['username']
    return render_template('cur_dashboard.html', username=username1, datas=res)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        account_type = request.args.get('account_type')
        if account_type == 'savings' or account_type == 'current':
            session['account_type'] = account_type
            return render_template("signup.html")
        else:
            return render_template("choice.html")
    elif request.method == 'POST':
        accno = request.form['AccNo']
        name = request.form['Name']
        amount = request.form['Amount']
        username = request.form['username']
        password = request.form['password']
        account_type = session.get('account_type')
        con, cursor = get_db_cursor()
        if account_type == 'savings':
            cursor.execute('INSERT INTO bankdetails(AccNo,Username,Amount) VALUES (%s,%s,%s)', (accno, name, amount))
        elif account_type == 'current':
            cursor.execute('INSERT INTO curbankdetails(AccNo,Username,Amount) VALUES (%s,%s,%s)', (accno, name, amount))
        else:
            return "Invalid account type"

        cursor.execute('INSERT INTO userdetails(username,password) VALUES (%s,%s)', (username, password))
        con.commit()
        return redirect('/')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route("/withdraw/<string:id>", methods=['GET', 'POST'])
def withdraw(id):
    if 'username' not in session:
        return redirect('/')

    con, cursor = get_db_cursor()
    current_account_type = session.get('account_type')
    if current_account_type == 'savings':
        table_name = 'bankdetails'
    elif current_account_type == 'current':
        table_name = 'curbankdetails'

    if request.method == 'POST':
        amount = float(request.form['Amount'])

        cursor.execute(f'SELECT * FROM {table_name} WHERE AccNo=%s', (id,))
        res = cursor.fetchone()
        if res:
            current_balance = float(res[2])
            if current_balance >= amount:
                new_balance = current_balance - amount
                cursor.execute(f'UPDATE {table_name} SET Amount=%s WHERE AccNo=%s', (new_balance, id))
                con.commit()
                current_account_type = session.get('account_type')
                if current_account_type == 'savings':
                    return redirect(url_for('sav_dashboard'))
                elif current_account_type == 'current':
                    return redirect(url_for('cur_dashboard'))
            else:
                return render_template("withdraw.html", message="Insufficient Balance")
        else:
            return render_template("withdraw.html", message="Invalid Account Number")
    cursor.execute(f'SELECT * FROM {table_name} WHERE AccNo=%s', (id,))
    res = cursor.fetchone()
    cursor.close()
    con.close()
    return render_template("withdraw.html", datas=res)


@app.route("/credit/<string:id>", methods=['GET', 'POST'])
def credit(id):
    con, cursor = get_db_cursor()
    current_account_type = session.get('account_type')
    if current_account_type == 'savings':
        table_name = 'bankdetails'
    elif current_account_type == 'current':
        table_name = 'curbankdetails'

    if 'username' not in session:
        return redirect('/')

    if request.method == 'POST':
        amount = float(request.form['Amount'])
        cursor.execute(f'SELECT * FROM {table_name} WHERE AccNo=%s', (id,))
        res = cursor.fetchone()
        if res:
            current_balance = float(res[2])
            if current_balance <= 100000000:
                new_balance = current_balance + amount
                cursor.execute(f'UPDATE {table_name} SET Amount=%s WHERE AccNo=%s', (new_balance, id))
                con.commit()
                current_account_type = session.get('account_type')
                if current_account_type == 'savings':
                    return redirect(url_for('sav_dashboard'))
                elif current_account_type == 'current':
                    return redirect(url_for('cur_dashboard'))
            else:
                return render_template("credit.html", message="You have reached the limit")
        else:
            return render_template("credit.html", message="Invalid Account Number")
    cursor.execute(f"SELECT * FROM {table_name} WHERE AccNo=%s", (id,))
    res = cursor.fetchone()
    cursor.close()
    con.close()
    return render_template("credit.html", datas=res)


# -------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    app.secret_key = '12345'
    app.run(debug=True)
