# app/api/router.py

from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import StreamingResponse
import io
import pandas as pd
import random
from typing import Dict, List

from ..schemas.question import QuestionPublic, Submission, SubmissionResult, Option, Content

from ..core.adaptation import AdaptationEngine
from ..core.student_bkt_manager import StudentBKTManager

router = APIRouter()

def get_question_bank(request: Request) -> list:
    return request.app.state.question_bank

def get_adaptation_engine(request: Request) -> AdaptationEngine:
    return request.app.state.adaptation_engine

def get_student_manager(student_id: str, request: Request) -> StudentBKTManager:
    student_managers: Dict[str, StudentBKTManager] = request.app.state.student_managers
    if student_id not in student_managers:
        all_kcs = request.app.state.all_knowledge_components
        student_managers[student_id] = StudentBKTManager(student_id=student_id, all_kcs=all_kcs)
    return student_managers[student_id]

@router.get("/session/{student_id}/next-question", response_model=QuestionPublic, tags=["Session"])
def get_next_question(
    student_id: str,
    question_bank: list = Depends(get_question_bank),
    adaptation_engine: AdaptationEngine = Depends(get_adaptation_engine),
    student_manager: StudentBKTManager = Depends(get_student_manager)
):
    next_kc, next_difficulty = adaptation_engine.get_next_question_spec(student_manager=student_manager)
    
    potential_questions = [
        q for q in question_bank
        if q.get('knowledge_component') == next_kc and q.get('difficulty_level') == next_difficulty
    ]
    
    if not potential_questions:
        potential_questions = [
            q for q in question_bank
            if q.get('knowledge_component') == next_kc
        ]
    
    if not potential_questions:
        raise HTTPException(status_code=404, detail=f"Không có câu hỏi nào cho KC: {next_kc}")
    
    selected_question = random.choice(potential_questions)
    
    correct_answer_text = selected_question.get('correct_answer')
    options_list = []
    for opt_text in selected_question.get('options', []):
        options_list.append(Option(text=opt_text, is_correct=(opt_text == correct_answer_text)))
    
    question_data_for_public = selected_question.copy()
    question_data_for_public['options'] = options_list

    return QuestionPublic(**question_data_for_public)

@router.post("/session/{student_id}/submit-answer", response_model=SubmissionResult, tags=["Session"])
def submit_answer(
    student_id: str,
    submission: Submission,
    question_bank: list = Depends(get_question_bank),
    student_manager: StudentBKTManager = Depends(get_student_manager)
):
    question = next((q for q in question_bank if q['question_id'] == submission.question_id), None)
    if not question:
         raise HTTPException(status_code=404, detail=f"Không tìm thấy câu hỏi ID: {submission.question_id}")

    question_kc = question['knowledge_component']
    
    student_manager.update_mastery(kc=question_kc, is_correct=submission.correct)
    
    return {
        "message": "Answer submitted successfully",
        "correct": submission.correct,
        "correct_answer": question.get('correct_answer', '')
    }

@router.get("/students/{student_id}/export", tags=["Students"])
def export_student_data(
    student_id: str,
    student_manager: StudentBKTManager = Depends(get_student_manager)
):
    mastery_vector = student_manager.get_mastery_vector()
    interactions_df = student_manager.get_interactions_df()
    
    output = io.StringIO()
    output.write("--- MASTERY VECTOR ---\n")
    mastery_df = pd.DataFrame(list(mastery_vector.items()), columns=['skill_name', 'mastery_prob'])
    output.write(mastery_df.to_csv(index=False))
    output.write("\n\n--- INTERACTION HISTORY ---\n")
    output.write(interactions_df.to_csv(index=False, encoding='utf-8'))
    
    response = StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=results_{student_id}.csv"}
    )
    return response

@router.get("/students/{student_id}/dashboard", tags=["Students"], response_model=List[Dict])
def get_dashboard_data(
    student_id: str,
    student_manager: StudentBKTManager = Depends(get_student_manager)
):
    mastery_vector = student_manager.get_mastery_vector()
    sorted_mastery = sorted(mastery_vector.items(), key=lambda item: item[1], reverse=True)
    dashboard_data = [{"skill": kc, "mastery": prob} for kc, prob in sorted_mastery]
    return dashboard_data

@router.get("/students/{student_id}/progress")
async def get_student_progress(
    student_id: str,
    student_manager: StudentBKTManager = Depends(get_student_manager)
):
    topic_stars = student_manager.get_topic_stars()
    total_stars = student_manager.get_total_stars()
    current_title = student_manager.get_current_title()

    formatted_topic_stars = [
        {"topic": kc, "stars": stars} for kc, stars in topic_stars.items()
    ]

    return {
        "student_id": student_manager.student_id,
        "topic_progress": formatted_topic_stars,
        "total_stars": total_stars,
        "title": current_title
    }