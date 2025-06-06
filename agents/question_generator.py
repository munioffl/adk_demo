import sys
import os
from typing import Optional, List, Union # Correct type hints

# Ensure the 'agents' directory is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) 
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import generate_text_from_gemini # Gemini helper

class QuestionGenerator:
    def __init__(self):
        print("QuestionGenerator initialized.")

    def generate(self, skills: Union[List[str], str], experience: int, difficulty: str) -> Optional[str]:
        """
        Generates a coding question based on the provided skills and experience.
        Uses Gemini API.

        Args:
            skills: A list of skills (e.g., ["Python", "Django"]) or a single skill string.
            experience: Years of experience as an integer.
            difficulty: The desired difficulty of the question (e.g., "Easy", "Medium", "Hard").

        Returns:
            A string containing the generated coding question, or None if generation fails.
        """
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        elif isinstance(skills, str):
            skills_str = skills
        else:
            print("QuestionGenerator: Invalid type for skills argument. Must be List[str] or str.")
            return None
        
        if not isinstance(experience, int):
            print("QuestionGenerator: Invalid type for experience argument, must be int.")
            return None

        prompt = f"""Generate a {difficulty}-difficulty coding question suitable for a candidate with the following skills: {skills_str} and {experience} years of experience.
The question should be solvable in approximately 30-45 minutes for its difficulty level and focus on practical problem-solving.
Provide only the question text itself, without any preamble, labels, explanations, or markdown formatting. Just the plain text of the question.
"""
        try:
            print(f"QuestionGenerator: Generating {difficulty} question for skills: '{skills_str}', experience: {experience} years...")
            
            question_text = generate_text_from_gemini(prompt)

            if question_text:
                cleaned_question = question_text.strip()
                # Basic cleaning for common Gemini artifacts like ```
                if cleaned_question.startswith("```") and cleaned_question.endswith("```"):
                    lines = cleaned_question.splitlines()
                    if len(lines) > 2 and lines[0].strip().lower().startswith("```") and lines[-1].strip() == "```":
                        cleaned_question = "\\n".join(lines[1:-1]).strip()
                    else: 
                        cleaned_question = cleaned_question.strip("` \t\\n")
                
                print(f"QuestionGenerator: Successfully generated question: {cleaned_question[:150]}...")
                return cleaned_question
            else:
                print("QuestionGenerator: Gemini returned an empty response or failed to generate a question.")
                return None
        except Exception as e:
            print(f"QuestionGenerator: Error during Gemini API call or processing: {e}")
            return None
            