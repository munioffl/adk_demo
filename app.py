import streamlit as st
from agents.manager_agent import ManagerAgent
from utils import GEMINI_API_KEY # For checking API key status
import io

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

    if uploaded_file is not None:
        # Process resume only if skills/question haven't been extracted for this upload yet
        if st.session_state.get('extracted_skills') is None and st.session_state.get('generated_question') is None:
            st.success(f"Uploaded: {uploaded_file.name}")
            st.toast("Analyzing resume and generating question...", icon="⏳")
            with st.spinner("Analyzing resume and generating question..."):
                resume_bytes = uploaded_file.getvalue()
                skills, question = st.session_state.manager.process_resume_and_generate_question(resume_bytes, file_name=uploaded_file.name)
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
        
        code_input_placeholder = "def solve():\n    # Your code here\n    pass"
        # Use the renamed session state key for code input
        code_input = st.text_area(
            "Enter your code solution here:",
            value=st.session_state.code_input_area_content,
            height=300,
            key="code_input_area_widget_flow" # Changed key
        )
        st.session_state.code_input_area_content = code_input # Update session state as user types

        if st.button("Submit Code for Evaluation", key="submit_code_flow"):
            if code_input and code_input.strip() and code_input != code_input_placeholder:
                st.session_state.submitted_code_display = code_input
                st.session_state.evaluation_feedback = None # Clear old feedback
                
                st.toast("Evaluating your code...", icon="⏳")
                with st.spinner("Evaluating your code..."):
                    feedback = st.session_state.manager.evaluate_code_submission(
                        st.session_state.generated_question,
                        code_input
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
            st.code(st.session_state.submitted_code_display, language='python')

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
    if st.session_state.get('evaluation_feedback'):
        st.subheader("Evaluation Feedback:")
        st.markdown(st.session_state.evaluation_feedback)
    else:
        # This case implies user navigated here before feedback was ready, or it failed
        st.info("Evaluation feedback will appear here once available.")
        if st.session_state.get('submitted_code_display') and not st.session_state.get('evaluation_feedback'):
            st.warning("Evaluation might still be in progress or failed. If it takes too long, you might need to resubmit.")
    
    if st.button("Start Over with a New Resume 🔄", key="start_over_flow"):
        # Reset all relevant session state variables
        st.session_state.active_tab_index = 0
        st.session_state.generated_question = None
        st.session_state.extracted_skills = None
        st.session_state.evaluation_feedback = None
        st.session_state.submitted_code_display = None
        st.session_state.code_input_area_content = "def solve():\n    # Your code here\n    pass"
        # Clearing the file uploader: its on_change will handle full reset if a new file is uploaded.
        # For explicit reset, changing its key or st.rerun() is enough here.
        st.rerun()

st.markdown("---    ")
st.sidebar.header("Settings & Info")
if not GEMINI_API_KEY:
    st.sidebar.error("GEMINI_API_KEY not set. Please set the environment variable.")
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
