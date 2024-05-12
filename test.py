from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from pymongo import MongoClient
import os
import fpdf
from werkzeug.utils import secure_filename


pdf = fpdf.FPDF(format='letter')

client = MongoClient("mongodb://localhost:27017")
db = client["Project"]
collection = db["flaskApp"]

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def index():  # application code
    return render_template("login.html")


@app.route('/index.html')
def index_page():
    return render_template("index.html")


@app.route("/submit", methods=["GET", "POST"])
def submit():
    Name = request.form["Name"]
    Registration = request.form["Registration Number"]
    roll = request.form["Roll Number"]
    username = request.form["Username"]
    password = request.form["Password"]
    collection.insert_one({"Name": Name, "Registration Number": Registration, "Roll Number": roll, "Username": username,
                           "Password": password})
    data = collection.find()
    return render_template("dashboard.html", data=data)


@app.route("/submitLogin", methods=["GET", "POST"])
def submit_login():
    username = request.form["email"]
    password = request.form["password"]
    if collection.find_one({"Username": username}) and collection.find_one({"Password": password}):
        return render_template("welcome.html")
    else:
        flash('No user found')
        return render_template("login.html")


@app.route('/add_ques', methods=['POST'])
def upload_image():
    ques = request.form["question"]
    mrk = request.form["marks"]
    print(ques, mrk)
    query = db.udb.insert_one({"Question": f"{ques}", "Marks": int(mrk)})
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        #print('upload_image filename: ' + filename)
        flash('Image successfully uploaded and displayed below')
        return render_template('addNewQues.html', filename=filename)
    else:
        flash('Allowed image types are - png, jpg, jpeg')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


query2 = list(db.udb.find({'Marks': 2}))

query4 = list(db.udb.find({'Marks': 4}))

query10 = list(db.udb.find({'Marks': 10}))


@app.route('/make')
def make_html():
    return render_template("make.html", entries=query2, entries2=query4, entries3=query10)


@app.route('/addNew')
def add_new_qes():
    return render_template("addNewQues.html")


@app.route('/Generate_pdf', methods=['GET', 'POST'])
def pdf_gen():
    if request.method == 'POST':
        # Retrieve user input from the form
        marks2 = [int(i) for i in (request.form.get('2marks')).split()]
        marks4 = [int(i) for i in (request.form.get('4marks')).split()]
        marks10 = [int(i) for i in (request.form.get('10marks')).split()]
        print(marks2, marks4, marks10)
        if marks2 and marks4 and marks10:
            generate_pdf_file(query2, query4, query10, marks2, marks10, marks4)
            pdf_file = "./file.pdf"
    return send_file(pdf_file, as_attachment=True, download_name='question.pdf')


def generate_pdf_file(list1, list2, list3, marks2, marks10, marks4):
    pdf.add_page()
    pdf.set_font("Times", size=20)

    pdf.cell(200, 15, "Unstructured Database Exam 2024", ln=1, align="C")
    pdf.set_font("Times", 'i', size=17)
    pdf.cell(200, 15, "Generated using an automated paper generation system", ln=1, align="C")
    pdf.set_font("Times", 'i', size=14)
    pdf.cell(200, 10, "A project created by Dipanjan Laha", ln=1, align="C")
    pdf.set_font("Times", size=13)
    pdf.cell(167, 15, "Max Marks : 50", align="l")
    pdf.cell(100, 15, "Time : 3 Hours", ln=1, align="r")
    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(134, 15, "Section A", align="l")
    pdf.set_font("Times", 'i', size=13)
    pdf.cell(100, 15, "Max marks for this section are 2", ln=1, align="l")

    pdf.set_font("Times", size=12)
    for i in range(5):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list1[marks2[i]-1]["Question"], ln=1, align="l")

    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(134, 15, "Section B", align="l")
    pdf.set_font("Times", 'i', size=13)
    pdf.cell(100, 15, "Max marks for this section are 4", ln=1, align="l")

    pdf.set_font("Times", size=12)
    for i in range(5):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list2[marks4[i]-1]["Question"], ln=1, align="l")

    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(133, 15, "Section C", align="l")
    pdf.set_font("Times", 'i', size=13)
    pdf.cell(100, 15, "Max marks for this section are 10", ln=1, align="l")

    pdf.set_font("Times", size=12)
    for i in range(2):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list3[marks10[i]-1]["Question"], ln=1, align="l")

    pdf.output("file.pdf")


if __name__ == '__main__':
    app.run(host="0.0.0.0")