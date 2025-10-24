import json
import os
from dataclasses import dataclass
from typing import List


DATA_DIR = os.path.join(os.path.dirname(__file__))
BUSINESSES_FILE = os.path.join(DATA_DIR, "businesses.json")
USER_FILE = os.path.join(DATA_DIR, "user_data.json")


@dataclass
class Business:
    id: str
    name: str
    category: str
    description: str
    reviews: List[dict]
    deals: List[str]

    @property
    def rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(review.get("rating", 0) for review in self.reviews) / len(self.reviews)


class DataHandler:

    def __init__(self) -> None:
        self.businesses: List[Business] = []
        self._favorites: set[str] = set()
        self._load_businesses()
        self._load_user_data()

    def _load_businesses(self) -> None:
        try:
            with open(BUSINESSES_FILE, "r", encoding="utf8") as file:
                items = json.load(file)
        except Exception:
            items = []
        for biz in items:
            self.businesses.append(Business(biz.get("id", ""),
                                            biz.get("name", ""),
                                            biz.get("category", ""),
                                            biz.get("description", ""),
                                            biz.get("reviews", []),
                                            biz.get("deals", [])))

    def _load_user_data(self) -> None:
        if not os.path.exists(USER_FILE):
            with open(USER_FILE, "w", encoding="utf8") as file:
                json.dump({"favorites": []}, file)
        try:
            with open(USER_FILE, "r", encoding="utf8") as file:
                data = json.load(file)
            favs = data.get("favorites", [])
            if isinstance(favs, list):
                self._favorites = set(favs)
        except Exception:
            self._favorites = set()

    def save_user_data(self) -> None:
        try:
            with open(USER_FILE, "w", encoding="utf8") as file:
                json.dump({"favorites": sorted(self._favorites)}, file, indent=2)
        except Exception:
            pass

    # Public API
    def list_businesses(self) -> List[Business]:
        return self.businesses

    def search(self, query: str) -> List[Business]:
        query_clean = (query or "").lower().strip()
        if not query_clean:
            return self.businesses
        filtered = []
        for biz in self.businesses:
            # Query in name or category
            if query_clean in biz.name.lower() or query_clean in biz.category.lower():
                filtered.append(biz)
        return filtered

    def favorite_ids(self) -> set[str]:
        return set(self._favorites)

    def favorite_businesses(self) -> List[Business]:
        return [biz for biz in self.businesses if biz.id in self._favorites]

    def is_favorite(self, biz: Business) -> bool:
        return biz.id in self._favorites

    def add_favorite(self, biz: Business) -> None:
        self._favorites.add(biz.id)
        self.save_user_data()

    def remove_favorite(self, biz: Business) -> None:
        self._favorites.discard(biz.id)
        self.save_user_data()

    def toggle_favorite(self, biz: Business) -> None:
        if self.is_favorite(biz):
            self.remove_favorite(biz)
        else:
            self.add_favorite(biz)