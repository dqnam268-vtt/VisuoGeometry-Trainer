from fastapi import APIRouter, Depends, Request, HTTPException
from typing import Dict, List

# Sửa lại import để phù hợp với cấu trúc
from ..schemas.question import QuestionPublic
from ..schemas.student import AnswerSubmission, SubmissionResult
from ..core.adaptation import AdaptationEngine
from ..core.student_model import StudentBKTManager

router = APIRouter()

# --- Dependency Functions ---
def get_student_manager(student_id: str, request: Request) -> StudentBKTManager:
    """Lấy hoặc tạo mới student manager cho một ID cụ thể."""
    student_managers: Dict[str, StudentBKTManager] = request.app.state.student_managers
    if student_id not in student_managers:
        all_kcs = request.app.state.all_kcs
        student_managers[student_id] = StudentBKTManager(student_id=student_id, all_kcs=all_kcs)
    return student_managers[student_id]

def get_question_bank(request: Request) -> list:
    return request.app.state.question_bank

def get_adaptation_engine(request: Request) -> AdaptationEngine:
    return request.app.state.adaptation_engine

# --- API Endpoints ---
@router.get("/session/{student_id}/next-question", response_model=QuestionPublic, tags=["Session"])
def get_next_question(
    student_manager: StudentBKTManager = Depends(get_student_manager),
    question_bank: list = Depends(get_question_bank),
    adaptation_engine: AdaptationEngine = Depends(get_adaptation_engine)
):
    """Lấy câu hỏi tiếp theo cho một học sinh."""
    # Logic chọn câu hỏi... (ví dụ)
    mastery_vector = student_manager.get_mastery_vector()
    kc, difficulty = adaptation_engine.get_next_question_spec(student_manager)
    
    potential_questions = [q for q in question_bank if q.get('knowledge_component') == kc and q.get('difficulty_level') == difficulty]
    if not potential_questions:
        # Fallback logic
        potential_questions = [q for q in question_bank if q.get('knowledge_component') == kc]

    if not potential_questions:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi phù hợp.")
    
    return random.choice(potential_questions)


@router.post("/session/{student_id}/submit-answer", response_model=SubmissionResult, tags=["Session"])
def submit_answer(
    submission: AnswerSubmission,
    student_manager: StudentBKTManager = Depends(get_student_manager),
    question_bank: list = Depends(get_question_bank)
):
    """Nhận và xử lý câu trả lời của học sinh."""
    # Logic xử lý câu trả lời... (ví dụ)
    question = next((q for q in question_bank if q['question_id'] == submission.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Không tìm thấy câu hỏi.")

    is_correct = (submission.submitted_answer == question['correct_answer'])
    student_manager.update_with_answer(kc=question['knowledge_component'], is_correct=is_correct)

    return {"is_correct": is_correct, "correct_answer": question['correct_answer'], "feedback": "Làm tốt lắm!" if is_correct else "Hãy thử lại nhé."}