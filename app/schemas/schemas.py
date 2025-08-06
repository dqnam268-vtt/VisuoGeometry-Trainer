from pydantic import BaseModel
from typing import List, Optional, Dict

# === CÁC MODEL TỪ TỆP question.py CŨ ===

class Content(BaseModel):
    text: str
    image: Optional[str] = None
    formula_latex: Optional[str] = None

class QuestionPublic(BaseModel):
    question_id: str
    content: Content
    question_type: str
    options: List[str]
    knowledge_component: str
    difficulty_level: int
    correct_answer: str
    hints: Optional[List[Dict]] = None

# === CÁC MODEL TỪ TỆP student.py CŨ ===

class Submission(BaseModel):
    question_id: str
    correct: bool

class SubmissionResult(BaseModel):
    message: str
    correct: bool
    correct_answer: str