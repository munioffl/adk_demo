from typing import Tuple, Optional, Union, List # Added typing imports
from agents.resume_analyzer import ResumeAnalyzer
from agents.question_generator import QuestionGenerator
from agents.code_evaluator import CodeEvaluator
# from utils import generate_text_from_gemini # If manager directly uses Gemini

class ManagerAgent:
    def __init__(self):
        """Initializes the ManagerAgent and its subordinate agents."""
        self.resume_analyzer = ResumeAnalyzer()
        self.question_generator = QuestionGenerator()
        self.code_evaluator = CodeEvaluator()
        print("ManagerAgent initialized with sub-agents.")

    def process_resume_and_generate_question(self, resume_content: bytes, file_name: str, difficulty: str) -> Tuple[Optional[Union[List[str], str]], Optional[str]]:
        """
        Coordinates the resume analysis and question generation process.

        Args:
            resume_content: The content of the uploaded resume as bytes.
            file_name: The name of the uploaded file.
            difficulty: The desired difficulty level for the question (e.g., "Easy", "Medium", "Hard").

        Returns:
            A tuple containing (extracted_skills, generated_question).
            Returns (None, None) if any step fails, or (skills, None) if only question generation fails.
        """
        print(f"ManagerAgent: Received resume '{file_name}' for {difficulty} question, starting analysis...")
        
        extracted_skills_data = self.resume_analyzer.analyze(resume_content, file_name)
        if not extracted_skills_data:
            print("ManagerAgent: Failed to extract skills from resume.")
            return None, None
        
        skills = extracted_skills_data.get("skills")
        experience = extracted_skills_data.get("experience_years")
        print(f"ManagerAgent: Extracted skills - {skills}, Experience - {experience} years")
        
        if not skills or experience is None: # Ensure experience is not None
            print("ManagerAgent: Missing skills or experience from analysis.")
            return None, None

        generated_question = self.question_generator.generate(skills, experience, difficulty)
        if not generated_question:
            print("ManagerAgent: Failed to generate a question.")
            # Return skills even if question generation fails, so UI can show something
            return skills, None 
        
        print(f"ManagerAgent: Generated question - {generated_question[:100]}...")

        return skills, generated_question

    def evaluate_code_submission(self, question: str, code_submission: str, language: str) -> Optional[str]:
        """
        Coordinates the code evaluation process.

        Args:
            question: The coding question that was asked.
            code_submission: The user's code submission.
            language: The detected programming language of the submission.

        Returns:
            Feedback on the code submission, or None if evaluation fails.
        """
        print(f"ManagerAgent: Received {language} code submission for question: {question}")
        feedback = self.code_evaluator.evaluate(question, code_submission, language)
        if not feedback:
            print("ManagerAgent: Failed to evaluate code.")
            return None
        print(f"ManagerAgent: Evaluation feedback - {feedback}")
        
        return feedback
