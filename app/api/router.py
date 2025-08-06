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
# PHẦN 3: CÁC HÀM TRỢ GIÚP VÀ API MẪU (Giữ lại để tham khảo)
# =======================================================================
def create_utf8_filename_header(filename: str) -> str:
    encoded_filename = urllib.parse.quote(filename, safe='')
    return f"attachment; filename*=UTF-8''{encoded_filename}"

@router.get("/status", tags=["Health Check"])
def get_status():
    return {"status": "ok", "message": "API router is running!"}

@router.get("/export-results/{student_id}", tags=["Export"])
async def export_results(student_id: str):
    original_filename = f"kết_quả_thi_{student_id}.csv"
    csv_data = "STT,Câu hỏi,Kết quả\n1,Hình học không gian,Đúng"
    stream = io.StringIO(csv_data)
    headers = {"Content-Disposition": create_utf8_filename_header(original_filename)}
    return StreamingResponse(iter([stream.read()]), media_type="text/csv", headers=headers)

# =======================================================================
# PHẦN 4: ĐỊNH NGHĨA CÁC API CHÍNH CỦA ỨNG DỤNG
# Đây là nơi logic cốt lõi của VisuoGeometry-Trainer được xây dựng.
# =======================================================================

class AnswerPayload(BaseModel):
    """Định nghĩa dữ liệu đầu vào cho việc nộp câu trả lời."""
    student_id: str
    question_id: int
    is_correct: bool

@router.post("/session/start", tags=["Học tập"])
async def start_session(request: Request, student_id: str):
    """
    Bắt đầu một phiên học mới cho học sinh.
    Nếu học sinh đã tồn tại, tải lại thông tin.
    """
    student_managers = request.app.state.student_managers
    all_kcs = request.app.state.all_knowledge_components

    if student_id not in student_managers:
        # Nếu là học sinh mới, tạo một trình quản lý mới cho họ
        student_managers[student_id] = StudentBKTManager(kcs=all_kcs)
        message = f"Phiên làm việc mới đã được tạo cho học sinh {student_id}."
    else:
        message = f"Chào mừng học sinh {student_id} quay trở lại."

    return {"student_id": student_id, "message": message}

@router.get("/questions/next", tags=["Học tập"])
async def get_next_question(request: Request, student_id: str):
    """
    Lấy câu hỏi tiếp theo phù hợp nhất cho học sinh dựa trên trình độ hiện tại.
    """
    if student_id not in request.app.state.student_managers:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh. Vui lòng bắt đầu phiên học.")

    # Lấy các engine và dữ liệu từ state của ứng dụng
    student_manager: StudentBKTManager = request.app.state.student_managers[student_id]
    adaptation_engine = request.app.state.adaptation_engine
    question_bank = request.app.state.question_bank

    # Lấy trạng thái kiến thức hiện tại của học sinh
    # Giả định: lớp StudentBKTManager có hàm `get_mastery_levels()`
    knowledge_state = student_manager.get_mastery_levels()

    # Dùng AdaptationEngine để chọn câu hỏi tiếp theo
    # Giả định: lớp AdaptationEngine có hàm `select_question()`
    question_id = adaptation_engine.select_question(knowledge_state)
    
    # Tìm câu hỏi đầy đủ từ kho câu hỏi
    next_question = next((q for q in question_bank if q['id'] == question_id), None)
    
    if not next_question:
        return {"message": "Chúc mừng! Bạn đã hoàn thành tất cả các câu hỏi."}

    return next_question

@router.post("/answers/submit", tags=["Học tập"])
async def submit_answer(request: Request, payload: AnswerPayload):
    """
    Học sinh nộp câu trả lời, hệ thống cập nhật mô hình kiến thức.
    """
    student_id = payload.student_id
    if student_id not in request.app.state.student_managers:
        raise HTTPException(status_code=404, detail="Không tìm thấy học sinh. Vui lòng bắt đầu phiên học.")

    student_manager: StudentBKTManager = request.app.state.student_managers[student_id]
    question_bank = request.app.state.question_bank

    # Tìm thành phần kiến thức (KC) của câu hỏi đã trả lời
    question = next((q for q in question_bank if q['id'] == payload.question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy câu hỏi với ID {payload.question_id}.")
    
    kc = question['knowledge_component']
    
    # Cập nhật mô hình BKT với kết quả mới
    # Giả định: lớp StudentBKTManager có hàm `update_skill()`
    student_manager.update_skill(kc=kc, is_correct=payload.is_correct)
    
    return {"message": "Đã ghi nhận câu trả lời của bạn."}