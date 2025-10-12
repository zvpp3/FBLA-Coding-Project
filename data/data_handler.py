import json
from typing import List

class Business:
    def __init__(self, name, category, reviews, deals, favorited) -> None:
        self.name = name
        self.category = category
        self.reviews = reviews
        self.deals = deals
        self.rating = 0.0
        self.favorited = favorited
        self.calculate_average_rating()

    def calculate_average_rating(self) -> float:
        for review in self.reviews:
            self.rating += review["rating"]
        if self.reviews:
            self.rating /= len(self.reviews)

    def add_review(self) -> None:
        return
    
class DataHandler:
    def __init__(self) -> None:
        self.businesses = []
        self._load_business_data()

    def _get_favorite_business_names(self):
        # Open JSON
        with open('data/user_data.json', 'r') as file:
            user_data = json.load(file)
        return user_data["favorites"]

    def _load_business_data(self) -> List[str]:
        # Get favorites
        favorites = self._get_favorite_business_names()
        # Open JSON
        with open('data/businesses.json', 'r') as file:
            data = json.load(file)
        for biz in data:
            self.businesses.append(Business(
                name = biz["name"],
                category = biz["category"],
                reviews = biz["reviews"],
                deals = biz["deals"],
                favorited = biz["name"] in favorites
            ))
    
    def filter_business_list(self, text: str):
        query = text.lower().strip()
        if not query:
            return self.businesses
        filtered = [
            biz
            for biz in self.businesses
            if query in biz.name.lower() or query in biz.category.lower()
        ]
        return filtered
    
    def get_favorite_businesses(self):
        filtered = [
            biz
            for biz in self.businesses
            if biz.favorited
        ]
        return filtered
    
    def add_business_to_favorites(self, biz: Business):
        biz.favorited = True
        with open("data/user_data.json", "r") as file:
            data = json.load(file)
        data["favorites"].append(biz.name)
        with open("data/user_data.json", "w") as file:
            json.dump(data, file, indent=4)

    def remove_business_from_favorites(self, biz: Business):
        biz.favorited = False
        with open("data/user_data.json", "r") as file:
            data = json.load(file)
        data["favorites"].remove(biz.name)
        with open("data/user_data.json", "w") as file:
            json.dump(data, file, indent=4)
    
    def toggle_favorite_business(self, biz: Business):
        if biz.favorited:
            self.remove_business_from_favorites(biz)
        else:
            self.add_business_to_favorites(biz)