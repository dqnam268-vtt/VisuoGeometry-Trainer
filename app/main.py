import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Sửa lại import để trỏ đến đúng tệp
from .api.router import router as api_router
from .core.adaptation import AdaptationEngine
from .core.student_model_manager import StudentModelManager 

app = FastAPI(
    title="VisuoGeometry-Trainer API",
    description="API cho Hệ thống Luyện tập Hình học Trực quan Thích ứng",
    version="1.0.0"
)

origins = ["*"] # Cho phép tất cả các nguồn gốc
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def load_resources():
    """Nạp các tài nguyên cần thiết khi ứng dụng khởi động."""
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
    app.state.student_managers: Dict[str, StudentModelManager] = {}
    
    print("Hệ thống đã sẵn sàng để hỗ trợ nhiều người dùng.")

app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Chào mừng bạn đến với VisuoGeometry-Trainer API!"}