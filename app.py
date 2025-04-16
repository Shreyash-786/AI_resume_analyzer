import os
import time
from flask import Flask, request, render_template
import PyPDF2

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Predefined skill set
skill_set = [
    "Python", "Django", "Flask", "SQL", "AWS", "Git", "REST", "APIs",
    "JavaScript", "Docker", "Programming language", "C", "C++", "Core Java",
    "penetration testing", "C Programming", "C++ Programming", "Python Basics"
]

# Extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

# Extract skills from text based on a given skill list
def extract_skills(text, skill_list):
    text = text.lower()
    return [skill for skill in skill_list if skill.lower() in text]

@app.route('/', methods=['GET', 'POST'])
def index():
    matched_resume_skills = []
    job_related_skills = []
    score = 0
    no_skills_found = False

    if request.method == 'POST':
        job_desc = request.form['job_description']
        file = request.files['resume']

        if file and file.filename != '':
            # Save file with unique name
            timestamp = str(int(time.time()))
            file_ext = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{timestamp}.{file_ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Step 1: Extract job-related skills
            job_related_skills = extract_skills(job_desc, skill_set)

            if not job_related_skills:
                no_skills_found = True
            else:
                # Step 2: Extract resume text
                if file_ext == 'pdf':
                    resume_text = extract_text_from_pdf(file_path)
                elif file_ext == 'txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        resume_text = f.read()
                else:
                    resume_text = ""

                # Step 3: Match resume skills with job-related skills
                matched_resume_skills = extract_skills(resume_text, job_related_skills)
                score = round(len(matched_resume_skills) / len(job_related_skills) * 100, 2)

            return render_template('index.html',
                                   job_skills=job_related_skills,
                                   skills=matched_resume_skills,
                                   score=score,
                                   submitted=True,
                                   no_skills_found=no_skills_found)

    return render_template('index.html', submitted=False)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
