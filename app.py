from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import os
import openai
import fitz  # PyMuPDF
import numpy as np
from numpy.linalg import norm
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_default_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize the database and session
db = SQLAlchemy(app)
Session(app)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    # Add relationship to ChatHistory
    chats = db.relationship('ChatHistory', backref='user', lazy=True)

# Define the ChatHistory model with an additional field for the PDF filename
class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.String(1000), nullable=False)
    pdf_filename = db.Column(db.String(200), nullable=False)  # New field for the PDF filename

# Create the database
with app.app_context():
    db.create_all()

# Define the route for the landing page
@app.route('/')
def landing():
    return render_template('landing.html')

# Define the route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('pdf_chatbot'))
        else:
            flash('Login failed. Check your email and/or password.', 'danger')
    
    return render_template('login.html')

# Define the route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        
        if User.query.filter_by(email=email).first():
            flash('Email address already exists.', 'danger')
        else:
            new_user = User(email=email, username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
    
    return render_template('signup.html')

# Define the route for the PDF chatbot page
@app.route('/pdf_chatbot', methods=['GET', 'POST'])
def pdf_chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    username = session.get('username')
    answer = None
    pdf_filename = None

    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename.endswith('.pdf'):
                pdf_filename = file.filename
                file_path = os.path.join('uploads', pdf_filename)
                file.save(file_path)
                session['file_path'] = file_path
                session['pdf_filename'] = pdf_filename

        if 'question' in request.form:
            question = request.form['question']
            if session.get('file_path'):
                answer = extract(pdf_path=session['file_path'], users_question=question)
                
                new_chat = ChatHistory(user_id=session['user_id'], question=question, answer=answer, pdf_filename=session.get('pdf_filename', ''))
                db.session.add(new_chat)
                db.session.commit()

    user_chats = ChatHistory.query.filter_by(user_id=session['user_id']).all()

    return render_template('pdf_chatbot.html', answer=answer, username=username, history=user_chats)

# Define the route for logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('file_path', None)
    session.pop('pdf_filename', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))

def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return openai.Embedding.create(input=[text], model=model)['data'][0]['embedding']

def extract(pdf_path, users_question):
    document = fitz.open(pdf_path)
    text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        text += page.get_text()

    article_text = text

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,
        chunk_overlap=20,
        length_function=len,
    )

    texts = text_splitter.create_documents([article_text])

    text_chunks = [text.page_content for text in texts]

    df = pd.DataFrame({'text_chunks': text_chunks})

    df['ada_embedding'] = df.text_chunks.apply(lambda x: get_embedding(x, model='text-embedding-ada-002'))

    question_embedding = get_embedding(text=users_question, model="text-embedding-ada-002")

    cos_sim = []
    for index, row in df.iterrows():
        A = row.ada_embedding
        B = question_embedding
        cosine = np.dot(A, B) / (norm(A) * norm(B))
        cos_sim.append(cosine)

    df["cos_sim"] = cos_sim
    df = df.sort_values(by=["cos_sim"], ascending=False)

    context = " ".join(df.iloc[0:20]['text_chunks'].tolist())

    template = """
    You are a chat bot who loves to help people! Given the following context sections, answer the
    question using only the given context. If you are unsure and the answer is not
    explicitly written in the documentation, say "Sorry, I don't know how to help with that."

    Context sections:
    {context}

    Question:
    {users_question}

    Answer:
    """

    filled_template = template.format(context=context, users_question=users_question)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": filled_template}
        ],
        max_tokens=150,
        temperature=0.7,
    )

    return response.choices[0]['message']['content'].strip()

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
