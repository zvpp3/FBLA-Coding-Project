import json
import os
from dataclasses import dataclass
from typing import List


DATA_DIR = os.path.join(os.path.dirname(__file__))
BUSINESSES_FILE = os.path.join(DATA_DIR, "businesses.json")
USER_FILE = os.path.join(DATA_DIR, "user_data.json")


@dataclass
class Review:
    user: str
    rating: int
    text: str


@dataclass
class Business:
    id: str
    name: str
    category: str
    description: str
    reviews: List[Review]
    deals: List[str]

    @property
    def rating(self) -> float:
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)


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
            review_list = []
            for review in biz.get("reviews", []):
                review_list.append(Review(review.get("user", ""),
                                          review.get("rating", 0),
                                          review.get("text", "")))
            self.businesses.append(Business(biz.get("id", ""),
                                            biz.get("name", ""),
                                            biz.get("category", ""),
                                            biz.get("description", ""),
                                            review_list,
                                            biz.get("deals", [])))
    
    def save_businesses(self) -> None:
        """Save all business data (including reviews) to BUSINESSES_FILE."""
        try:
            items = []
            for biz in self.businesses:
                # Serialize reviews
                reviews_data = []
                for review in biz.reviews:
                    reviews_data.append({
                        "user": review.user,
                        "rating": review.rating,
                        "text": review.text
                    })

                # Serialize business
                items.append({
                    "id": biz.id,
                    "name": biz.name,
                    "category": biz.category,
                    "description": biz.description,
                    "reviews": reviews_data,
                    "deals": biz.deals
                })

            # Write to JSON file
            with open(BUSINESSES_FILE, "w", encoding="utf8") as file:
                json.dump(items, file, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving businesses: {e}")

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

        # Lower case and strip query
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

    def add_review(self, biz: Business, user: str, rating: int, text: str) -> None:
        review = Review(user, rating, text)
        biz.reviews.append(review)
        self.save_businesses()