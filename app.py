from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re

from flask import Flask, request, jsonify
from typing_extensions import override
from openai import AssistantEventHandler
from openai import OpenAI

OPENAI_API_KEY = "YOUR API KEY"
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'pdf'}


app.config['UPLOAD_FOLDER'] = "uploads"

def allowed_file(filename):
    
    return '.' in filename and filename.split('.')[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PyPDF2.PdfFileReader(pdf_file)
    for page_num in range(pdf_reader.numPages):
        text += pdf_reader.getPage(page_num).extractText()
    return text


def create_query(resume_file,job_descript_text):
    
    # Create prompt from prompt file. 

    with open("prompt.txt") as f:
        prompt = str(f.read().splitlines()[0])
    
    prompt = prompt + resume_file
    prompt = prompt + " this is the job description:"
    prompt = prompt + job_descript_text
    return prompt    


def process_pdf(uploaded_file):

    if uploaded_file.filename == '':
        return redirect(request.url)
    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    text = extract_text_from_pdf(uploaded_file)
    return text


def generate_resonse(query):


    stream = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': query}
        ],
        temperature=0,
    )

    text = stream.choices[0].message.content.strip()
    score, name, job_descript, summary = text.splitlines()
    return score.split('%')[0],name, job_descript, summary


@app.route('/')
def index():
    return render_template('index.html')

def get_competative_score(score,compiled_results_file):

    # Percential formula: P = (n/N)*100  
    # Where P is the percentile, n is the number of data points below the data point, and N is the total number of data points.
    
    with open(compiled_results_file, "r") as fp:
        results = fp.readlines()
    
    n = 0 
    N = len(results)
    
    for line in results: 
        other_score = float(line.split(" ")[2])

        if score>=other_score: 
            n=n+1
    print(n,'nmber of people we did better than')
    P = round((n/N)*100,0)
    print(N,'NUMBER')
    if len(results)==0:
        message = "This is the first applicant for this job."

    else:
        message = " Resume is in "+str(P)+"% percntial of other the other " +str(N)+ " applicants"

    return message


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():

    
    if request.method == 'POST':
        # check if the post request has the file part

        resume_file = request.files['resume']
        job_descript_file = request.files['job_descript']

        resume_text = process_pdf(resume_file)
        job_descript_text = process_pdf(job_descript_file)
        
        query = create_query(resume_text,job_descript_text)
 

        score,name, job_title, summary  = generate_resonse(query)
        compiled_results_file = job_title+'.txt'

        comp_score = get_competative_score(float(score),compiled_results_file)
        # Add Score to results file
        with open(compiled_results_file, "a") as fp:
            fp.write(name+" "+score+"\n")        

    return render_template('results.html', name = name, score=score, summary=summary,comp_score=comp_score,)             


if __name__ == '__main__':
    app.run(debug=True)