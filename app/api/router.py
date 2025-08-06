import urllib.parse

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