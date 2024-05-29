from flask import Flask,render_template,session,request,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
import json
import subprocess
from flask_mail import Mail, Message
from sqlalchemy.orm import Session
from forms import ContactForm
import os
from flask import Flask, request, jsonify
from wit import Wit
from sqlalchemy import or_
from datetime import datetime
from flask import Flask, request, jsonify
import cv2
import numpy as np
import base64

# MY db connection
local_server= True
app = Flask(__name__)
app.secret_key='123'


# Load your pre-trained face recognition model
# Example using OpenCV's pre-trained model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


#hashing for password
app.config['MAIL_PORT'] = 587  # Port for TLS/STARTTLS
app.config['MAIL_USE_TLS'] = True  # Enable TLS/STARTTLS
app.config['MAIL_USERNAME'] = 'zaidimojiz4@gmail.com'
app.config['MAIL_PASSWORD'] = 'xawu xifl dtvx pese'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
#app.config['MAIL_USERNAME'] = os.environ.get('Mail_Username')
#app.config['MAIL_PASSWORD'] = os.environ.get('Mail_Password')
mail = Mail(app)

app.config['MAIL_DEBUG'] = True


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# Initialize Wit.ai client
client = Wit('XOWOBMFCQSBVMSDYQDO376HWODSR5KDS')


@login_manager.user_loader
def load_user(user_id):
    session = db.session
    return session.get(User, int(user_id))


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:1735@localhost/sms'
db=SQLAlchemy(app)




# here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))
    

class Department(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    branch=db.Column(db.String(100))

class Attendence(db.Model):
    aid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    attendance=db.Column(db.Integer())

class Trig(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(100))
    action=db.Column(db.String(100))
    timestamp=db.Column(db.String(100))


class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))
  #  image_url = db.Column(db.String(200))  




class Student(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    rollno=db.Column(db.String(50))
    sname=db.Column(db.String(50))
    sem=db.Column(db.Integer)
    gender=db.Column(db.String(50))
    branch=db.Column(db.String(50))
    email=db.Column(db.String(50))
    number=db.Column(db.String(12))
    address=db.Column(db.String(100))
    
    
    
class ContactSubmission(db.Model):
    __tablename__ = 'form_submissions'  # Match the actual table name in your database

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    submission_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    


# Define the Log model for the database table/chatbot
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(255))
    query = db.Column(db.String(255))
    response = db.Column(db.String(255))

# Function to insert log entries/chatbot
def insert_log(action, query, response):
    log_entry = Log(action=action, query=query, response=response)
    db.session.add(log_entry)
    db.session.commit()


    

@app.route('/')
def index(): 
    return render_template('index.html')


@app.route('/about')
@login_required
def about():
    user = User.query.filter_by(id=current_user.id).first()
    return render_template('about.html', user=user)

@app.route('/studentdetails')
def studentdetails():
    # query=db.engine.execute(f"SELECT * FROM `student`") 
    query=Student.query.all() 
    return render_template('studentdetails.html',query=query)

@app.route('/triggers')
def triggers():
    # query=db.engine.execute(f"SELECT * FROM `trig`") 
    query=Trig.query.all()
    return render_template('triggers.html',query=query)

@app.route('/department',methods=['POST','GET'])
def department():
    if request.method=="POST":
        dept=request.form.get('dept')
        query=Department.query.filter_by(branch=dept).first()
        if query:
            flash("Department Already Exist","warning")
            return redirect('/department')
        dep=Department(branch=dept)
        db.session.add(dep)
        db.session.commit()
        flash("Department Added","success")
    return render_template('department.html')

@app.route('/addattendance', methods=['POST', 'GET'])
def addattendance():
    query = Student.query.all()
    try:
        if request.method == "POST":
            rollno = request.form.get('rollno')
            attend = request.form.get('attend')
            # Check if attendance for this roll number exists
            atte = Attendence.query.filter_by(rollno=rollno).first()
            if atte:
                # If attendance exists, update it
                atte.attendance = attend
                flash("Attendance updated", "success")
            else:
                # If attendance doesn't exist, create a new entry
                atte = Attendence(rollno=rollno, attendance=attend)
                db.session.add(atte)
                flash("Attendance added", "warning")
            db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        flash("Failed to update attendance due to database error", "error")
        print(str(e))  # Log the error for debugging

    return render_template('attendance.html', query=query)


@app.route('/search',methods=['POST','GET'])
def search():
    if request.method=="POST":
        rollno=request.form.get('roll')
        bio=Student.query.filter_by(rollno=rollno).first()
        attend=Attendence.query.filter_by(rollno=rollno).first()
        return render_template('search.html',bio=bio,attend=attend)
        
    return render_template('search.html')

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    post=Student.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    # db.engine.execute(f"DELETE FROM `student` WHERE `student`.`id`={id}")
    flash("Slot Deleted Successful","danger")
    return redirect('/studentdetails')


@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    # dept=db.engine.execute("SELECT * FROM `department`")    
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        sem=request.form.get('sem')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        # query=db.engine.execute(f"UPDATE `student` SET `rollno`='{rollno}',`sname`='{sname}',`sem`='{sem}',`gender`='{gender}',`branch`='{branch}',`email`='{email}',`number`='{num}',`address`='{address}'")
        post=Student.query.filter_by(id=id).first()
        post.rollno=rollno
        post.sname=sname
        post.sem=sem
        post.gender=gender
        post.branch=branch
        post.email=email
        post.number=num
        post.address=address
        db.session.commit()
        flash("Slot is Updated","success")
        return redirect('/studentdetails')
    dept=Department.query.all()
    posts=Student.query.filter_by(id=id).first()
    return render_template('edit.html',posts=posts,dept=dept)


@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method == "POST":
        username=request.form.get('username')
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exist","warning")
            return render_template('/signup.html')
        encpassword=generate_password_hash(password)

        # new_user=db.engine.execute(f"INSERT INTO `user` (`username`,`email`,`password`) VALUES ('{username}','{email}','{encpassword}')")

        # this is method 2 to save data in db
        newuser=User(username=username,email=email,password=encpassword)
        db.session.add(newuser)
        db.session.commit()
        flash("Signup Succes Please Login","success")
        return render_template('login.html')

          

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/addstudent',methods=['POST','GET'])
@login_required
def addstudent():
    # dept=db.engine.execute("SELECT * FROM `department`")
    dept=Department.query.all()
    if request.method=="POST":
        rollno=request.form.get('rollno')
        sname=request.form.get('sname')
        sem=request.form.get('sem')
        gender=request.form.get('gender')
        branch=request.form.get('branch')
        email=request.form.get('email')
        num=request.form.get('num')
        address=request.form.get('address')
        # query=db.engine.execute(f"INSERT INTO `student` (`rollno`,`sname`,`sem`,`gender`,`branch`,`email`,`number`,`address`) VALUES ('{rollno}','{sname}','{sem}','{gender}','{branch}','{email}','{num}','{address}')")
        query=Student(rollno=rollno,sname=sname,sem=sem,gender=gender,branch=branch,email=email,number=num,address=address)
        db.session.add(query)
        db.session.commit()

        flash("Booking Confirmed","info")


    return render_template('student.html',dept=dept)


@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return 'My db is not Connected'

# Define route for contact page
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    user=current_user
    # Create an instance of the ContactForm
    form = ContactForm()
    
    # Check if form is submitted and valid
    if form.validate_on_submit():
        # Handle form submission
        flash('Message sent successfully!', 'success')
        return redirect(url_for('index'))
    
    # Render contact.html template with form object
    return render_template('contact.html', form=form,user=user)



@app.route('/submit_contact_form', methods=['POST'])
def submit_contact_form():
    user=current_user
    if request.method == 'POST':
        # Access form data
        name = request.form.get('name')
        email = request.form.get('email')
       # phone = request.form.get('phone')
        message = request.form.get('message')
        
        # Create a new instance of ContactSubmission model
        submission = ContactSubmission(name=name, email=email,  message=message)
        
        # Add the submission to the database session
        db.session.add(submission)
        
        # Commit the session to save the submission in the database
        db.session.commit()
        
        # Process form data (e.g., send email)
        msg = Message('New Contact Form Submission', sender=email, recipients=['syed.zaidi@agu.edu.tr'])
        msg.body = f"Name: {name}\nEmail: {email} \nMessage: {message}"
        mail.send(msg)
        
        # Flash a success message
        flash('Message sent successfully!', 'success')
        
        # Redirect to a thank you page
        return render_template('thanks.html', user=user)





@app.route("/webhook", methods=["POST"])
@app.route("/chat", methods=["POST"])
def webhook():
    data = request.json
    print("Received data:", data)  # Print the entire JSON data received in the request

    user_message = data.get("message")

    if user_message:
        # Send user's message to Wit.ai for processing
        wit_response = client.message(user_message)
        # Print wit_response for debugging
        print(wit_response)

        # Parse Wit.ai response to extract intent and entities
        intent = (
            wit_response["intents"][0]["name"] if "intents" in wit_response else None
        )
        entities = wit_response.get("entities", {})

        # Business logic based on intent and entities
        if intent == 'register_student':
            # Extract entities like roll number, name, email, etc.
            rollno_entity = entities.get('wit$number:rollno', [{}])[0]
            sname_entity = entities.get('student_name:student_name', [{}])[0]
            email_entity = entities.get('wit$email:email', [{}])[0]
            branch_entity = entities.get('department:department', [{}])[0]
            phone_entity = entities.get('wit$phone_number:phone_number', [{}])[0]
            address_entity = entities.get('address:address', [{}])[0]
            gender_entity = entities.get('gender:gender', [{}])[0]
            sem_entity = entities.get('wit$number:sem', [{}])[0]

            # Check if all required entities are present
            if rollno_entity and sname_entity and email_entity and branch_entity and phone_entity and address_entity and gender_entity and sem_entity:
                # Extract values from entities
                rollno = rollno_entity.get('value')
                sname = sname_entity.get('value')
                email = email_entity.get('value')
                branch = branch_entity.get('value')
                phone = phone_entity.get('value')
                address = address_entity.get('value')
                gender = gender_entity.get('value')
                sem = sem_entity.get('value')

                # Create a new student entry in the database
                new_student = Student(rollno=rollno, sname=sname, email=email, branch=branch,
                                      number=phone, address=address, gender=gender, sem=sem)
                db.session.add(new_student)
                try:
                    db.session.commit()
                    bot_response = f"Student {sname} with roll number {rollno} has been registered successfully."
                    # Insert log entry
                    insert_log('register_student', user_message, bot_response)
                    db.session.commit()  # Commit after logging
                except SQLAlchemyError as e:
                    db.session.rollback()
                    bot_response = "Failed to register student due to database error."

            else:
                bot_response = "Sorry, I couldn't understand. Please provide valid information to register the student."

        elif intent == 'delete_student':
            # Extract entities like roll number and name
            rollno = entities.get('wit$number:rollno', [{}])[0].get('value')
            sname = entities.get('student_name:student_name', [{}])[0].get('value')

            # Check if either roll number or name is provided
            if rollno or sname:
                try:
                    # Query the database for the student based on roll number or name
                    condition = or_(Student.rollno == rollno, Student.sname == sname)
                    student = Student.query.filter(condition).first()
                    if student:
                        # If student exists, delete the entry from the database
                        db.session.delete(student)
                        db.session.commit()
                        bot_response = f"Student with roll number {rollno} and name {sname} has been deleted successfully."
                        # Insert log entry
                        insert_log('delete_student', user_message, bot_response)
                        db.session.commit()  # Commit after logging
                    else:
                        bot_response = f"No student found with provided roll number or name."
                except Exception as e:
                    # Handle any exceptions that might occur during the deletion process
                    print(f"An error occurred: {str(e)}")
                    bot_response = "Failed to delete the student due to an error."

            else:
                bot_response = "Please provide either roll number or name to delete the student."
        # Return a JSON response with the bot's response
        return jsonify({'response': bot_response})
    else:
        return jsonify({"response": "No message provided."})


# Route to log entries
@app.route('/logs')
def logs():
    # Retrieve all log entries from the database using a session query
    all_logs = db.session.query(Log).all()
    return render_template('logs.html', all_logs=all_logs)




@app.route('/forms', methods=['GET'])
def contact_submissions():
    
    # Query the database to retrieve all contact form submissions
    submissions = ContactSubmission.query.all()
    
    # Render the template with the submissions data
    return render_template('forms.html', submissions=submissions)


if __name__ == "__main__":
    app.run()
    
app.debug = True
#application = app






