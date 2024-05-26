from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from fpdf import Align, XPos, YPos
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
    query = db.udb.insert_one({"Question": f"{ques}", "Marks": int(mrk)})
    img_name = str(db.udb.find_one({"Question": f"{ques}", "Marks": int(mrk)})["_id"])
    if request.form.getlist('match') and request.form.getlist('match')[0] == 'on':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No image selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(img_name+".png")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #print('upload_image filename: ' + filename)
            flash('Question successfully uploaded')
            flash('Image successfully uploaded and displayed below')
            return render_template('addNewQues.html', filename=filename)
        else:
            flash('Allowed image types are - png, jpg, jpeg')
            return redirect(request.url)
    else:
        flash('Question successfully uploaded')
        return render_template('addNewQues.html')


pics = []
with os.scandir('./static/uploads') as it:
    for entry in it:
        pics.append(entry.name)

images_NoExt = [os.path.splitext(f)[0] for f in os.listdir('./static/uploads') if os.path.isfile(os.path.join('./static/uploads', f)) and f.lower().endswith(('png', 'jpg', 'jpeg', 'gif'))]


@app.route('/display/<filename>')
def display_image(filename):
    #print('display_image filename: ' + filename)
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


query2 = list(db.udb.find({'Marks': 2}))

query4 = list(db.udb.find({'Marks': 4}))

query10 = list(db.udb.find({'Marks': 10}))


@app.route('/make')
def make_html():
    return render_template('make.html', entries=query2, entries2=query4, entries3=query10, images=pics, images2=images_NoExt)


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
    pdf.set_font("Times", "B", size=14)

    with pdf.table() as table:
        row = table.row()
        row.cell(img='static/adamas.png')
        row.cell("ADAMAS UNIVERSITY END-SEMESTER EXAMINATION : JUNE 2024 ", colspan=3, align="C")

        pdf.set_font("Times", "B", size=12)

        row = table.row()
        row.cell("Name of the Program:", align="C")
        row.cell("B. Tech CSE, CSE(AI&ML), CSE(CSF)", align="C")
        row.cell("Semester:", align="C")
        row.cell("VI", align="C")

        row = table.row()
        row.cell("Paper Title :", align="C")
        row.cell("Unstructured Database", align="C")
        row.cell("Paper Code:", align="C")
        row.cell("CSE12002", align="C")

        row = table.row()
        row.cell("Maximum Marks:", align="C")
        row.cell("50", align="C")
        row.cell("Time Duration:", align="C")
        row.cell("3HR", align="C")

        row = table.row()
        row.cell("Total No of questions:", align="C")
        row.cell("12", align="C")
        row.cell("Total No of Pages:", align="C")
        row.cell("2", align="C")

        row = table.row()
        pdf.set_font("Times", "I", size=10)
        row.cell("(Any other information for the student may be mentioned here)", align="L")
        pdf.set_font("Times", "", size=10)
        row.cell(
            "1. At top sheet, clearly mention Name, Univ. Roll No., Enrolment No., Paper Name & Code, Date of Exam.\n "
            "2. All parts of a Question should be answered consecutively. Each Answer should start from a fresh "
            "page.\n 3. Assumptions made if any, should be stated clearly at the beginning of your answer.",
            colspan=3, align="L")

    pdf.set_font("Times", size=20)

    pdf.cell(200, 15, "Answer all the Groups", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Times", 'i', size=17)
    pdf.cell(200, 15, "Generated using an automated paper generation system", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Times", 'i', size=14)
    pdf.cell(200, 10, "A project created by Dipanjan Laha", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.set_font("Times", size=13)
    pdf.cell(200, 15, "Answer all the Groups", align="c", new_x=XPos.LMARGIN, new_y=YPos.NEXT,)
    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(200, 15, "Group A", align="c", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=13)
    pdf.cell(184, 15, "Answer all the following Questions", align="c")
    pdf.cell(50, 15, "2x5 = 10", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")

    pdf.set_font("Times", size=12)
    for i in range(5):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list1[marks2[i]-1]["Question"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")
        if str(list1[marks2[i]-1]["_id"]) in images_NoExt:
            pdf.image((os.path.join(app.config['UPLOAD_FOLDER'], str(list1[marks2[i]-1]["_id"])))+".png", Align.C, w=50, h=20)

    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(184, 15, "Group B", align="c", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=13)
    pdf.cell(184, 15, "Answer all the following Questions", align="c")
    pdf.cell(50, 15, "4x5 = 20", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")

    pdf.set_font("Times", size=12)
    for i in range(5):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list2[marks4[i]-1]["Question"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")
        if str(list2[marks4[i]-1]["_id"]) in images_NoExt:
            pdf.image((os.path.join(app.config['UPLOAD_FOLDER'], str(list2[marks4[i]-1]["_id"])))+".png", Align.C, w=50, h=20)

    pdf.set_font("Arial", 'b', size=16)
    pdf.cell(184, 15, "Group C", align="c", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("Times", size=13)
    pdf.cell(184, 15, "Answer all the following Questions", align="c")
    pdf.cell(50, 15, "10x2 = 20", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")

    pdf.set_font("Times", size=12)
    for i in range(2):
        pdf.cell(170, 6, "Q"+str(i+1)+": "+list3[marks10[i]-1]["Question"], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="l")
        if str(list3[marks10[i]-1]["_id"]) in images_NoExt:
            pdf.image((os.path.join(app.config['UPLOAD_FOLDER'], str(list3[marks10[i]-1]["_id"])))+".png", Align.C, w=50, h=20)

    pdf.output("file.pdf")


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
