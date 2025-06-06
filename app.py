import streamlit as st
from agents.manager_agent import ManagerAgent
from utils import GEMINI_API_KEY # For checking API key status
import io
from pygments import lexers
from pygments.util import ClassNotFound
from streamlit_ace import st_ace, LANGUAGES, THEMES, KEYBINDINGS

st.set_page_config(layout="wide", page_title="AI-Powered Interview System")

st.title("🤖 AI-Powered Interview System")
st.caption("Upload a resume to generate a tailored coding question and get AI-powered code evaluation.")

# --- Initialize ManagerAgent and other session states ---
if 'manager' not in st.session_state:
    st.session_state.manager = ManagerAgent()
    print("App.py: ManagerAgent initialized and stored in session state.")
if 'generated_question' not in st.session_state:
    st.session_state.generated_question = None
if 'extracted_skills' not in st.session_state:
    st.session_state.extracted_skills = None
if 'evaluation_feedback' not in st.session_state:
    st.session_state.evaluation_feedback = None
if 'submitted_code_display' not in st.session_state:
    st.session_state.submitted_code_display = None
if 'code_input_area_content' not in st.session_state: # Renamed for clarity
    st.session_state.code_input_area_content = "def solve():\n    # Your code here\n    pass"
if 'active_tab_index' not in st.session_state:
    st.session_state.active_tab_index = 0
if 'selected_difficulty' not in st.session_state:
    st.session_state.selected_difficulty = "Medium"  # Default difficulty
if 'detected_language' not in st.session_state:
    st.session_state.detected_language = "text" # Default language for st.code (will be less used now)
if 'selected_editor_language' not in st.session_state:
    st.session_state.selected_editor_language = "python"
if 'selected_editor_theme' not in st.session_state:
    st.session_state.selected_editor_theme = "tomorrow_night"
if 'selected_keybinding' not in st.session_state:
    st.session_state.selected_keybinding = "ace"

def clear_session_state_for_restart():
    """Clears session state variables to allow the user to start over."""
    st.session_state.active_tab_index = 0
    st.session_state.generated_question = None
    st.session_state.extracted_skills = None
    st.session_state.evaluation_feedback = None
    st.session_state.submitted_code_display = None
    st.session_state.code_input_area_content = "def solve():\n    # Your code here\n    pass"
    st.session_state.selected_difficulty = "Medium" # Reset difficulty
    st.session_state.detected_language = "text" # Reset detected language (less used now)
    st.session_state.selected_editor_language = "python"
    st.session_state.selected_editor_theme = "tomorrow_night"
    st.session_state.selected_keybinding = "ace"
    # The file uploader will reset itself if its key changes or a new file is uploaded.
    # Forcing a full clear might involve more complex handling of the uploader widget itself.
    print("App.py: Session state cleared for restart.")


# --- Workflow Progress Indicator ---
st.markdown("### Workflow Progress")
max_steps = 3  # Resume Analysis, Coding Challenge, Evaluation Feedback
progress_bar_value = 0

if st.session_state.get('generated_question'): 
    progress_bar_value = 1
if st.session_state.get('submitted_code_display'):
    progress_bar_value = 2
if st.session_state.get('evaluation_feedback'):
    progress_bar_value = 3

st.progress(progress_bar_value / max_steps)

# Captions based on active_tab_index and completion status
if st.session_state.active_tab_index == 0:
    if not st.session_state.get('generated_question'):
        st.caption("Step 1 of 3: Upload and analyze your resume.")
    else:
        st.caption("Step 1 of 3 Complete: Resume analyzed. Click 'Next' to proceed.")
elif st.session_state.active_tab_index == 1:
    if not st.session_state.get('submitted_code_display'):
        st.caption("Step 2 of 3: Solve the coding challenge.")
    else:
        st.caption("Step 2 of 3 Complete: Code submitted. Click 'Next' to view feedback.")
elif st.session_state.active_tab_index == 2:
    if not st.session_state.get('evaluation_feedback'):
        st.caption("Step 3 of 3: View evaluation feedback.")
    else:
        st.caption("Workflow complete! Evaluation feedback received.")

st.markdown("---    ")

# --- UI Sections based on active_tab_index ---

# Step 1: Resume Upload & Analysis
if st.session_state.active_tab_index == 0:
    st.header("📄 Resume Upload & Analysis")
    uploaded_file = st.file_uploader(
        "Choose a resume file (PDF, DOCX, TXT)",
        type=["pdf", "docx", "txt"],
        key="resume_uploader_flow", # Changed key to avoid conflict if old one persists
        on_change=lambda: [
            setattr(st.session_state, 'generated_question', None),
            setattr(st.session_state, 'extracted_skills', None),
            setattr(st.session_state, 'evaluation_feedback', None),
            setattr(st.session_state, 'submitted_code_display', None),
            setattr(st.session_state, 'code_input_area_content', "def solve():\n    # Your code here\n    pass"),
            setattr(st.session_state, 'active_tab_index', 0) # Reset to step 1
        ]
    )

    st.session_state.selected_difficulty = st.radio(
        "Select Question Difficulty:",
        ("Easy", "Medium", "Hard"),
        index=["Easy", "Medium", "Hard"].index(st.session_state.selected_difficulty), # Persist selection
        horizontal=True,
        key="difficulty_selector"
    )

    if uploaded_file is not None:
        # Process resume only if skills/question haven't been extracted for this upload yet
        if st.session_state.get('extracted_skills') is None and st.session_state.get('generated_question') is None:
            st.success(f"Uploaded: {uploaded_file.name}")
            st.toast(f"Analyzing resume and generating {st.session_state.selected_difficulty} question...", icon="⏳")
            with st.spinner(f"Analyzing resume and generating {st.session_state.selected_difficulty} question..."):
                resume_bytes = uploaded_file.getvalue()
                skills, question = st.session_state.manager.process_resume_and_generate_question(
                    resume_bytes,
                    file_name=uploaded_file.name,
                    difficulty=st.session_state.selected_difficulty
                )
                st.session_state.extracted_skills = skills
                st.session_state.generated_question = question

                if skills and question:
                    st.toast("Resume processed and question generated!", icon="✅")
                elif skills:
                    st.toast("Skills extracted, but question generation failed.", icon="⚠️")
                else:
                    st.toast("Failed to process resume and generate question.", icon="❌")
    
    if st.session_state.get('extracted_skills'):
        st.subheader("🔍 Extracted Skills:")
        skills_display = st.session_state.extracted_skills
        if isinstance(skills_display, list):
            skills_display = ", ".join(skills_display)
        st.write(skills_display)
    else:
        st.info("Extracted skills will appear here after resume analysis.")

    if st.session_state.get('extracted_skills') and st.session_state.get('generated_question'):
        if st.button("Next: Go to Coding Challenge ➡️", key="next_to_coding_challenge"):
            st.session_state.active_tab_index = 1
            st.rerun()

# Step 2: Coding Challenge
elif st.session_state.active_tab_index == 1:
    st.header("💻 Coding Challenge")
    if st.session_state.get('generated_question'):
        st.info(f"**Question:** {st.session_state.generated_question}")
        
        st.subheader("Code Editor Settings")
        editor_cols = st.columns(3)
        with editor_cols[0]:
            st.session_state.selected_editor_language = st.selectbox(
                "Language", 
                options=LANGUAGES, 
                index=LANGUAGES.index(st.session_state.selected_editor_language) if st.session_state.selected_editor_language in LANGUAGES else LANGUAGES.index('python'),
                key="editor_language_select"
            )
        with editor_cols[1]:
            st.session_state.selected_editor_theme = st.selectbox(
                "Theme", 
                options=THEMES, 
                index=THEMES.index(st.session_state.selected_editor_theme) if st.session_state.selected_editor_theme in THEMES else THEMES.index('tomorrow_night'),
                key="editor_theme_select"
            )
        with editor_cols[2]:
            st.session_state.selected_keybinding = st.selectbox(
                "Keybinding", 
                options=KEYBINDINGS, 
                index=(KEYBINDINGS.index(st.session_state.selected_keybinding) if st.session_state.selected_keybinding in KEYBINDINGS else 0),
                key="editor_keybinding_select"
            )

        st.subheader("Enter your code solution here:")
        code_input = st_ace(
            value=st.session_state.code_input_area_content,
            language=st.session_state.selected_editor_language,
            theme=st.session_state.selected_editor_theme,
            keybinding=st.session_state.selected_keybinding,
            font_size=14,
            tab_size=4,
            show_gutter=True,
            wrap=True,
            auto_update=False, # Update on blur
            min_lines=20, # Adjust for desired height
            key="ace_editor_main"
        )
        # Update session state if code_input is not None (st_ace returns None initially sometimes)
        if code_input is not None:
            st.session_state.code_input_area_content = code_input
        
        code_input_placeholder = "def solve():\n    # Your code here\n    pass" # Keep for logic below if needed

        col1, col2 = st.columns([1,1]) # Adjust ratio as needed
        with col1:
            if st.button("⬅️ Previous: Resume Upload", key="prev_to_resume_upload"):
                st.session_state.active_tab_index = 0
                st.rerun()
        with col2:
            if st.button("Submit Code for Evaluation 🚀", key="submit_code_flow"):
                if code_input and code_input.strip() and code_input != code_input_placeholder:
                    st.session_state.submitted_code_display = code_input
                    st.session_state.evaluation_feedback = None # Clear old feedback

                    # Use the language selected in the Ace editor for evaluation
                    evaluation_language = st.session_state.selected_editor_language
                    print(f"App.py: Evaluating code as {evaluation_language}")

                    st.toast(f"Evaluating your {evaluation_language} code...", icon="⏳")
                    with st.spinner(f"Evaluating your {evaluation_language} code..."):
                        feedback = st.session_state.manager.evaluate_code_submission(
                            st.session_state.generated_question,
                            st.session_state.code_input_area_content, # Use the content from session state
                            language=evaluation_language
                        )
                        st.session_state.evaluation_feedback = feedback
                        if feedback:
                            st.toast("Evaluation complete!", icon="✅") # Simpler toast
                        else:
                            st.toast("Failed to get evaluation feedback.", icon="❌")
                else:
                    st.error("Please enter your code solution before submitting.")
        
        if st.session_state.get('submitted_code_display'):
            st.subheader("Your Submitted Code:")
            st.code(st.session_state.submitted_code_display, language=st.session_state.selected_editor_language)

        if st.session_state.get('evaluation_feedback'): # Show 'Next' only after feedback is available
            if st.button("Next: View Evaluation Feedback ➡️", key="next_to_feedback"):
                st.session_state.active_tab_index = 2
                st.rerun()
    else:
        # This case should ideally not be reachable if navigation is controlled
        st.warning("No coding question generated. Please go back to Step 1 and upload a resume.")
        if st.button("Back to Resume Upload", key="back_to_resume_upload_from_coding"):
            st.session_state.active_tab_index = 0
            st.rerun()

# Step 3: Evaluation Feedback
elif st.session_state.active_tab_index == 2:
    st.header("🧐 Evaluation Feedback")

    col1, col2 = st.columns([1,1]) # Adjust ratio as needed
    with col1:
        if st.button("⬅️ Previous: Coding Challenge", key="prev_to_coding_challenge_from_feedback"):
            st.session_state.active_tab_index = 1
            st.rerun()
    with col2:
        if st.button("🔄 Start Over with New Resume", key="start_over_flow_v2"):
            clear_session_state_for_restart()
            st.rerun()

    st.markdown("---") # Visual separator

    if st.session_state.get('evaluation_feedback'):
        st.subheader("Evaluation Feedback:")
        st.markdown(st.session_state.evaluation_feedback)
    else:
        # This case implies user navigated here before feedback was ready, or it failed
        st.info("Evaluation feedback will appear here once available.")
        if st.session_state.get('submitted_code_display') and not st.session_state.get('evaluation_feedback'):
            st.warning("Evaluation might still be in progress or failed. If it takes too long, you might need to resubmit.")


st.markdown("---    ")
st.sidebar.header("Settings & Info")
if not GEMINI_API_KEY:
    st.sidebar.error("GEMINI_API_KEY not found in Streamlit secrets. Please add it to .streamlit/secrets.toml.")
    st.sidebar.markdown(
        "Get your Gemini API Key from [Google AI Studio](https://aistudio.google.com/app/apikey).")
else:
    st.sidebar.success("Gemini API Key is configured (check console for actual load status).")

st.sidebar.markdown("---    ")
st.sidebar.info(
    "This is a demo of an AI-Powered Interview System using Google ADK and Gemini. "
    "All agent responses are currently mocked/placeholders."
)
st.sidebar.markdown("**Workflow:** User → Streamlit UI → Manager Agent → Resume Analyzer → Question Generator → Code Evaluator → Feedback.")


# To run this app:
# 1. Ensure GEMINI_API_KEY is set in your environment (though current logic is mocked).
# 2. Install dependencies: pip install -r requirements.txt
# 3. Navigate to this directory in your terminal.
# 4. Run: streamlit run app.py
