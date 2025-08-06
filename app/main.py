import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Sửa lại import để phù hợp với vị trí mới
from .api.router import router as api_router
from .core.adaptation import AdaptationEngine
from .core.student_model import StudentBKTManager # Giả sử bạn đang dùng BKT

app = FastAPI(
    title="Adaptive Fractions ITS API",
    description="API cho Hệ thống Luyện tập Thích ứng về Phân số",
    version="1.0.0"
)

# ... (phần còn lại của tệp main.py không đổi, nhưng hãy đảm bảo bạn có quản lý state)

@app.on_event("startup")
async def load_resources():
    """Nạp các tài nguyên cần thiết khi ứng dụng khởi động."""
    # Sửa đường dẫn data cho đúng
    data_path = os.path.join(os.path.dirname(__file__), "data", "question_bank.json")
    with open(data_path, "r", encoding="utf-8") as f:
        question_bank = json.load(f)
    print(f"Đã tải {len(question_bank)} câu hỏi vào bộ nhớ.")

    all_kcs = sorted(list(set(
        q.get('knowledge_component') for q in question_bank if 'knowledge_component' in q
    )))
    print(f"Tìm thấy {len(all_kcs)} thành phần kiến thức.")

    app.state.question_bank = question_bank
    app.state.all_kcs = all_kcs
    app.state.adaptation_engine = AdaptationEngine(all_kcs=all_kcs)
    
    # Quản lý nhiều học sinh
    app.state.student_managers: Dict[str, StudentBKTManager] = {}

    print("Hệ thống đã sẵn sàng.")

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Chào mừng bạn đến với API của Hệ thống Luyện tập Thích ứng!"}