import random
from typing import Tuple, Dict
from .student_model_manager import StudentModelManager # <-- Sửa tên tệp ở đây

class AdaptationEngine:
    def __init__(self, all_kcs: list):
        self.all_kcs = all_kcs
        print("Cơ chế Thích ứng đang chạy ở chế độ Heuristic đơn giản.")

    def get_next_question_spec(self, student_manager: StudentModelManager) -> Tuple[str, int]:
        mastery_vector = student_manager.get_mastery_vector()
        
        min_mastery = min(mastery_vector.values())
        low_mastery_kcs = [kc for kc, prob in mastery_vector.items() if prob == min_mastery]
        
        chosen_kc = random.choice(low_mastery_kcs)
        
        if min_mastery < 0.5:
            difficulty = random.choice([1, 2])
        elif 0.5 <= min_mastery < 0.9:
            difficulty = random.choice([3, 4])
        else:
            difficulty = 5
            
        print(f"Heuristic chọn: KC='{chosen_kc}', Độ khó='{difficulty}' (Trình độ hiện tại: {min_mastery:.2f})")
        
        return chosen_kc, difficulty