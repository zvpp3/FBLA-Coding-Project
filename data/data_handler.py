import json
import os
from dataclasses import dataclass
from typing import List


DATA_DIR = os.path.join(os.path.dirname(__file__))
BUSINESSES_FILE = os.path.join(DATA_DIR, "businesses.json")
USER_FILE = os.path.join(DATA_DIR, "user_data.json")


@dataclass
class BusinessRecord:
    id: str
    name: str
    category: str
    reviews: List[dict]
    deals: List[str]

    @property
    def rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(r.get("rating", 0) for r in self.reviews) / len(self.reviews)


class DataHandler:
    """Simple handler for reading business data and tracking favorites.

    Favorites are stored as a list of business ids in `data/user_data.json`.
    """

    def __init__(self) -> None:
        self.businesses: List[BusinessRecord] = []
        self._favorites: set[str] = set()
        self._load_businesses()
        self._load_user_data()

    def _load_businesses(self) -> None:
        try:
            with open(BUSINESSES_FILE, "r", encoding="utf8") as f:
                items = json.load(f)
        except Exception:
            items = []
        for b in items:
            # support old files without id by falling back to name
            bid = b.get("id") or b.get("name")
            self.businesses.append(BusinessRecord(bid, b.get("name", ""), b.get("category", ""), b.get("reviews", []), b.get("deals", [])))

    def _load_user_data(self) -> None:
        if not os.path.exists(USER_FILE):
            # initialize
            with open(USER_FILE, "w", encoding="utf8") as f:
                json.dump({"favorites": []}, f)
        try:
            with open(USER_FILE, "r", encoding="utf8") as f:
                data = json.load(f)
            favs = data.get("favorites", [])
            if isinstance(favs, list):
                self._favorites = set(favs)
        except Exception:
            self._favorites = set()

    def save_user_data(self) -> None:
        try:
            with open(USER_FILE, "w", encoding="utf8") as f:
                json.dump({"favorites": sorted(self._favorites)}, f, indent=2)
        except Exception:
            pass

    # Public API
    def list_businesses(self) -> List[BusinessRecord]:
        return self.businesses

    def search(self, query: str) -> List[BusinessRecord]:
        q = (query or "").lower().strip()
        if not q:
            return self.businesses
        return [b for b in self.businesses if q in b.name.lower() or q in b.category.lower()]

    def favorite_ids(self) -> set[str]:
        return set(self._favorites)

    def favorite_records(self) -> List[BusinessRecord]:
        return [b for b in self.businesses if b.id in self._favorites]

    def is_favorite(self, record: BusinessRecord) -> bool:
        return record.id in self._favorites

    def add_favorite(self, record: BusinessRecord) -> None:
        self._favorites.add(record.id)
        self.save_user_data()

    def remove_favorite(self, record: BusinessRecord) -> None:
        self._favorites.discard(record.id)
        self.save_user_data()

    def toggle_favorite(self, record: BusinessRecord) -> None:
        if self.is_favorite(record):
            self.remove_favorite(record)
        else:
            self.add_favorite(record)