# bkt_params.py

# Các tham số BKT cho từng thành phần kiến thức (Knowledge Component - KC).
# p_L0: Xác suất học sinh đã biết kỹ năng ban đầu.
# p_T: Xác suất học sinh sẽ học được kỹ năng trong lần thử tiếp theo.
# p_S: Xác suất học sinh trả lời sai mặc dù đã biết.
# p_G: Xác suất học sinh trả lời đúng mặc dù chưa biết.

BKT_PARAMS = {
    "hinh_hop_lap_phuong": {
        "p_L0": 0.2,   # Khái niệm cơ bản, xác suất biết ban đầu có thể cao hơn một chút.
        "p_T": 0.2,    # Dễ học.
        "p_S": 0.1,    # Khả năng nhầm lẫn thấp.
        "p_G": 0.2     # Khả năng đoán đúng thấp.
    },
    "dien_tich_the_tich_hinh_hop": {
        "p_L0": 0.1,   # Cần tính toán, xác suất biết ban đầu thấp hơn.
        "p_T": 0.25,   # Sau khi hiểu công thức, tốc độ học có thể nhanh hơn.
        "p_S": 0.15,   # Dễ nhầm lẫn công thức hoặc tính toán sai.
        "p_G": 0.15    # Khả năng đoán thấp.
    },
    "hinh_lang_tru_dung": {
        "p_L0": 0.15,  # Tương tự hình hộp, nhưng có thể hơi khó hơn.
        "p_T": 0.2,    # Dễ học.
        "p_S": 0.15,   # Dễ nhầm lẫn khái niệm.
        "p_G": 0.2     # Khả năng đoán thấp.
    },
    "dien_tich_the_tich_hinh_lang_tru": {
        "p_L0": 0.05,  # Khá phức tạp, xác suất biết ban đầu thấp.
        "p_T": 0.3,    # Sau khi hiểu, tốc độ học có thể rất nhanh.
        "p_S": 0.2,    # Khả năng nhầm lẫn cao.
        "p_G": 0.1     # Khả năng đoán thấp.
    }
}