import json

class Business:
    def __init__(self, name, category, reviews, deals) -> None:
        self.name = name
        self.category = category
        self.reviews = reviews
        self.deals = deals
        self.rating = 0.0
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

    def _load_business_data(self) -> None:
        # Open JSON
        with open('data/businesses.json', 'r') as file:
            data = json.load(file)
        for biz in data:
            self.businesses.append(Business(
                name = biz["name"],
                category = biz["category"],
                reviews = biz["reviews"],
                deals = biz["deals"]
            ))
    
    def filter_business_list(self, text: str) -> None:
        query = text.lower().strip()
        if not query:
            return self.businesses
        filtered = [
            biz
            for biz in self.businesses
            if query in biz.name.lower() or query in biz.category.lower()
        ]
        return filtered
    