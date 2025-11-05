import csv
import os
from typing import List, Dict

class CsvTable:
    def __init__(self, path: str, headers: List[str]):
        self.path = path
        self.headers = list(headers)
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

    def read_all(self) -> List[Dict[str, str]]:
        with open(self.path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = [dict(r) for r in reader]
        # Normalize to declared headers
        norm = []
        for r in rows:
            norm.append({k: r.get(k, "") for k in self.headers})
        return norm

    def overwrite(self, rows: List[Dict[str, str]]) -> None:
        with open(self.path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in self.headers})

    def append(self, row: Dict[str, str]) -> None:
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.headers)
            writer.writerow({k: row.get(k, "") for k in self.headers})