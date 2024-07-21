# PDF Chatbot

PDF Chatbot is a web application that allows users to upload PDF files, ask questions about the content of the PDFs, and get answers. The application uses OpenAI's API to process and respond to user queries.

## Features

- User authentication (Sign Up, Login, Logout)
- Upload PDF files
- Ask questions about the content of uploaded PDFs
- View chat history with the uploaded PDF's filename
- Responsive design with Bootstrap

## Installation

### Prerequisites

- Python 3.7 or higher
- OpenAI API key

### Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/yourusername/pdf-chatbot.git
    cd pdf-chatbot
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install the required packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    Create a `.env` file in the project root directory and add your OpenAI API key:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    ```

5. **Run the Flask application**:
    ```bash
    flask run
    ```

6. **Open the application in your browser**:
    Go to `http://127.0.0.1:5000/`.

   ### Important Files

- `app/__init__.py`: Initializes the Flask application and sets up the database.
- `app/routes.py`: Defines the routes for the application, including user authentication and PDF processing.
- `app/models.py`: Defines the database models for users and chat history.
- `app/static/style.css`: Contains the custom CSS for the application.
- `app/templates/`: Contains the HTML templates for the application.
- `requirements.txt`: Lists the Python packages required for the project.
- `run.py`: The main entry point to run the Flask application.

## Usage

### User Authentication

- **Sign Up**: Users can create a new account by providing an email, username, and password.
- **Login**: Users can log in using their email and password.
- **Logout**: Users can log out from their account.

### PDF Chatbot

- **Upload PDF**: Users can upload a PDF file.
- **Ask Questions**: Users can ask questions related to the uploaded PDF.
- **View Chat History**: Users can view their chat history with the filename of the PDF.

### Dependencies

- Flask: A lightweight WSGI web application framework.
- Flask-SQLAlchemy: Adds SQLAlchemy support to Flask applications.
- Flask-Login: Provides user session management for Flask.
- OpenAI: Provides the API for generating answers.
- PyMuPDF: A lightweight PDF and XPS viewer.

Install all dependencies using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### Acknowledgments
- Thanks to OpenAI for providing the API for generating answers.
- Thanks to Flask for the web framework.
- Thanks to Bootstrap for the responsive design framework.
