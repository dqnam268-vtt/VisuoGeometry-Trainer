# Tệp: app/api/router.py

# =======================================================================
# PHẦN 1: IMPORT CÁC THƯ VIỆN CẦN THIẾT
# =======================================================================
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import urllib.parse

# =======================================================================
# PHẦN 2: KHỞI TẠO ĐỐI TƯỢNG ROUTER
# Dòng này cực kỳ quan trọng, nó tạo ra biến 'router' mà main.py cần.
# Đây chính là chìa khóa để sửa lỗi "ImportError".
# =======================================================================
router = APIRouter()

# =======================================================================
# PHẦN 3: CÁC HÀM TRỢ GIÚP (BẠN ĐÃ VIẾT ĐÚNG PHẦN NÀY)
# =======================================================================
def create_utf8_filename_header(filename: str) -> str:
    """
    Tạo giá trị cho header 'Content-Disposition' để hỗ trợ tên tệp UTF-8 (tiếng Việt).
    
    Hàm này sẽ mã hóa tên tệp theo chuẩn RFC 5987, đảm bảo trình duyệt 
    hiểu được các ký tự đặc biệt.
    
    Args:
        filename: Tên tệp gốc (có thể chứa tiếng Việt).
        
    Returns:
        Một chuỗi định dạng cho header Content-Disposition.
    """
    # URL-encode tên tệp bằng UTF-8
    encoded_filename = urllib.parse.quote(filename, safe='')
    
    # Tạo chuỗi header theo định dạng: attachment; filename*=UTF-8''<encoded_name>
    return f"attachment; filename*=UTF-8''{encoded_filename}"

# =======================================================================
# PHẦN 4: ĐỊNH NGHĨA CÁC API ENDPOINT (ROUTE)
# Đây là nơi bạn đặt logic cho các API của mình.
# Luôn sử dụng @router.get, @router.post, v.v.
# =======================================================================

@router.get("/status", tags=["Health Check"])
def get_status():
    """
    Một API đơn giản để kiểm tra xem router có đang hoạt động hay không.
    """
    return {"status": "ok", "message": "API router is running!"}

@router.get("/export-results/{student_id}", tags=["Export"])
async def export_results(student_id: str):
    """
    API xuất kết quả thi ra tệp CSV với tên tệp tiếng Việt.
    """
    original_filename = f"kết_quả_thi_{student_id}.csv"
    csv_data = "STT,Câu hỏi,Kết quả\n1,Hình học không gian,Đúng"
    stream = io.StringIO(csv_data)
    
    headers = {
        "Content-Disposition": create_utf8_filename_header(original_filename)
    }
    
    return StreamingResponse(
        iter([stream.read()]), 
        media_type="text/csv", 
        headers=headers
    )

# ---> BẠN CÓ THỂ THÊM CÁC API KHÁC CỦA MÌNH VÀO ĐÂY <---