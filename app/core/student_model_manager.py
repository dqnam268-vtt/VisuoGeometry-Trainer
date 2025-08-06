import pandas as pd
import os
import json
from typing import Dict, Any

STUDENT_MODELS_DIR = "app/data/student_models/"
os.makedirs(STUDENT_MODELS_DIR, exist_ok=True)

class StudentModelManager:
    """
    Quản lý trạng thái của học sinh bằng một mô hình đơn giản, tất định như mô tả trong bài báo nghiên cứu.
    """
    def __init__(self, student_id: str, all_kcs: list):
        self.student_id = student_id
        self.all_kcs = all_kcs
        self.state_path = os.path.join(STUDENT_MODELS_DIR, f"{student_id}_state.json")
        self.interactions_path = os.path.join(STUDENT_MODELS_DIR, f"{student_id}_interactions.csv")
        
        self.state = self._load_state()
        self.interactions_df = self._load_interactions()
        print(f"Đã khởi tạo StudentModelManager cho sinh viên: {student_id}")

    def _load_state(self) -> Dict[str, Any]:
        """Tải trạng thái của học sinh, bao gồm vector trình độ."""
        if os.path.exists(self.state_path):
            with open(self.state_path, 'r') as f:
                return json.load(f)
        else:
            # Trạng thái ban đầu: mỗi kỹ năng bắt đầu với trình độ là 0.3
            initial_mastery = {kc: 0.3 for kc in self.all_kcs}
            return {"mastery_vector": initial_mastery}

    def _save_state(self):
        """Lưu trạng thái của học sinh."""
        with open(self.state_path, 'w') as f:
            json.dump(self.state, f, indent=4)

    def _load_interactions(self) -> pd.DataFrame:
        """Tải lịch sử tương tác của học sinh."""
        if os.path.exists(self.interactions_path):
            return pd.read_csv(self.interactions_path)
        return pd.DataFrame(columns=['order_id', 'user_id', 'skill_name', 'correct'])

    def _save_interactions(self):
        """Lưu lịch sử tương tác."""
        self.interactions_df.to_csv(self.interactions_path, index=False)

    def update_with_answer(self, kc: str, is_correct: bool):
        """Cập nhật trình độ của học sinh dựa trên câu trả lời bằng một công thức đơn giản."""
        learning_rate = 0.25
        penalty_rate = 0.15
        
        current_mastery = self.state['mastery_vector'].get(kc, 0.3)
        
        if is_correct:
            # Học một phần của những gì chưa biết
            new_mastery = current_mastery + (1 - current_mastery) * learning_rate
        else:
            # Quên một phần của những gì đã biết
            new_mastery = current_mastery - current_mastery * penalty_rate
        
        # Giới hạn điểm thành thạo trong khoảng [0.05, 0.95]
        self.state['mastery_vector'][kc] = max(0.05, min(0.95, new_mastery))
        
        print(f"Đã cập nhật KC '{kc}': trình độ từ {current_mastery:.2f} -> {self.state['mastery_vector'][kc]:.2f}")
        
        new_order_id = (self.interactions_df['order_id'].max() + 1) if not self.interactions_df.empty else 1
        new_interaction = pd.DataFrame([{'order_id': new_order_id, 'user_id': self.student_id, 'skill_name': kc, 'correct': int(is_correct)}])
        self.interactions_df = pd.concat([self.interactions_df, new_interaction], ignore_index=True)
        
        self._save_state()
        self._save_interactions()

    def get_mastery_vector(self) -> Dict[str, float]:
        """Lấy vector trình độ hiện tại của học sinh."""
        return self.state.get("mastery_vector", {kc: 0.3 for kc in self.all_kcs})