import csv
from typing import List, Dict

class CSVService:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._data: List[Dict[str, str]] = []
        self._load_data()

    def _load_data(self) -> None:
        """Loads data from the CSV file."""
        self._data = []
        try:
            with open(self.file_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self._data.append(row)
        except Exception as e:
            # We can log this or let the caller handle it.
            raise ValueError(f"Could not read CSV file: {e}")

    def get_all_employees(self) -> List[Dict[str, str]]:
        """Returns the full list of employees."""
        return self._data

    def search_employees(self, query: str) -> List[Dict[str, str]]:
        """Filters employees by name based on the search query."""
        if not query:
            return self._data
        query = query.lower()
        return [
            emp for emp in self._data
            if query in emp.get("Full Name", "").lower()
        ]
