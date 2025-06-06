# AI-Powered Interview System

## Business Use Case

The AI-Powered Interview System aims to streamline the initial technical screening process for software engineering candidates. It addresses several challenges faced by hiring teams:

*   **Time-Consuming Screening:** Manually reviewing resumes and conducting initial technical evaluations can be very time-intensive.
*   **Inconsistent Evaluation:** Human bias and varying interviewer standards can lead to inconsistent candidate assessments.
*   **Generating Relevant Questions:** Crafting coding questions that are appropriately challenging and relevant to a candidate's specific skills and experience level is difficult.
*   **Providing Detailed Feedback:** Giving candidates structured, actionable feedback on their coding submissions is often overlooked but highly valuable.

This system automates key parts of this process by:
1.  Analyzing resumes to extract key skills and years of experience.
2.  Dynamically generating relevant coding questions tailored to the candidate's profile using AI.
3.  Evaluating submitted code solutions using AI, providing a detailed breakdown of scores and qualitative feedback across multiple categories.
4.  Offering a user-friendly web interface for both recruiters/interviewers and candidates.

## Features

*   **Resume Analysis:** Supports `.pdf`, `.docx`, and `.txt` resume formats. Extracts skills and estimates years of experience.
*   **Dynamic Question Generation:** Leverages Google's Gemini API to create coding questions based on the extracted skills and experience.
*   **AI-Powered Code Evaluation:** Utilizes Gemini API to assess submitted code, providing:
    *   An overall summary.
    *   Scores (1-10) for: Problem Understanding, Problem Solving Approach, Code Structure & Readability, Syntax & Language Usage, and Test Coverage & Edge Cases.
    *   Detailed qualitative feedback for each scoring category.
*   **Interactive Web Interface:** Built with Streamlit for a guided, multi-step user experience (Resume Upload → Coding Challenge → Evaluation Feedback).
*   **Secure API Key Handling:** Uses a `.env` file for managing the Gemini API key.
*   **Automatic App Reload:** Streamlit app reloads on code changes for a smoother development experience.

## Folder Structure

```
.
├── agents/
│   ├── __init__.py
│   ├── code_evaluator.py
│   ├── manager_agent.py
│   ├── question_generator.py
│   └── resume_analyzer.py
├── .streamlit/
│   └── config.toml
├── .env               # Stores API keys (not committed to Git)
├── .gitignore
├── app.py             # Main Streamlit application
├── README.md          # This file
├── requirements.txt   # Python dependencies
└── utils.py           # Utility functions (e.g., Gemini API interaction)
```

## Core Logic

*   **`app.py`**: The main entry point for the Streamlit web application. It handles the UI, user interactions, and session state management. It calls the `ManagerAgent` to orchestrate the interview workflow.
*   **`agents/manager_agent.py`**: Acts as the central coordinator. It initializes and delegates tasks to the other specialized agents (`ResumeAnalyzer`, `QuestionGenerator`, `CodeEvaluator`).
*   **`agents/resume_analyzer.py`**: Responsible for parsing uploaded resume files (PDF, DOCX, TXT). It uses the Gemini API to extract relevant skills and estimate years of experience from the resume content.
*   **`agents/question_generator.py`**: Takes the extracted skills and experience from the `ResumeAnalyzer` and uses the Gemini API to generate a relevant coding question.
*   **`agents/code_evaluator.py`**: Receives the coding question and the candidate's code submission. It uses the Gemini API with a structured prompt to evaluate the code based on predefined criteria, returning detailed scores and qualitative feedback in a JSON format, which is then parsed and displayed as a Markdown table.
*   **`utils.py`**: Contains helper functions, most notably the `generate_text_from_gemini` function, which handles the actual communication with the Google Gemini API. It also includes logic for loading the API key from the `.env` file.
*   **`.streamlit/config.toml`**: Configures Streamlit server behavior, such as `runOnSave = true` for automatic app reloading during development.
*   **`.env`**: A file (not committed to version control) to store sensitive information like the `GEMINI_API_KEY`.
*   **`requirements.txt`**: Lists all Python dependencies required to run the project.

## Local Setup Instructions

1.  **Prerequisites:**
    *   Python 3.9 or higher.
    *   Access to Google's Gemini API and a valid API key.

2.  **Clone the Repository (Optional):**
    If you have the project files, navigate to the project's root directory. If not, clone it:
    ```bash
    git clone <repository_url>
    cd <project_directory_name>
    ```

3.  **Create and Activate a Virtual Environment:**
    It's highly recommended to use a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

4.  **Install Dependencies:**
    Install all required packages from `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Up Environment Variables:**
    Create a file named `.env` in the root directory of the project. Add your Gemini API key to this file:
    ```
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
    ```
    Replace `"YOUR_GEMINI_API_KEY_HERE"` with your actual API key.

6.  **Run the Application:**
    Once the setup is complete, run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
    The application should open in your default web browser.

## Usage

1.  **Upload Resume:**
    *   Navigate to the "Upload & Analyze Resume" tab.
    *   Click "Choose a resume file" and select a PDF, DOCX, or TXT file.
    *   The system will analyze the resume, extract skills, and generate a coding question.
    *   Extracted skills and the generated question will be displayed.
    *   Click "Next: Go to Coding Challenge ➡️".

2.  **Solve Coding Challenge:**
    *   The generated coding question will be displayed.
    *   Write your code solution in the provided text area.
    *   Click "Submit Code for Evaluation".

3.  **View Evaluation Feedback:**
    *   Your submitted code will be displayed.
    *   The AI-powered evaluation feedback, including scores and qualitative comments for different categories, will be shown in a table format.
    *   Click "Start Over with a New Resume 🔄" to begin a new interview session.

