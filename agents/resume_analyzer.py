from typing import Optional, Dict, Any, List
import json
import sys
import os
import io # Added for BytesIO
from docx import Document # Added for .docx parsing
from PyPDF2 import PdfReader # Added for .pdf parsing

# Add project root to sys.path to allow absolute import of 'utils'
# current_file_path -> adk_poc/agents/resume_analyzer.py
# project_root -> adk_poc/
current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path) # .../adk_poc/agents
project_root = os.path.dirname(parent_directory)      # .../adk_poc

if project_root not in sys.path:
    sys.path.append(project_root)

class ResumeAnalyzer:
    def __init__(self):
        """Initializes the ResumeAnalyzer agent."""
        print("ResumeAnalyzer initialized.")

    def analyze(self, resume_content: bytes, file_name: str) -> Optional[Dict[str, Any]]: # Added file_name
        """
        Analyzes the resume content to extract skills and experience.
        This method uses Gemini API via utils.py.

        Args:
            resume_content: The content of the resume as bytes.
            file_name: The name of the uploaded file, used to determine type.

        Returns:
            A dictionary containing extracted 'skills' and 'experience_years',
            or an error dictionary if analysis fails.
        """
        print(f"ResumeAnalyzer: Received resume '{file_name}' for analysis (first 100 bytes: {resume_content[:100]}...)") # Added file_name
        resume_text = ""
        file_extension = os.path.splitext(file_name)[1].lower()
        print(f"ResumeAnalyzer: Processing file '{file_name}' with extension '{file_extension}'")

        try:
            if file_extension == '.docx':
                try:
                    document = Document(io.BytesIO(resume_content))
                    full_text = []
                    for para in document.paragraphs:
                        full_text.append(para.text)
                    resume_text = '\n'.join(full_text)
                except Exception as e:
                    print(f"ResumeAnalyzer: Error parsing DOCX file '{file_name}': {e}")
                    return {"error": f"Could not parse DOCX content: {str(e)}", "skills": [], "experience_years": 0}
            
            elif file_extension == '.pdf':
                try:
                    reader = PdfReader(io.BytesIO(resume_content))
                    if reader.is_encrypted:
                        # Attempt to decrypt with an empty password, common for some PDFs
                        try:
                            reader.decrypt('')
                        except Exception as decrypt_err:
                            print(f"ResumeAnalyzer: PDF file '{file_name}' is encrypted and could not be decrypted: {decrypt_err}")
                            return {"error": "PDF file is encrypted and decryption failed.", "skills": [], "experience_years": 0}
                    
                    full_text = []
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        full_text.append(page.extract_text())
                    resume_text = '\n'.join(filter(None, full_text)) # Filter out None results from extract_text
                except Exception as e:
                    print(f"ResumeAnalyzer: Error parsing PDF file '{file_name}': {e}")
                    return {"error": f"Could not parse PDF content: {str(e)}", "skills": [], "experience_years": 0}

            elif file_extension == '.txt':
                try:
                    resume_text = resume_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        resume_text = resume_content.decode('latin-1') # Try another common encoding
                    except UnicodeDecodeError as e:
                        print(f"ResumeAnalyzer: Error decoding TXT file '{file_name}': {e}")
                        return {"error": f"Could not decode TXT content: {str(e)}", "skills": [], "experience_years": 0}
            else:
                print(f"ResumeAnalyzer: Unsupported file type '{file_extension}' for file '{file_name}'. Attempting plain text decode as fallback.")
                try:
                    resume_text = resume_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        resume_text = resume_content.decode('latin-1')
                    except UnicodeDecodeError as e:
                        print(f"ResumeAnalyzer: Error decoding unsupported file type '{file_name}' as text: {e}")
                        return {"error": f"Unsupported file type, and could not decode as plain text: {str(e)}", "skills": [], "experience_years": 0}
            
            if not resume_text.strip():
                print(f"ResumeAnalyzer: Extracted text from '{file_name}' is empty or only whitespace.")
                return {"error": "Extracted text from resume is empty.", "skills": [], "experience_years": 0}

        except Exception as e: # Catch-all for unexpected issues during text extraction phase
            print(f"ResumeAnalyzer: General error during text extraction for '{file_name}': {e}")
            return {"error": f"General error extracting text from resume: {str(e)}", "skills": [], "experience_years": 0}

        prompt = f"""
Analyze the following resume text and extract the key skills and total years of professional experience. 
Provide the output as a JSON object with two keys: 'skills' (a list of strings for technical skills) and 'experience_years' (an integer representing the total number of years of professional experience).
If specific years of experience cannot be determined, use null for 'experience_years'.

Resume Text:
```
{resume_text}
```

JSON Output:"""

        try:
            import utils # Absolute import, assuming adk_poc is in sys.path
            gemini_response_str = utils.generate_text_from_gemini(prompt)
            
            if not gemini_response_str or gemini_response_str.startswith("Error:"):
                print(f"ResumeAnalyzer: Gemini API error or empty response: {gemini_response_str}")
                return {"error": gemini_response_str or "Empty response from API", "skills": [], "experience_years": 0}

            # Attempt to parse the JSON response from Gemini
            try:
                # Gemini might return the JSON within backticks or other markdown
                cleaned_response = gemini_response_str.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:-3].strip()
                elif cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:-3].strip()
                
                parsed_response = json.loads(cleaned_response)
                
                skills = parsed_response.get("skills", [])
                experience = parsed_response.get("experience_years")

                if not isinstance(skills, list):
                    # If skills is not a list (e.g., a single string), wrap it in a list
                    skills = [str(skill_item) for skill_item in ([skills] if skills is not None else [])]
                else:
                    # Ensure all items in skills list are strings
                    skills = [str(skill_item) for skill_item in skills]
                
                if experience is None or not isinstance(experience, (int, float)):
                    experience_years = 0 # Default if not found, null, or not a number
                else:
                    experience_years = int(experience)

                print(f"ResumeAnalyzer: Successfully parsed Gemini response. Skills: {skills}, Experience: {experience_years}")
                return {"skills": skills, "experience_years": experience_years}
            
            except json.JSONDecodeError as e:
                print(f"ResumeAnalyzer: Error parsing JSON response from Gemini: {e}")
                print(f"Gemini Raw Response: {gemini_response_str}")
                return {"error": "Failed to parse skills and experience from resume response.", "skills": [], "experience_years": 0}
            except Exception as e:
                print(f"ResumeAnalyzer: Unexpected error processing Gemini response: {e}")
                return {"error": f"Unexpected error processing API response: {str(e)}", "skills": [], "experience_years": 0}

        except ImportError as e:
            print(f"ResumeAnalyzer: Error importing utils: {e}. Ensure 'agents' is a package and utils.py is in the parent directory.")
            return {"error": "Internal server error (module import issue).", "skills": [], "experience_years": 0}
        except Exception as e:
            print(f"ResumeAnalyzer: General error during analysis: {e}")
            return {"error": f"General error during resume analysis: {str(e)}", "skills": [], "experience_years": 0}
