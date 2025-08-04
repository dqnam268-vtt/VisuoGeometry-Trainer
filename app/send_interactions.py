import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/session/submit-answer"
HEADERS = {"Content-Type": "application/json"}
STUDENT_ID = "default_student"

# Định nghĩa các tương tác
# Mỗi dictionary là một yêu cầu POST
interactions_data = [
    # Dữ liệu tương tác cho KC: khai_niem_phan_so
    {"question_id": "khai_niem_phan_so_01", "correct": True},
    {"question_id": "khai_niem_phan_so_02", "correct": True},
    {"question_id": "khai_niem_phan_so_03", "correct": False},
    {"question_id": "khai_niem_phan_so_01", "correct": True},
    {"question_id": "khai_niem_phan_so_04", "correct": False},
    {"question_id": "khai_niem_phan_so_02", "correct": True},
    {"question_id": "khai_niem_phan_so_05", "correct": True},
    {"question_id": "khai_niem_phan_so_03", "correct": False},
    {"question_id": "khai_niem_phan_so_01", "correct": True},
    {"question_id": "khai_niem_phan_so_04", "correct": True},

    # Dữ liệu tương tác cho KC: rut_gon_phan_so
    {"question_id": "rut_gon_phan_so_01", "correct": True},
    {"question_id": "rut_gon_phan_so_02", "correct": False},
    {"question_id": "rut_gon_phan_so_01", "correct": True},
    {"question_id": "rut_gon_phan_so_03", "correct": False},
    {"question_id": "rut_gon_phan_so_02", "correct": True},

    # Dữ liệu tương tác cho KC: cong_cung_mau_so
    {"question_id": "cong_cung_mau_so_01", "correct": True},
    {"question_id": "cong_cung_mau_so_02", "correct": False},
    {"question_id": "cong_cung_mau_so_01", "correct": True},

    # Dữ liệu tương tác cho KC: phep_nhan_phan_so
    {"question_id": "phep_nhan_phan_so_01", "correct": True},
    {"question_id": "phep_nhan_phan_so_02", "correct": False}
]

def send_interaction(interaction):
    payload = {
        "student_id": STUDENT_ID,
        "question_id": interaction["question_id"],
        "submitted_answer": "placeholder_answer", # Có thể điền giá trị thực nếu cần
        "time_on_task_seconds": 15,
        "correct": interaction["correct"]
    }
    try:
        response = requests.post(BASE_URL, headers=HEADERS, data=json.dumps(payload))
        response.raise_for_status() # Ném lỗi nếu status code là 4xx hoặc 5xx
        print(f"Sent: KC='{payload['question_id']}', Correct={payload['correct']} -> Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending interaction for KC='{payload['question_id']}', Correct={payload['correct']}: {e}")

if __name__ == "__main__":
    print(f"Starting to send {len(interactions_data)} interactions...")
    for i, interaction in enumerate(interactions_data):
        send_interaction(interaction)
        time.sleep(0.5) # Chờ một chút giữa các yêu cầu để backend xử lý và huấn luyện lại
        if (i + 1) % 5 == 0: # Thông báo sau mỗi 5 yêu cầu
            print(f"--- Đã gửi {i + 1}/{len(interactions_data)} yêu cầu. Kiểm tra logs backend... ---")
    print("All interactions sent.")