import json
import os
from docx import Document
import pandas as pd
import numpy as np
import argparse
import data as gd
import heapq
from datetime import datetime

import utilities as ut

class AnalyzeHours:

    def get_total_hours_open(self, hours: dict) -> dict:
        """Gets all hours open for all places."""
        hours = ut.delete_dne(hours)
        all_hours = {}
        for place in hours:
            total_hours = {place: 0}
            days = hours[place]
            for day, hour in days.items():
                # 0 means closed
                if hour != 0:
                    open = int(hour[0])
                    close = int(hour[1])
                    result = close - open
                    final_result = f"{result:04d}"
                    total_hours[place] = total_hours[place] + int(final_result[:2])
            # total_hours returns a dictionary that has every place name with hours open during the week
            all_hours[place] = total_hours[place]
        return all_hours

    def get_average_hours_open(self, hours: dict) -> list:
        """Get average hours open of all places."""
        all_hours = self.get_total_hours_open(hours)
        average = sum(value for value in all_hours.values()) / len(all_hours)
        per_day = average / 7
        avg = ("Average Hours Open", round(average, 2))
        per = ("Average Hours Per Day", round(per_day, 2))
        return  [avg, per]

    def get_most_hours_open(self, hours: dict) -> list:
        """Return list of places that are open the most during the week."""
        all_hours = self.get_total_hours_open(hours)
        most_hours = heapq.nlargest(5, all_hours.items(), key=lambda pair: pair[1])
        return most_hours

    def get_least_hours_open(self, hours: dict) -> list:
        """Return list of places that are open the least during the week."""
        all_hours = self.get_total_hours_open(hours)
        least_hours = heapq.nsmallest(5, all_hours.items(), key=lambda pair: pair[1])
        return least_hours

    def standardize_places_closed(self, data: dict) -> list:
        """Makes data into a list of tuples to make writing to word document easier."""
        list_tuples = []
        for day in data:
            one = day
            two = data[day]['days']
            three = ", ".join(data[day]['places'])
            list_tuples.append((one, two, three))
        return list_tuples

    def get_most_days_closed(self, hours: dict) -> list:
        """Returns list of days that have places closed on that day with places names."""
        days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        days_closed = {key: {"days": 0, "places": []} for key in days}
        hours = ut.delete_dne(hours)
        
        for place in hours:
            days = hours[place]
            for day in days:
                if days[day] == 0:
                    days_closed[day]['days'] = days_closed[day]['days'] + 1
                    days_closed[day]['places'].append(place)
        
        days_closed = {key: value for key, value in days_closed.items() if value['days'] != 0}
        return self.standardize_places_closed(days_closed)

    def get_earliest_open_places(self, hours: dict) -> list:
        """Returns list of places open the earliest during the week."""
        hours = ut.delete_dne(hours)
        early_hours = {}
        for place in hours:
            total_hours = {place: 0}
            for day, hour in hours[place].items():
                if hour != 0:
                    open = ut.convert_time(hour[0])
                    total_hours[place] = open
            early_hours[place] = total_hours[place]

        early_hours = heapq.nsmallest(5, early_hours.items(), key=lambda pair: pair[1])
        return early_hours

    def get_latest_open_places(self, hours: dict) -> list:
        """Returns list of places open the latest during the week."""
        hours = ut.delete_dne(hours)
        late_hours = {}
        for place in hours:
            total_hours = {place: 0}
            for day, hour in hours[place].items():
                if hour != 0:
                    close = ut.convert_time(hour[1])
                    total_hours[place] = close
            late_hours[place] = total_hours[place]

        late_hours = heapq.nlargest(5, late_hours.items(), key=lambda pair: pair[1])
        return late_hours

    def analyze_hours_report(self, details: dict) -> list:
        """Function runs and returns all other functions as final report of hours."""
        details = ut.delete_non_operational_businesses(details)
        hours = {}
        for place in details:
            name = ut.get_name(details[place])
            address = ut.get_address(details[place])
            name = f'{name} ({",".join(address.split(",")[:-1])})'

            hours[name] = ut.get_opening_hours(details[place])
        
        always_open_places = []
        for place in hours: 
            if isinstance(hours[place], dict) and hours[place]['Sunday'] == ("2424", "2424"):
                always_open_places.append(place)
        
        for place in always_open_places:
            hours.pop(place)

        most_open_places = self.get_most_hours_open(hours)
        least_open_places = self.get_least_hours_open(hours)
        average_hour_open = self.get_average_hours_open(hours)
        most_days_closed = self.get_most_days_closed(hours)
        earliest_open_places = self.get_earliest_open_places(hours)
        latest_open_places = self.get_latest_open_places(hours)

        return [most_open_places, least_open_places, average_hour_open, most_days_closed, earliest_open_places, latest_open_places, always_open_places]
        # return [most_open_places, least_open_places, average_hour_open, most_days_closed, earliest_open_places, latest_open_places]
    