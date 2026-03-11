# bkt_params.py

# Các tham số BKT cho từng thành phần kiến thức (Knowledge Component - KC).
# p_L0: Xác suất học sinh đã biết kỹ năng ban đầu.
# p_T: Xác suất học sinh sẽ học được kỹ năng trong lần thử tiếp theo.
# p_S: Xác suất học sinh trả lời sai mặc dù đã biết.
# p_G: Xác suất học sinh trả lời đúng mặc dù chưa biết.

BKT_PARAMS = {
    "hinh_hop_lap_phuong": {
        "p_L0": 0.35,   # Đã cập nhật từ 0.2 (Kết quả dò tìm)
        "p_T": 0.2,    
        "p_S": 0.1,    
        "p_G": 0.2     
    },
    "dien_tich_the_tich_hinh_hop": {
        "p_L0": 0.35,   # Đã cập nhật từ 0.1 (Kết quả dò tìm)
        "p_T": 0.25,   
        "p_S": 0.15,   
        "p_G": 0.15    
    },
    "hinh_lang_tru_dung": {
        "p_L0": 0.31,   # Đã cập nhật từ 0.15 (Kết quả dò tìm)
        "p_T": 0.2,    
        "p_S": 0.15,   
        "p_G": 0.2     
    },
    "dien_tich_the_tich_hinh_lang_tru": {
        "p_L0": 0.35,   # Đã cập nhật từ 0.05 (Kết quả dò tìm)
        "p_T": 0.3,    
        "p_S": 0.2,    
        "p_G": 0.1     
    }
}