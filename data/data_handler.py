"""
This is the data handler module for LocalLink.

This module manages loading, saving, and manipulating business data and user preferences.
It provides methods to filter and sort businesses, manage favorites, handle reviews,
and store user settings. All data is saved in JSON files within the "data" directory.

"""

# imports
import json
import os
import logging
import csv
import logging
from dataclasses import dataclass
from typing import List
 
# define file paths
DATA_DIR = os.path.join(os.path.dirname(__file__))
BUSINESSES_FILE = os.path.join(DATA_DIR, "businesses.json")
USER_FILE = os.path.join(DATA_DIR, "user_data.json")

# data classes
@dataclass
class Review:
    user: str
    rating: int
    text: str
    user_created: bool = False  # indicates if the review was created by the user


@dataclass
class Business:
    id: str
    name: str
    category: str
    description: str
    banner: str
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
        # user preferences stored as a dict. defaults are set in _load_user_data()
        self.preferences: dict[str, str] = {}
        self._load_businesses()
        self._load_user_data()

    def _load_businesses(self) -> None:
        # load business data from BUSINESSES_FILE
        try:
            with open(BUSINESSES_FILE, "r", encoding="utf8") as file:
                items = json.load(file)
        except Exception:
            items = []
        for biz in items:
            review_list = []
            for review in biz.get("reviews", []):
                review_list.append(Review(
                    review.get("user", ""),
                    review.get("rating", 0),
                    review.get("text", ""),
                    bool(review.get("user_created", False))
                ))
            self.businesses.append(Business(biz.get("id", ""),
                                            biz.get("name", ""),
                                            biz.get("category", ""),
                                            biz.get("description", ""),
                                            biz.get("banner", ""),
                                            review_list,
                                            biz.get("deals", [])))
        # we intentionally do not modify existing review objects on load
    
    def save_businesses(self) -> None:
        # save all business data (including reviews) to BUSINESSES_FILE
        try:
            items = []
            for biz in self.businesses:
                # serialize reviews
                reviews_data = []
                for review in biz.reviews:
                    # only persist user_created when True; older reviews
                    # shouldn't contain this key.
                    rd = {
                        "user": review.user,
                        "rating": review.rating,
                        "text": review.text,
                    }
                    if bool(getattr(review, "user_created", False)):
                        rd["user_created"] = True
                    reviews_data.append(rd)

                # serialize business
                items.append({
                    "id": biz.id,
                    "name": biz.name,
                    "category": biz.category,
                    "description": biz.description,
                    "banner": biz.banner,
                    "reviews": reviews_data,
                    "deals": biz.deals
                })

            # write to json file
            with open(BUSINESSES_FILE, "w", encoding="utf8") as file:
                json.dump(items, file, indent=2, ensure_ascii=False)
        except Exception:
            # Log any error to assist with debugging.  Because the
            # previous except catches all Exceptions, additional except
            # clauses here are unreachable and thus omitted.
            logging.exception("Error saving businesses")
    def _load_user_data(self) -> None:
        # load user data (favorites + preferences). create a default file if missing
        if not os.path.exists(USER_FILE):
            # Initialize with empty favorites and default preferences
            with open(USER_FILE, "w", encoding="utf8") as file:
                json.dump({"favorites": [], "preferences": {}}, file, indent=2)
        try:
            with open(USER_FILE, "r", encoding="utf8") as file:
                data = json.load(file)

            favs = data.get("favorites", [])

            if isinstance(favs, list):
                self._favorites = set(favs)

            # load preferences or set defaults
            prefs = data.get("preferences", {})

            if not isinstance(prefs, dict):
                prefs = {}

            # set default theme to dark if not provided
            if "theme" not in prefs:
                prefs["theme"] = "dark"

            # add other defaults: reduce_motion disables animations and
            # confirm_delete toggles confirmation when removing a favorite
            if "reduce_motion" not in prefs:
                prefs["reduce_motion"] = "no"

            if "confirm_delete" not in prefs:
                prefs["confirm_delete"] = "yes"

            if "always_on_top" not in prefs:
                prefs["always_on_top"] = "no"

            self.preferences = prefs
        except Exception:
            # On error, fall back to empty favorites and default prefs
            self._favorites = set()
            self.preferences = {"theme": "dark"}

    def save_user_data(self) -> None:
        # save favorites and preferences to disk. logs on error
        try:
            with open(USER_FILE, "w", encoding="utf8") as file:
                json.dump({
                    "favorites": sorted(self._favorites),
                    "preferences": self.preferences or {}
                }, file, indent=2)
        except Exception:
            logging.exception("Error saving user data")

    
    # Public API
    def list_businesses(self) -> List[Business]:
        return self.businesses

    def filter_businesses(self, query: str, sort_key: str, reverse_sort: bool, filter_keys: List[str], only_favs: bool) -> List[Business]:
        # filter and sort businesses. returns a new list, original and untouched
        # args:
        #   query: text to match against name or category (case-insensitive)
        #   sort_key: one of 'ratings', 'name', 'reviews', 'deals'
        #   reverse_sort: reverse the sort order
        #   filter_keys: list of categories to include
        #   only_favs: if True, only return favorite businesses
        # returns: list of businesses matching the filters

        # start with a shallow copy so we don't mutate the original list
        filtered: List[Business] = self.list_businesses().copy()

        # clean and normalize the query
        query_clean = (query or "").lower().strip()

        # filter by text: match name or category
        if query_clean:
            filtered = [business for business in filtered
                        if query_clean in business.name.lower() or
                           query_clean in business.category.lower()]

        # filter by selected categories, if any
        if filter_keys:
            filtered = [business for business in filtered if business.category in filter_keys]

        # filter to favorites only, if requested
        if only_favs:
            filtered = [business for business in filtered if self.is_favorite(business)]

        # sort results according to the requested key
        if sort_key == "ratings":
            filtered.sort(key=lambda business: business.rating, reverse=reverse_sort)

        elif sort_key == "name":
            filtered.sort(key=lambda business: business.name.lower(), reverse=reverse_sort)

        elif sort_key == "reviews":
            filtered.sort(key=lambda business: len(business.reviews), reverse=reverse_sort)

        elif sort_key == "deals":
            filtered.sort(key=lambda business: len(business.deals), reverse=reverse_sort)

        return filtered

    # these are all functions that are called by other modules, these are references. 
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
        # add a review created by the user. mark user_created=True so we can
        # identify removable reviews. we do not assign stable ids anymore.
        review = Review(user, rating, text, True)
        biz.reviews.append(review)
        self.save_businesses()

    def remove_review(self, biz: Business, review: Review) -> None:
        # remove a review (by object or by matching fields) and save changes
        try:
            # Prefer identity removal if the exact object is present
            if review in biz.reviews:
                biz.reviews.remove(review)
            else:
                # Fall back to matching by user/text/rating
                for r in list(biz.reviews):
                    if r.user == review.user and r.rating == review.rating and r.text == review.text:
                        biz.reviews.remove(r)
                        break
            self.save_businesses()
        except Exception:
            logging.exception("Error removing review")

    # Preferences API
    def get_preference(self, key: str, default: str | None = None) -> str | None:
        # get a preference by key, or return the default if it's missing
        return self.preferences.get(key, default)

    def set_preference(self, key: str, value: str) -> None:
        # set a preference in memory and save it to disk
        self.preferences[key] = value
        self.save_user_data()

    def categories(self) -> List[str]:
        # return a sorted list of unique business categories
        categories = {biz.category for biz in self.businesses}
        return sorted(categories)
    
    def get_number_of_businesses_by_category(self, category: str) -> int:
        # count how many businesses are in `category`
        # use a generator expression for efficiency
        return sum(1 for business in self.businesses if business.category == category)

    def get_average_rating_by_category(self, category: str) -> float:
        # average rating for businesses in `category`. returns 0.0 if none
        matching_businesses = [business for business in self.businesses if business.category == category]
        if not matching_businesses:
            return 0.0
        
        total_rating = sum(business.rating for business in matching_businesses)
        return total_rating / len(matching_businesses)


    # major function, this writes all of the data to a CSV file, and we format the csv file using this code/function
    def export_businesses_to_csv(self, filepath: str, favorites_only: bool = False) -> None:
        try:
            export_list = self.favorite_businesses() if favorites_only else self.businesses

            with open(filepath, "w", newline="", encoding="utf8") as csvfile:
                writer = csv.writer(csvfile)

                # One row per review (or a blank review row if none)
                writer.writerow([
                    "Business ID", "Business Name", "Category", "Description",
                    "Business Rating", "Deals",
                    "Review User", "Review Rating", "Review Text"
                ])

                for business in export_list:
                    deals_text = "; ".join(business.deals)

                    # If no reviews, still write the business once
                    if not business.reviews:
                        writer.writerow([
                            business.id,
                            business.name,
                            business.category,
                            business.description,
                            f"{business.rating:.2f}",
                            deals_text,
                            "", "", ""
                        ])
                        continue

                    # Write one row per review
                    for review in business.reviews:
                        writer.writerow([
                            business.id,
                            business.name,
                            business.category,
                            business.description,
                            f"{business.rating:.2f}",
                            deals_text,
                            review.user,
                            review.rating,
                            review.text
                        ])

        except Exception:
            logging.exception("Error exporting businesses to CSV")

    # this is the core part of our smart feature, this recommends businesses based on user favorites and ratings
    def recommend_businesses(self, top_n: int = 3) -> List[Business]:
        # return up to top_n recommended businesses based on favorites and ratings
        # If there are no favorites, simply return the top rated businesses
        if not self._favorites:
            return sorted(
                [business for business in self.businesses],
                key=lambda b: b.rating,
                reverse=True
            )[:top_n]

        # Build a weight for each category based on how many favorites
        # belong to that category. This biases recommendations toward
        # categories the user already likes.
        category_weights: dict[str, int] = {}
        for business in self.businesses:
            if business.id in self._favorites:
                category_weights[business.category] = category_weights.get(business.category, 0) + 1

        # Score businesses that are not already favorites. Higher scores
        # come from businesses with better ratings and from categories the
        # user prefers. Ratings are normalized to 0–1 by dividing by 5.
        scored: list[tuple[float, Business]] = []
        
        for business in self.businesses:
            if business.id in self._favorites:
                continue
            rating_score = business.rating / 5.0  # Assume 5 is max rating
            category_score = category_weights.get(business.category, 0)
            score = rating_score + category_score
            scored.append((score, business))

        # Sort primarily by the computed score and secondarily by rating. The
        # reverse flag puts highest scores first.
        scored.sort(key=lambda item: (item[0], item[1].rating), reverse=True)
        return [business for _, business in scored[:top_n]]
