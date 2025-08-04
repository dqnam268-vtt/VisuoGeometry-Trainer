# app/main.py

import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import các router và các lớp logic từ các gói con trong cùng gói 'app'
from .api.router import router
from .core.adaptation import AdaptationEngine
from .core.student_bkt_manager import StudentBKTManager

app = FastAPI(
    title="Hệ Thống Luyện Tập Phân Số Thích Ứng",
    description="Ứng dụng giúp học sinh luyện tập phân số với khả năng thích ứng dựa trên trình độ.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",                                    # Cho phát triển cục bộ
        "null",                                                     # Cho việc mở index.html trực tiếp từ ổ đĩa (chỉ cho test, không dùng prod)
        "https://dqnam268-vtt.github.io",                           # URL gốc của GitHub Pages
        "https://dqnam268-vtt.github.io/adaptive-fractions-its1",   # URL cụ thể của repo trên GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Ứng dụng đang khởi động...")

    question_bank_path = 'app/data/question_bank.json'

    try:
        with open(question_bank_path, "r", encoding="utf-8") as f:
            question_data = json.load(f)
        app.state.question_bank = question_data
        print(f"Đã tải {len(question_data)} câu hỏi từ {question_bank_path}")
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy tệp '{question_bank_path}'. Vui lòng đảm bảo tệp nằm đúng đường dẫn.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Lỗi: Không thể đọc tệp '{question_bank_path}'. Đảm bảo tệp là JSON hợp lệ.")
        exit(1)

    all_kcs = sorted(list(set(q["knowledge_component"] for q in question_data)))
    app.state.all_knowledge_components = all_kcs
    print(f"Đã phát hiện {len(all_kcs)} thành phần kiến thức (Knowledge Components): {', '.join(all_kcs)}")

    app.state.adaptation_engine = AdaptationEngine(all_kcs=all_kcs)
    print("Đã khởi tạo Adaptation Engine.")

    app.state.student_managers = {}
    print("Đã khởi tạo bộ quản lý học sinh (cache).")
    print("Ứng dụng khởi động hoàn tất.")

app.include_router(router, prefix="/api/v1")