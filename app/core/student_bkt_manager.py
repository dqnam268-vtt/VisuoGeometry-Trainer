# app/core/student_bkt_manager.py

import pandas as pd
import datetime
import json
import os
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import Student, Interaction

DATA_DIR = "./student_data"

class StudentBKTManager:
    def __init__(self, student_id: str, all_kcs: list):
        self.student_id = student_id
        self.all_kcs = all_kcs
        self.p_L0 = 0.1
        self.p_T = 0.2
        self.p_S = 0.1
        self.p_G = 0.2

        # _ensure_data_dir_exists là của giải pháp cũ, có thể bỏ
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)

        self.mastery_file = os.path.join(DATA_DIR, f"{self.student_id}_mastery.json")
        self.interactions_file = os.path.join(DATA_DIR, f"{self.student_id}_interactions.csv")

        self.mastery_vector = self._load_mastery_from_file()
        if not self.mastery_vector:
            self.mastery_vector = {kc: self.p_L0 for kc in all_kcs}
            self._save_mastery_to_file()

        self.interactions_df = self._load_interactions_from_file()

    # ... (các hàm khác không đổi)

    def get_topic_stars(self) -> dict:
        topic_stars = {}
        for kc in self.all_kcs:
            mastery_level = self.mastery_vector.get(kc, self.p_L0)
            if mastery_level <= 0.2:
                topic_stars[kc] = 0
            elif mastery_level <= 0.4:
                topic_stars[kc] = 1
            elif mastery_level <= 0.6:
                topic_stars[kc] = 2
            elif mastery_level <= 0.8:
                topic_stars[kc] = 3
            elif mastery_level <= 0.9:
                topic_stars[kc] = 4
            else:
                topic_stars[kc] = 5
        return topic_stars

    # ... (các hàm còn lại không đổi)