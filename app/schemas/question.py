from pydantic import BaseModel
from typing import List, Optional, Dict

class Option(BaseModel):
    text: str
    is_correct: bool

class Content(BaseModel):
    text: str
    image: Optional[str] = None
    formula_latex: Optional[str] = None

class QuestionPublic(BaseModel):
    question_id: str
    content: Content
    question_type: str
    options: List[Option]
    knowledge_component: str
    difficulty_level: int
    hints: Optional[List[Dict]] = None

class Submission(BaseModel):
    question_id: str
    correct: bool

class SubmissionResult(BaseModel):
    message: str
    correct: bool
    correct_answer: str