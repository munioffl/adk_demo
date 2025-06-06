from typing import Optional, Dict, Any
import sys
import os
import json

# Add project root to sys.path to allow absolute import of 'utils'
current_file_path = os.path.abspath(__file__)
parent_directory = os.path.dirname(current_file_path)
project_root = os.path.dirname(parent_directory)

if project_root not in sys.path:
    sys.path.append(project_root)

import utils

class CodeEvaluator:
    def __init__(self):
        """Initializes the CodeEvaluator agent."""
        print("CodeEvaluator initialized.")

    def evaluate(self, question: str, code_submission: str) -> Optional[str]:
        """
        Evaluates the submitted code against the given question using Gemini API,
        expecting a JSON response for structured feedback.

        Args:
            question: The coding question that was asked.
            code_submission: The candidate's code solution.

        Returns:
            A Markdown string containing structured feedback (table and text),
            or None if evaluation fails or response is not as expected.
        """
        print(f"CodeEvaluator: Evaluating code for question: '{question[:70]}...'" )

        prompt = f"""
Analyze the following code submission based on the provided coding question.
Provide a detailed evaluation as a JSON object.

The JSON object must have the following top-level keys:
- "evaluation_summary": A brief overall summary of the code submission (string).
- "scores": An object containing scores for different categories.
- "category_feedback": An object containing qualitative feedback for each category.

The "scores" object must contain these keys, with values as strings representing scores (e.g., "X / 10"):
- "problem_understanding"
- "problem_solving_approach"
- "code_structure_readability"
- "syntax_language_usage"
- "test_coverage_edge_cases"

The "category_feedback" object must contain these keys, with string values providing specific feedback:
- "problem_understanding_feedback"
- "problem_solving_approach_feedback"
- "code_structure_readability_feedback"
- "syntax_language_usage_feedback"
- "test_coverage_edge_cases_feedback"

Coding Question:
```
{question}
```

Candidate's Code Submission:
```python
{code_submission}
```

Ensure the output is a single, valid JSON object only, enclosed in triple backticks if necessary for clarity in your response, but the core content must be parseable JSON.
JSON Output:
"""
        try:
            gemini_response_str = utils.generate_text_from_gemini(prompt)

            if not gemini_response_str or gemini_response_str.startswith("Error:"):
                print(f"CodeEvaluator: Gemini API error or empty response: {gemini_response_str}")
                return "Error: Could not get evaluation from AI. Please try again."

            # Attempt to parse the JSON response from Gemini
            # Gemini might return the JSON within backticks or other markdown
            cleaned_response_str = gemini_response_str.strip()
            if cleaned_response_str.startswith("```json"):
                cleaned_response_str = cleaned_response_str[7:] # Remove ```json
            if cleaned_response_str.endswith("```"):
                cleaned_response_str = cleaned_response_str[:-3] # Remove ```
            cleaned_response_str = cleaned_response_str.strip()

            try:
                eval_data: Dict[str, Any] = json.loads(cleaned_response_str)
            except json.JSONDecodeError as e:
                print(f"CodeEvaluator: Failed to parse JSON response from Gemini: {e}")
                print(f"CodeEvaluator: Raw Gemini response was: {gemini_response_str}")
                return "Error: AI response was not in the expected format. Could not parse evaluation."

            # Extract data, with defaults for safety
            summary = eval_data.get("evaluation_summary", "Summary not provided.")
            scores = eval_data.get("scores", {})
            cat_feedback = eval_data.get("category_feedback", {})

            # Build Markdown output
            md_output = f"### Overall Summary:\n{summary}\n\n"
            md_output += "### Detailed Evaluation Scores:\n"
            md_output += "| Category                     | Score    |\n"
            md_output += "| ---------------------------- | -------- |\n"
            md_output += f"| Problem Understanding        | {scores.get('problem_understanding', 'N/A')}   |\n"
            md_output += f"| Problem Solving Approach     | {scores.get('problem_solving_approach', 'N/A')} |\n"
            md_output += f"| Code Structure & Readability | {scores.get('code_structure_readability', 'N/A')} |\n"
            md_output += f"| Syntax & Language Usage    | {scores.get('syntax_language_usage', 'N/A')}  |\n"
            md_output += f"| Test Coverage & Edge Cases   | {scores.get('test_coverage_edge_cases', 'N/A')} |\n\n"

            md_output += "### Category Specific Feedback:\n"
            md_output += f"- **Problem Understanding:** {cat_feedback.get('problem_understanding_feedback', 'N/A')}\n"
            md_output += f"- **Problem Solving Approach:** {cat_feedback.get('problem_solving_approach_feedback', 'N/A')}\n"
            md_output += f"- **Code Structure & Readability:** {cat_feedback.get('code_structure_readability_feedback', 'N/A')}\n"
            md_output += f"- **Syntax & Language Usage:** {cat_feedback.get('syntax_language_usage_feedback', 'N/A')}\n"
            md_output += f"- **Test Coverage & Edge Cases:** {cat_feedback.get('test_coverage_edge_cases_feedback', 'N/A')}\n"
            
            print(f"CodeEvaluator: Successfully processed Gemini evaluation.")
            return md_output.strip()

        except ImportError as e:
            print(f"CodeEvaluator: Error importing utils: {e}.")
            return "Error: System configuration issue (utils import)."
        except Exception as e:
            print(f"CodeEvaluator: General error during code evaluation: {e}")
            return f"Error: An unexpected error occurred during code evaluation: {str(e)}"
