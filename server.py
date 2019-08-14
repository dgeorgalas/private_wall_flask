import re, datetime
from flask import Flask, render_template, request, redirect, session, flash
from mysqlconnection import connectToMySQL
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 

db = connectToMySQL('private_wall')

app = Flask(__name__)
app.secret_key = "keep it secret, keep it safe"

@app.route('/')
def login_reg():
    return render_template('login_reg.html')

@app.route('/login', methods=["POST"])
def login():
    query = f"SELECT * FROM users WHERE email = '{request.form['log_email']}' AND password = '{request.form['log_password']}';"
    data = {
        'log_email' : request.form['log_email'],
        'log_password' : request.form['log_password']
    }
    user = db.query_db(query, data)
    print(user)

    if user :
        session['first_name'] = user[0]['first_name']
        session['id'] = user[0]['id']
        print(session['id'])
        print(session['first_name'])
        return redirect('wall')
    else: 
        return redirect('/')


@app.route('/register', methods=["POST"])
def create_user():
    is_valid = True 
    if len(request.form['first_name']) < 2:
        is_valid = False
        flash("First Name must be more than 2 characters!")
    if len(request.form['last_name']) < 2:
        is_valid = False
        flash("Last Name must be more than 2 characters!")
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Invalid email address!")
    if len(request.form['password']) < 8:
        is_valid = False
        flash("Password must be more than 8 characters!")
    if request.form['confirm PW'] != request.form['password']:
        is_valid = False
        flash("Passwords must match!")
    if not is_valid:
        return redirect('/')


    else:

        query = "INSERT INTO users (first_name, last_name, email, password, Created_At, Updated_At) VALUES (%(fn)s, %(ln)s, %(e)s, %(p)s, NOW(), NOW());"
        data = {
            "fn" : request.form['first_name'],
            "ln" : request.form['last_name'],
            "e" : request.form['email'],
            "p" : request.form['password']
            }
        session['first_name'] = request.form['first_name']
        user_id = db.query_db(query, data)
        session['id'] = user_id
        return redirect('wall')


@app.route('/wall')
def wall():
    if not session:
        return redirect('/')

    else:

        db = connectToMySQL('private_wall')
        users = db.query_db(f"SELECT * FROM users ORDER BY first_name;")
        messages = db.query_db(f"SELECT * FROM messages WHERE sent_to_id = '{session['id']}';")
        to_messages = db.query_db(f"SELECT COUNT(id) FROM messages WHERE sent_from_id = '{session['id']}';")
        from_messages = db.query_db(f"SELECT COUNT(id) FROM messages WHERE sent_to_id = '{session['id']}';")

        messages_received = from_messages[0]['COUNT(id)']
        messages_sent = to_messages[0]['COUNT(id)']

        print(users)
    

        return render_template('wall.html', users = users, messages = messages, messages_sent = messages_sent, messages_received = messages_received)

@app.route('/send_message', methods=["POST"])
def send_message():
    db=connectToMySQL('private_wall')
    query = "INSERT INTO messages (description, Created_At, Updated_At, sent_from_id, sent_to_id, sent_from_first_name) VALUES (%(d)s, NOW(), NOW(), %(sf)s, %(st)s, %(fn)s);"
    data = {
        "d" : request.form['description'],
        "sf" : session['id'],
        "st" : request.form['recipient_id'],
        "fn" : session['first_name']
    }
    message = db.query_db(query, data)
    print(message)
    return redirect('wall')

@app.route('/delete_message', methods=["POST"])
def delete_message():
    query = f"DELETE FROM messages WHERE id = '{request.form['message_id']}';"
    db.query_db(query)
    return redirect('wall')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)