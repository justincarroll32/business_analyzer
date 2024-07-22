import utilities as ut

class AnalyzeServing:

    def get_serving_per_place(self, detail: dict) -> dict:
        """Returns dictionary with key being a place and value being a dictionary of what they serve (true, false, or DNE)."""
        places = {}
        for place in detail:

            details = detail[place]
            name = ut.get_name(details)
            name = name + "-" + (ut.get_address(details).split(","))[0]
            breakfast, lunch, brunch, dinner = ut.get_meals(details)
            # price level out of 4
            servings = [breakfast, lunch, brunch, dinner, ut.get_wine(details), ut.get_beer(details), ut.get_wheelchair_accessible(details),
                        ut.get_vegetarian(details), ut.get_dine_in(details), ut.get_takeout(details), ut.get_reservable(details),
                        ut.get_price_level(details)]
            keyss = ['breakfast', 'lunch', 'brunch', 'dinner', 'wine', 'beer', 'wheelchair',
                    'vegetarian', 'dine_in', 'takeout', 'reservable', 'price_level']
            places[name] = dict(zip(keyss, servings))

        return places

    def get_average_price_level(self, places: dict) -> str:
        """Returns average price level of all places."""
        total = 0
        for key, value in places.items():
            if value['price_level'] != "DNE":
                total = total + int(value['price_level'])

        return f'{round((total / len(places)), 2)}'

    def get_percentages(self, places: dict) -> dict:
        """Returns percentages of places that are true for each category except price level."""

        keyss = ['breakfast', 'lunch', 'brunch', 'dinner', 'wine', 'beer', 'wheelchair',
                    'vegetarian', 'dine_in', 'takeout', 'reservable']

        categories = ['Serves breakfast', 'Serves lunch', 'Serves brunch', 'Serves dinner', 'Serves wine', 'Serves beer', 'Wheelchair accessible',
                    'Serves vegetarian', 'Dine in', 'Takeout', 'Reservable', 'Average price level (out of 4)']

        percents = {key: 0 for key in keyss}
        total_places = len(places)

        for k in keyss:
            total = 0
            for key, value in places.items():
                if value[k] is True:
                    total = total + 1

            percent = f'{round((total / total_places) * 100, 2)}%'
            percents[k] = percent

        percents['price_level'] = self.get_average_price_level(places)
        return {key: value for key, value in zip(categories, list(percents.values()))}

    def make_suggestions(self, percents: dict) -> tuple:
        """Returns list of servings that are below 50% places serving them."""
        threshold = 50
        # make dict from string to numbers again
        percents = {key: float((value.split("%"))[0]) for key, value in percents.items()}

        suggestions = [key for key in list(percents.keys()) if percents[key] < threshold and key != "Average price level (out of 4)"]
        # cleaned_words = [word.replace("Serves", "").replace(" ", "") for word in suggestions]
        suggestions = [key.replace('Serves', '').replace(' ', '').capitalize() for key in suggestions]
        return (len(percents), suggestions)

    def analyze_serving_report(self, details: dict) -> list:
        """Main function that returns percents of servings and suggestions"""

        details = ut.delete_non_operational_businesses(details)
        places = self.get_serving_per_place(details)
        serving_percents = self.get_percentages(places)
        suggestions = self.make_suggestions(serving_percents)

        return [serving_percents, suggestions]
