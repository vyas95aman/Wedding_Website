from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, make_response, jsonify
from flask_mail import Message, Mail
from flask_session import Session
from functools import wraps
import sqlite3
import random 

# Configure application
app = Flask(__name__)

# Run export FLASK_DEBUG=1 to turn on debug mode
# Any changes are implemented on website, turn off once completed
if __name__ == '__main__':
    app.run(debug=True)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure Flask-Mail to send confirmation emails
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = 'example@gmail.com'
app.config['MAIL_PASSWORD'] = 'tyj th tyh thn'
mail = Mail(app)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure to use SQLite database
# CHANGE TO SQL-ALCHEMY later
db = SQL("sqlite:///wedding.db")

# Configure connection to DynamoDB
# dynamo_resource = boto3.resource('dynamodb', region_name='us-east-2')
# dynamo = dynamo_resource.Table('guestlist')

@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Login required 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin') is not True:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# Password required
def pass_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('auth') is not True:
            return redirect("/landing")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/landing", methods=["GET", "POST"])
def landing():
    if request.method == "POST":
        password = request.form.get('password')
        if password == "3754632":
            session['auth'] = True
            return jsonify({'success': True, 'message': 'Password is correct'})
        else:
            return jsonify({'success': False, 'message': 'Incorrect password. Please try again.'})
    else:
        if session.get("auth") == True:
            return render_template('index.html')
        return render_template("landing.html")

@app.route("/check_names", methods=["POST"])
def check_names():
    data = request.get_json()
    first_name = data.get("firstName")
    last_name = data.get("lastName")
    name = (first_name + " " + last_name).title()
    # id = db.execute("SELECT id FROM guestlist WHERE name=?", name)
    # id = db.execute("SELECT id FROM guestlist WHERE name= :name OR guest_names LIKE :search_text", name=name, search_text=f"%{name}%")
    id = db.execute("SELECT id FROM guestlist WHERE name = :name OR (', ' || guest_names || ', ') LIKE :search_text",
                 name=name, search_text=f"%, {name},%")
    if id:
        if len(id) == 1:
            # print("Length of id is:: ", len(id))
            response = {"valid": id}
        else:
            # print("Longer : Length of id is:: ", len(id))
            # return prompt to pick from id/family members
            response = {"valid": False}
    else:
        response = {"valid": False}
    return jsonify(response)

@app.route("/", methods=["GET", "POST"])
@pass_required
def index():
    if request.method == "POST":
        name = (request.form.get("first name").strip() + " " + request.form.get("last name").strip()).title()
        resp = db.execute("SELECT id FROM guestlist WHERE name = :name OR (', ' || guest_names || ', ') LIKE :search_text",
                 name=name, search_text=f"%, {name},%")[0]
        if resp:
            id = resp['id']
            event = db.execute("SELECT events_invited FROM guestlist WHERE id=?", id)[0]['events_invited']
            event = event.split(" ")[0]
            hash = random.getrandbits(128)
            return redirect(f"/rsvp/{hash}/{id}/017/{event}")
        else:
            flash("An error occured. Please try again.", "warning")
            return redirect('/')
    else:
        if session.get("auth") == True:
            return render_template("index.html")
        else:
            return redirect("/landing")

@app.route("/login", methods=["GET", "POST"])
@pass_required
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if (username, password) == ("admin", "TestPassword"):
            session['admin'] = True
            flash("Welcome Back", "success")
            return redirect("/")
        else: 
            redirect("/login")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session['admin'] = False
    return redirect("/")

@app.route("/todo", methods=["GET", "POST"])
@login_required
@pass_required
def todo():
    if request.method == "POST":
        tag = request.form.get("tag")
        description = request.form.get("description")
        status = request.form.get("status")
        db.execute("INSERT INTO todo (tag, description, status) VALUES (?, ?, ?)", tag, description, status)
        return redirect("/todo")
    else:
        todolist = db.execute("SELECT * FROM todo WHERE  status = 'In Progress' OR status = 'Not Started'")
        completedlist = db.execute("SELECT * FROM todo WHERE status = 'Completed'")
        return render_template("todo.html", todolist=todolist, completedlist=completedlist)

@app.route("/delete", methods=["POST"])
@login_required
@pass_required
def delete():
    item_id = request.form.get("id")
    if item_id:
        db.execute("DELETE FROM todo WHERE id = ?", item_id)
    return redirect("/todo")

@app.route("/status", methods=["POST"])
@login_required
@pass_required
def status():
    item_id = request.form.get("id")
    status = request.form.get("status")
    if status == "Not Started":
        db.execute("UPDATE todo SET status = 'In Progress' WHERE id = ?", item_id)
    elif status == "In Progress":
        db.execute("UPDATE todo SET status = 'Completed' WHERE id = ?", item_id)
    elif status == "Completed":
        db.execute("UPDATE todo SET status = 'Not Started' WHERE id = ?", item_id)
    return redirect("/todo")


@app.route("/guestlist", methods=["GET", "POST"])
@login_required
@pass_required
def guestlist():
    if request.method == "POST":
        title = request.form.get("title")
        name = request.form.get("name").title()
        category = request.form.get("category")
        email = request.form.get("email")
        phone_number = request.form.get("phone number")
        party_size = request.form.get("party size")
        response = request.form.get("response")
        over_21 = request.form.get("over 21")
        events_invited = request.form.getlist("events")
        events_invited = ' '.join(events_invited)
        db.execute("INSERT INTO guestlist (title, name, category, email, phone_number, party_size, responded_rsvp, over_21, events_invited) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", title, name, category, email, phone_number, party_size, response, over_21, events_invited)
        return redirect("/guestlist")
    else:
        guestlist = db.execute("SELECT * FROM guestlist")

        count = db.execute("SELECT Wedding from guestlist WHERE Wedding is not ''")
        wedding_count = 0
        for i in count:
            temp = i['Wedding'].split(", ")
            wedding_count += len(temp)

        count = db.execute("SELECT Shreya_Haldi from guestlist WHERE Shreya_Haldi is not ''")
        Shreya_Haldi_count = 0
        for i in count:
            temp = i['Shreya_Haldi'].split(", ")
            Shreya_Haldi_count += len(temp)

        count = db.execute("SELECT Aman_Haldi from guestlist WHERE Aman_Haldi is not ''")
        Aman_Haldi_count = 0
        for i in count:
            temp = i['Aman_Haldi'].split(", ")
            Aman_Haldi_count += len(temp)

        count = db.execute("SELECT Sangeet from guestlist WHERE Sangeet is not ''")
        sangeet_count = 0
        for i in count:
            temp = i['Sangeet'].split(", ")
            sangeet_count += len(temp)

        count = db.execute("SELECT Reception from guestlist WHERE Reception is not ''")
        reception_count = 0
        for i in count:
            temp = i['Reception'].split(", ")
            reception_count += len(temp)

        return render_template("guestlist.html", guestlist=guestlist, wedding_count=wedding_count, Shreya_Haldi_count=Shreya_Haldi_count, Aman_Haldi_count=Aman_Haldi_count, sangeet_count=sangeet_count, reception_count=reception_count)

@app.route("/removeguest", methods=["POST"])
@login_required
@pass_required
def remove():
    id = request.form.get("id")
    db.execute("DELETE FROM guestlist WHERE id = ?", id)
    return redirect("/guestlist")

@app.route("/editguest/<int:id>", methods=["GET", "POST"])
@login_required
@pass_required
def editguest(id):
    if request.method == "POST":
        title = request.form.get("title")
        name = request.form.get("name")
        category = request.form.get("category")
        email = request.form.get("email")
        phone_number = request.form.get("phone number")
        party_size = int(request.form.get("party size"))
        response = request.form.get("response")
        over_21 = int(request.form.get("over 21"))
        events_invited = request.form.getlist("events invited")
        events_invited = ' '.join(events_invited)
        guests = request.form.getlist("guest name")
        guests = [i for i in guests if i]
        guests = ', '.join(guests)
        db.execute("UPDATE guestlist SET title=?, name=?, category=?, email=?, phone_number=?, party_size=?, responded_rsvp=?, over_21=?, events_invited=?, guest_names=? WHERE id = ?", title, name, category, email, phone_number, party_size, response, over_21, events_invited, guests, id)
        return redirect("/guestlist") 
    else:
        person = db.execute("SELECT * FROM guestlist WHERE id = ?", id)[0]
        guests = person['guest_names'].split(", ")
        guest_num = len(guests)
        return render_template("editguest.html", person=person, guests=guests, guest_num=guest_num)

@app.route("/rsvp/<hash>/<int:id>/017/<event>", methods=["GET", "POST"])
@pass_required
def rsvp(hash, id, event):
    if request.method == "POST":
        db.execute(f"UPDATE guestlist SET {event}='' WHERE id=?", id)
        events_invited = db.execute(f"SELECT events_invited FROM guestlist where id = {id}")[0]['events_invited']
        name = request.form.get("name")
        email = request.form.get("email")
        guests = [i for i in request.form.getlist("guest name") if i]
        guests.insert(0, name)
        attending = []
        for i in range(len(guests)):
            if request.form.get(f"guest {str(i + 1)}") == "Attending":
                attending.append(guests[i])
        guests.pop(0)
        guests = ', '.join(guests)
        attending_number = len(attending)
        attending = ', '.join(attending)
        db.execute(f"UPDATE guestlist SET name=?, email=?, guest_names=?, {event}=?, {event}_Number=? WHERE id=?", name, email, guests, attending, attending_number, id)
        if event == "Shreya_Haldi" and "Sangeet" in events_invited:
            event = "Sangeet"
        elif event == "Aman_Haldi" and "Sangeet" in events_invited:
            event = "Sangeet"
        elif event == "Sangeet" and "Wedding" in events_invited:
            event = "Wedding"
        elif event == "Wedding" and "Reception" in events_invited:
            event = "Reception"
        else:
            db.execute("UPDATE guestlist SET responded_rsvp=? WHERE id=?", "Yes", id)
            person =  db.execute("SELECT * FROM guestlist WHERE id=?", id)[0]
            person['decline'] = False
            if person["Shreya_Haldi"] == "" and person["Aman_Haldi"] == "" and person["Sangeet"] == "" and person["Wedding"] == "" and person["Reception"] == "":
                person['decline'] = True
            send_email(subject="Shreya & Aman's Wedding RSVP Confirmation", template='rsvp_confirmation.html', recipients=[email], sender='amanandshreya2024.com', data=person)
            return (redirect(f"/thankyou/{hash}/{id}"))
        return redirect(f"/rsvp/{hash}/{id}/017/{event}")

    else:
        person = db.execute("SELECT * FROM guestlist WHERE id = ?", id)[0]
        guests = person['guest_names'].split(", ")
        accepted = person[event].split(", ")
        return render_template("rsvp.html", person=person, guests=guests, event=event, accepted=accepted, hash=hash, id=id)
    
@app.route("/thankyou/<hash>/<int:id>", methods=["GET"])
@pass_required
def thankyou(hash, id):
    person =  db.execute("SELECT * FROM guestlist WHERE id=?", id)[0]
    person['decline'] = False
    

    if person["Shreya_Haldi"] == "" and person["Aman_Haldi"] == "" and person["Sangeet"] == "" and person["Wedding"] == "" and person["Reception"] == "":
        person['decline'] = True
    return render_template("thankyou.html", person=person)

def send_email(subject, template, recipients, sender, data):
    msg = Message(subject, recipients=recipients, sender=sender, html=render_template(template, data=data))
    mail.send(msg)
