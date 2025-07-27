# Altura-Med-AI
ALTURA: An AI-powered medical awareness chatbot (AI Spark project for Innovista). Badass Ai That Will Chnage The Medical Field 
# ALTURA - Medical AI Companion

An AI-powered chatbot designed to provide medical *awareness* based on user-input symptoms. This project was developed for the AI Spark program at [Your College Name - maybe Innovista?].

## What It Does

ALTURA helps users understand potential causes for their symptoms (like a cough or headache) and offers general advice. It's important to remember that ALTURA **does not diagnose** conditions. It aims to guide users on when they might want to consult a real doctor.

ALTURA can respond in two modes:
*   **Doctor Mode:** Provides information in a more formal, medical style.
*   **Friend Mode:** Offers a casual, supportive tone.

## How to Run the Project

### Prerequisites

*   **Python 3.x** installed on your computer.
*   An LLM server running locally (like Ollama, LM Studio, or llama.cpp) with a model loaded (e.g., Mistral). This project expects the LLM API to be accessible, typically at `http://localhost:11434` (Ollama default) or `http://localhost:1234`.
*   The necessary Python libraries installed. You can usually do this by running `pip install -r requirements.txt` in your project terminal (if you have a `requirements.txt` file listing Flask, etc.).

### Backend (Flask Server)

1.  Open your terminal or command prompt.
2.  Navigate to the folder containing `app.py` (e.g., `cd path/to/your/project/folder`).
3.  Run the command: `python app.py`
4.  The backend server should start, usually on `http://127.0.0.1:5000`. You'll see confirmation messages in the terminal.

### Frontend (User Interface)

1.  Make sure the backend server (step above) is running.
2.  Make sure your local LLM server (Ollama/LM Studio/etc.) is running and has a model loaded.
3.  Open the `index.html` file in your web browser.
    *   (Alternatively, if you used Live Server in VS Code, you can use that to open `index.html`).
4.  The ALTURA interface should load in your browser.

### Configuration

*   Check the `.env` file (if present) or the `app.py` file itself for the LLM server address and port. Make sure these match where your LLM is actually running (e.g., `LLM_HOST=localhost`, `LLM_PORT=11434`).

## Files in this Repository

*   `app.py`: The main Python Flask application (backend).
*   `index.html`: The main web page containing the user interface (frontend).
*   `altura-logo.png`: The ALTURA logo image (make sure it's in the same folder as `index.html`).
*   `requirements.txt`: (Optional but helpful) Lists the Python packages needed (e.g., Flask).
*   `.env`: (Optional) Stores configuration variables like LLM host/port.
*   `README.md`: This file.

## Notes

*   This project uses a locally running Large Language Model (LLM) for generating responses.
*   It's designed for educational purposes and symptom *awareness* only.
*   Always consult a qualified healthcare professional for medical advice and diagnosis.
