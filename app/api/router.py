# Tệp: app/api/router.py

# =======================================================================
# PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT
# =======================================================================
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import io
import urllib.parse
from pydantic import BaseModel

# Import các lớp logic để gợi ý kiểu dữ liệu (type hinting)
from ..core.student_bkt_manager import StudentBKTManager

# =======================================================================
# PHẦN 2: KHỞI TẠO ĐỐI TƯỢNG ROUTER
# =======================================================================
router = APIRouter()

# =======================================================================
# PHẦN 3: CÁC HÀM TRỢ GIÚP VÀ API MẪU
# =======================================================================
def create_utf8_filename_header(filename: str) -> str:
    encoded_filename = urllib.parse.quote(filename, safe='')
    return f"attachment; filename*=UTF-8''{encoded_filename}"

# =======================================================================
# PHẦN 4: ĐỊNH NGHĨA CÁC API CHÍNH CỦA ỨNG DỤNG
# =======================================================================

class AnswerPayload(BaseModel):
    student_id: str
    question_id: int
    is_correct: bool

@router.post("/session/start", tags=["Học tập"])
async def start_session(request: Request, student_id: str):
    student_managers = request.app.state.student_managers
    all_kcs = request.app.state.all_knowledge_components

    if student_id not in student_managers:
        student_managers[student_id] = StudentBKTManager(kcs=all_kcs)
        message = f"Phiên làm việc mới đã được tạo cho học sinh {student_id}."
    else:
        message = f"Chào mừng học sinh {student_id} quay trở lại."

    return {"student_id": student_id, "message": message}

# === THAY ĐỔI Ở ĐÂY ===
@router.get("/session/{student_id}/next-question", tags=["Học tập"])
async def get_next_question(student_id: str, request: Request):
    """
    Lấy câu hỏi tiếp theo phù hợp nhất cho học sinh.
    URL đã được cập nhật để nhận student_id từ path.
    """
    if student_id not in request.app.state.student_managers:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh. Vui lòng bắt đầu phiên học.")

    student_manager: StudentBKTManager = request.app.state.student_managers[student_id]
    adaptation_engine = request.app.state.adaptation_engine
    question_bank = request.app.state.question_bank
    
    knowledge_state = student_manager.get_mastery_levels()
    question_id = adaptation_engine.select_question(knowledge_state)
    
    next_question = next((q for q in question_bank if q['id'] == question_id), None)
    
    if not next_question:
        return {"message": "Chúc mừng! Bạn đã hoàn thành tất cả các câu hỏi."}

    return next_question

# === API MỚI ĐƯỢC THÊM VÀO ===
@router.get("/students/{student_id}/progress", tags=["Học tập"])
async def get_student_progress(student_id: str, request: Request):
    """
    Lấy thông tin tiến độ và trạng thái kiến thức của học sinh.
    """
    if student_id not in request.app.state.student_managers:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy học sinh {student_id}.")

    student_manager: StudentBKTManager = request.app.state.student_managers[student_id]
    
    # Giả định: lớp StudentBKTManager có hàm `get_mastery_levels()`
    knowledge_state = student_manager.get_mastery_levels()
    
    return {
        "student_id": student_id,
        "knowledge_state": knowledge_state
    }

@router.post("/answers/submit", tags=["Học tập"])
async def submit_answer(request: Request, payload: AnswerPayload):
    student_id = payload.student_id
    if student_id not in request.app.state.student_managers:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh. Vui lòng bắt đầu phiên học.")

    student_manager: StudentBKTManager = request.app.state.student_managers[student_id]
    question_bank = request.app.state.question_bank

    question = next((q for q in question_bank if q['id'] == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy câu hỏi với ID {payload.question_id}.")
    
    kc = question['knowledge_component']
    
    student_manager.update_skill(kc=kc, is_correct=payload.is_correct)
    
    return {"message": "Đã ghi nhận câu trả lời của bạn."}