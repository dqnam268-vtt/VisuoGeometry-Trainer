from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
import io
import pandas as pd
from ..schemas import QuestionPublic, Submission, SubmissionResult # Cập nhật import
from ..core.adaptation import AdaptationEngine
from ..core.student_model_manager import StudentModelManager # <-- Sửa tên tệp ở đây
import random
from typing import Dict, List

router = APIRouter()

def get_question_bank(request: Request) -> list:
    return request.app.state.question_bank

def get_adaptation_engine(request: Request) -> AdaptationEngine:
    return request.app.state.adaptation_engine

def get_student_manager(student_id: str, request: Request) -> StudentModelManager:
    student_managers: Dict[str, StudentModelManager] = request.app.state.student_managers
    if student_id not in student_managers:
        all_kcs = request.app.state.all_kcs
        student_managers[student_id] = StudentModelManager(student_id=student_id, all_kcs=all_kcs)
    return student_managers[student_id]

@router.get("/session/{student_id}/next-question", response_model=QuestionPublic, tags=["Session"])
def get_next_question(
    student_id: str,
    question_bank: list = Depends(get_question_bank),
    adaptation_engine: AdaptationEngine = Depends(get_adaptation_engine),
    student_manager: StudentModelManager = Depends(get_student_manager)
):
    next_kc, next_difficulty = adaptation_engine.get_next_question_spec(student_manager=student_manager)
    potential_questions = [q for q in question_bank if q.get('knowledge_component') == next_kc and q.get('difficulty_level') == next_difficulty]
    if not potential_questions:
        potential_questions = [q for q in question_bank if q.get('knowledge_component') == next_kc]
    if not potential_questions:
        raise HTTPException(status_code=404, detail=f"Không có câu hỏi nào cho KC: {next_kc}")
    
    selected_question = random.choice(potential_questions)
    return QuestionPublic(**selected_question)

@router.post("/session/{student_id}/submit-answer", response_model=SubmissionResult, tags=["Session"])
def submit_answer(
    student_id: str,
    submission: Submission,
    question_bank: list = Depends(get_question_bank),
    student_manager: StudentModelManager = Depends(get_student_manager)
):
    question = next((q for q in question_bank if q['question_id'] == submission.question_id), None)
    if not question:
         raise HTTPException(status_code=404, detail=f"Không tìm thấy câu hỏi ID: {submission.question_id}")

    question_kc = question['knowledge_component']
    student_manager.update_with_answer(kc=question_kc, is_correct=submission.correct)
    
    return {"message": "Answer submitted successfully", "correct": submission.correct, "correct_answer": question.get('correct_answer', '')}

@router.get("/students/{student_id}/export", tags=["Students"])
def export_student_data(
    student_id: str,
    student_manager: StudentModelManager = Depends(get_student_manager)
):
    mastery_vector = student_manager.get_mastery_vector()
    interactions_df = student_manager.interactions_df
    output = io.StringIO()
    output.write("--- MASTERY VECTOR ---\n")
    mastery_df = pd.DataFrame(list(mastery_vector.items()), columns=['skill_name', 'mastery_prob'])
    output.write(mastery_df.to_csv(index=False))
    output.write("\n\n--- INTERACTION HISTORY ---\n")
    output.write(interactions_df.to_csv(index=False))
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=results_{student_id}.csv"}
    )
    return response