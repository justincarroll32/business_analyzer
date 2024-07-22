import json
import os
from docx import Document
import pandas as pd
import numpy as np
import argparse
import data as gd
import heapq
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead

import utilities as ut

class Rating:

    def get_average_rating(self, details: dict) -> tuple:
        """Return average rating (out of 5) of all places."""
        total = 0
        for place in details:
            rating = ut.get_rating(details[place])
            if rating != "DNE":
                total = total + float(rating)
        
        return (len(details), round((total / len(details)), 2))
    
    def analyze_ratings(self, details: dict, flag: str) -> list:
        """Return either 5 good or bad reviews from places."""
        threshold = 2
        if flag == "bad":
            threshold = 3
        
        total_ratings = []
        for place in details:
            total_ratings = total_ratings + ut.get_reviews(details[place])
        
        if flag == "bad":
            ratings = [(rating, text) for rating, text in total_ratings if rating < threshold]
            # one_stars = [(rating, text) for rating, text in ratings if rating == 1]
            suggestions = []

            for rating in ratings:
                if len(ratings) < 5:
                    suggestions.append(rating[1])
                else:
                    suggestions.append(rating[1])

            # If the list is larger than 5, keep only the first 5 elements
            suggestions = suggestions[:5]
            return suggestions
        else:
            ratings = [(rating, text) for rating, text in total_ratings if rating > threshold]
            # five_stars = [(ratings, text) for rating, text in ratings if rating == 5]
            suggestions = []

            for rating in ratings:
                if len(ratings) < 5:
                    suggestions.append(rating[1])
                else:
                    suggestions.append(rating[1])

            # If the list is larger than 5, keep only the first 5 elements
            suggestions = suggestions[:5]
            return suggestions

    def rating_report(self, details: dict) -> list:
        """Return average ratings and good/bad reviews"""
        details = ut.delete_non_operational_businesses(details)
        average_rating = self.get_average_rating(details)
        bad_ratings = self.analyze_ratings(details, "bad")
        good_ratings = self.analyze_ratings(details, "good")

        return [average_rating, bad_ratings, good_ratings]