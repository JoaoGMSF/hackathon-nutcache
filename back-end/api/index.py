import os
from flask import Flask, flash, request, redirect
from werkzeug.utils import secure_filename
import PyPDF2
import re
import string
import sklearn
import joblib
import pandas as pd
import json
from pandas import json_normalize

UPLOAD_FOLDER = ('api/uploads')
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

turnover_model = joblib.load('model/turnover_model.save')

def read_keywords():
    file_path = 'api/keywords.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        keywords = json.load(f)
    f.close()

def save_user_turnover(username, df):
    output = turnover_model.predict_proba(df)

    file_path = 'api/user_data/' + username + '.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        person_json = json.load(f)
    f.close()

    turnover = {"turnover": [i[1] for i in output][0]}
    person_json.update(turnover)

    with open(file_path, 'w') as f:
        json.dump(person_json, f)
    f.close()

def load_json_into_df(username):
    file_path = 'api/jsons/' + username + '.json'

    with open(file_path, 'r', encoding='utf-8') as f:
        person_json = json.load(f)
    f.close()

    df = json_normalize(person_json)
    df.drop('name', inplace=True, axis=1)
    df.drop('event', inplace=True, axis=1)
    return df

def saving_user_json(username, data):
    user_data = json.dumps(data, indent=4)
    file_path = 'api/jsons/' + username + '.json'

    f = open(file_path, "w")
    f.write(user_data)
    f.close()

def write_text(filename, text):
    filename = filename.replace('.pdf', '')
    file_path = 'api/converted_pdfs/' + filename + '.txt'
    
    f = open(file_path, "w")
    f.write(text)
    f.close()

def cleaning_text(text):
    text = text.lower()
    text = re.sub(r'\d+','',text)
    text = text.translate(str.maketrans('','',string.punctuation))
    return text

def read_pdf(filename):
    filePath = 'api/uploads/' + filename
    pdf_file_obj = open(filePath, 'rb')
    pdf_reader = PyPDF2.PdfFileReader(pdf_file_obj)
    num_pages = pdf_reader.numPages

    count = 0
    text = ""

    while count < num_pages:
        page_obj = pdf_reader.getPage(count)
        count +=1
        text += page_obj.extractText()

    text = cleaning_text(text)
    write_text(filename, text)
    return text

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            read_pdf(filename)
            return "File saved"
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''

@app.route('/post_user_info', methods=['POST'])
def post_user_info():
    user_json = request.json
    user_json = json.dumps(user_json, default=str)
    
    temp_df = pd.read_json(user_json, lines=True)
    username = temp_df['name'].values[0]
    print(username)

    saving_user_json(username, user_json)
    df = load_json_into_df(username)
    save_user_turnover(username, df)
    return user_json, 201

@app.route('/get_user_info', methods=['GET'])
def get_user_info():
    args = request.args
    username = args.get("name")

    file_path = 'api/user_data/' + username + '.json'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        person_json = json.load(f)
    f.close()
    return person_json, 200