import json
import os
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
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
        # User preferences are stored as a dictionary. This allows for easy
        # extension as more settings (e.g., theme, accent color) are added to
        # the application. Defaults are defined in `_load_user_data()` if
        # preferences are absent from the on‑disk JSON.
        self.preferences: dict[str, str] = {}
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
                                            biz.get("banner", ""),
                                            review_list,
                                            biz.get("deals", [])))
    
    def save_businesses(self) -> None:
        """
        Save all business data (including reviews) to BUSINESSES_FILE.
        A timestamped backup of the existing file is created before overwriting to
        protect against accidental data loss.
        """
        try:
            # Back up the existing businesses file before writing a new one
            self._backup_file(BUSINESSES_FILE)
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
                    "banner": biz.banner,
                    "reviews": reviews_data,
                    "deals": biz.deals
                })

            # Write to JSON file
            with open(BUSINESSES_FILE, "w", encoding="utf8") as file:
                json.dump(items, file, indent=2, ensure_ascii=False)
        except Exception:
            logging.exception("Error saving businesses")
        except Exception as e:
            print(f"Error saving businesses: {e}")

    def _backup_file(self, filepath: str) -> None:
        """
        Create a timestamped backup of a given file. Backups are stored in a
        'backups' directory within the data folder. If the source file does not
        exist, the method simply returns. Backup failures are logged but do not
        interrupt execution.

        Args:
            filepath: The absolute path to the file to back up.
        """
        try:
            if not os.path.exists(filepath):
                return
            backup_dir = os.path.join(DATA_DIR, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = os.path.basename(filepath)
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
            shutil.copy2(filepath, backup_path)
        except Exception:
            logging.exception(f"Failed to backup {filepath}")

    def _load_user_data(self) -> None:
        """
        Load user data from disk. User data currently consists of two
        components: a list of favorite business IDs and a preferences
        dictionary. If the file does not exist it is created with
        sensible defaults. Missing keys fall back to defaults.
        """
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
            # Load preferences or set defaults
            prefs = data.get("preferences", {})
            if not isinstance(prefs, dict):
                prefs = {}
            # Set default theme to dark if not provided
            if "theme" not in prefs:
                # default to dark theme when not specified
                prefs["theme"] = "dark"
            # Set default sort to name if not provided
            if "default_sort" not in prefs:
                prefs["default_sort"] = "name"
            # Add new preferences with sensible defaults.  Reduce motion
            # disables page transition animations, and confirm_delete
            # triggers a confirmation dialog when removing a favorite.  If
            # keys are missing, populate them so the settings page can
            # display correct values.
            if "reduce_motion" not in prefs:
                prefs["reduce_motion"] = "no"
            if "confirm_delete" not in prefs:
                prefs["confirm_delete"] = "yes"
            self.preferences = prefs
        except Exception:
            # On error, fall back to empty favorites and default prefs
            self._favorites = set()
            self.preferences = {"theme": "dark"}

    def save_user_data(self) -> None:
        """
        Persist the current set of favorite business IDs to disk. A backup of the
        previous file is created before overwriting. If saving fails for any
        reason, the exception is logged.
        """
        try:
            # Backup the current user data before writing a new file.
            self._backup_file(USER_FILE)
            with open(USER_FILE, "w", encoding="utf8") as file:
                json.dump({
                    "favorites": sorted(self._favorites),
                    "preferences": self.preferences or {}
                }, file, indent=2)
        except Exception:
            logging.exception("Error saving user data")

    def restore_last_user_backup(self) -> None:
        """
        Restore the most recent backup of user_data.json. This is useful if the
        current user data becomes corrupted or accidentally overwritten. After
        restoration, the user data is reloaded into memory. If no backups are
        available, the method simply returns.
        """
        backup_dir = os.path.join(DATA_DIR, "backups")
        if not os.path.isdir(backup_dir):
            return
        backups = [f for f in os.listdir(backup_dir) if f.startswith(os.path.basename(USER_FILE))]
        if not backups:
            return
        # Determine the most recent backup based on the timestamp embedded in the filename.
        latest = max(backups, key=lambda f: f.split(".")[-2] if "." in f else "")
        backup_path = os.path.join(backup_dir, latest)
        try:
            shutil.copy2(backup_path, USER_FILE)
            # Reload favorites from the restored file
            self._load_user_data()
        except Exception:
            logging.exception("Failed to restore user data from backup")

    # Public API
    def list_businesses(self) -> List[Business]:
        return self.businesses

    def filter_businesses(self, query: str, sort_key: str, reverse_sort: bool, filter_keys: List[str], only_favs: bool) -> List[Business]:
        """
        Filter and sort businesses based on a query string, selected sort
        criteria, category filters and whether only favorites should be
        included. This method constructs a new list rather than mutating
        the original ``businesses`` list.

        Args:
            query (str): Free‑text query to match against business names and
                categories. Case insensitive.
            sort_key (str): The attribute by which to sort results (e.g.
                "ratings", "name", "reviews", "deals").
            reverse_sort (bool): Whether to reverse the sort order.
            filter_keys (List[str]): A list of category names to include.
            only_favs (bool): Whether to restrict results to the user's
                favorite businesses.

        Returns:
            List[Business]: A list of businesses matching the filters.
        """
        # Start with a shallow copy of the entire business list. We copy to
        # avoid mutating the original ``businesses`` when sorting.
        filtered: List[Business] = self.list_businesses().copy()

        # Clean and normalize the query for comparison (lowercase & trim)
        query_clean = (query or "").lower().strip()

        # Filter by free‑text query: include businesses where the query
        # appears in either the name or the category
        if query_clean:
            filtered = [business for business in filtered
                        if query_clean in business.name.lower() or
                           query_clean in business.category.lower()]

        # Filter by selected categories, if any
        if filter_keys:
            filtered = [business for business in filtered if business.category in filter_keys]

        # Filter to favorites only, if requested
        if only_favs:
            filtered = [business for business in filtered if self.is_favorite(business)]

        # Sort the results according to the requested key. We choose the
        # appropriate attribute for sorting and apply the reverse flag.
        if sort_key == "ratings":
            filtered.sort(key=lambda business: business.rating, reverse=reverse_sort)
        elif sort_key == "name":
            filtered.sort(key=lambda business: business.name.lower(), reverse=reverse_sort)
        elif sort_key == "reviews":
            filtered.sort(key=lambda business: len(business.reviews), reverse=reverse_sort)
        elif sort_key == "deals":
            filtered.sort(key=lambda business: len(business.deals), reverse=reverse_sort)

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

    # Preferences API
    def get_preference(self, key: str, default: str | None = None) -> str | None:
        """
        Retrieve a user preference by key. If the key is not present,
        return the provided default or None.

        Args:
            key: Preference key to look up.
            default: Value to return if key is missing.

        Returns:
            The stored preference or the supplied default.
        """
        return self.preferences.get(key, default)

    def set_preference(self, key: str, value: str) -> None:
        """
        Set a user preference. The preference is stored in the in-memory
        dictionary and persisted to disk immediately.

        Args:
            key: The preference key.
            value: The new value for the preference.
        """
        self.preferences[key] = value
        self.save_user_data()

    def categories(self) -> List[str]:
        """
        Return a sorted list of unique business categories. Using a set for
        deduplication improves efficiency over repeatedly checking a list.

        Returns:
            List[str]: Alphabetically sorted unique categories.
        """
        categories = {biz.category for biz in self.businesses}
        return sorted(categories)
    
    def get_number_of_businesses_by_category(self, category: str) -> int:
        """
        Count the number of businesses in a given category.

        Args:
            category (str): The category to count.

        Returns:
            int: Number of businesses in the specified category.
        """
        # Sum up businesses matching the given category. Using a generator
        # expression avoids building an intermediate list and is efficient.
        return sum(1 for business in self.businesses if business.category == category)

    def get_average_rating_by_category(self, category: str) -> float:
        """
        Compute the average rating of all businesses belonging to a given
        category. If there are no businesses in the specified category
        the method returns ``0.0`` to avoid division by zero.

        Args:
            category (str): The business category for which to calculate
                the average rating.

        Returns:
            float: The average rating for businesses in ``category``. A value
                between 0 and 5, where 0 signifies no available ratings.
        """
        # Filter out businesses that match the provided category
        matching_businesses = [business for business in self.businesses
                               if business.category == category]
        # If no businesses match, immediately return 0.0
        if not matching_businesses:
            return 0.0
        # Sum the ratings for each business and divide by the count to get
        # the average. The ``rating`` property on Business already returns
        # an averaged rating across that business's reviews.
        total_rating = sum(business.rating for business in matching_businesses)
        return total_rating / len(matching_businesses)

    def export_businesses_to_csv(self, filepath: str, favorites_only: bool = False) -> None:
        """
        Export business information to a CSV file. This helper writes a
        header row followed by one row per business. If ``favorites_only``
        is ``True`` then only the user's favorite businesses are exported;
        otherwise all businesses are included.

        The CSV columns are: ``ID``, ``Name``, ``Category``, ``Description``,
        ``Rating``, ``Deals``, and ``Reviews``. Deals and reviews are joined
        into single strings separated by semicolons so that each business
        occupies a single row.

        Args:
            filepath (str): The absolute or relative path to save the CSV.
            favorites_only (bool, optional): Whether to export only
                favorites. Defaults to ``False``.
        """
        import csv
        try:
            # Decide which list of businesses to export based on the flag
            export_list = self.favorite_businesses() if favorites_only else self.businesses
            # Open the destination CSV for writing
            with open(filepath, "w", newline="", encoding="utf8") as csvfile:
                writer = csv.writer(csvfile)
                # Write header row
                writer.writerow([
                    "ID", "Name", "Category", "Description",
                    "Rating", "Deals", "Reviews"
                ])
                # Iterate through each business and assemble row data
                for business in export_list:
                    # Join deals and reviews into strings. We include both
                    # the review text and the rating to make the export
                    # self‑contained and readable.
                    deals_text = "; ".join(business.deals)
                    reviews_text = "; ".join([
                        f"{review.user}: {review.text} (Rating {review.rating})"
                        for review in business.reviews
                    ])
                    writer.writerow([
                        business.id,
                        business.name,
                        business.category,
                        business.description,
                        f"{business.rating:.2f}",
                        deals_text,
                        reviews_text
                    ])
        except Exception:
            # Log any unexpected error; this helps during debugging but
            # silently ignores failures when running in production.
            logging.exception("Error exporting businesses to CSV")

    def recommend_businesses(self, top_n: int = 3) -> List[Business]:
        """
        Produce a ranked list of business recommendations based on the
        categories of the user's favorite businesses and overall ratings.
        Favorites themselves are excluded. If the user hasn't marked
        any favorites, the top‑rated businesses are returned.

        Args:
            top_n (int): The maximum number of recommendations to return.

        Returns:
            List[Business]: Recommended businesses in descending order of
            suitability.
        """
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
        # ``reverse`` flag puts highest scores first.
        scored.sort(key=lambda item: (item[0], item[1].rating), reverse=True)
        return [business for _, business in scored[:top_n]]
