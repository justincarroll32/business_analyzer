from datetime import datetime
import data as gd
import re
from math import radians, cos, sin, asin, sqrt

def delete_non_operational_businesses(details: dict) -> dict:
    """Returns rid of any businesses that API returns as 'CLOSED_TEMPORARILY' and returns new dictionary. """
    new_details = {}
    for key, value in details.items():
        if value['business_status'] != "CLOSED_TEMPORARILY":
            new_details[key] = value

    return new_details

def delete_dne(hours: dict) -> dict:
    """Deletes all DNEs from 'hours' data and returns new dictionary."""
    new_hours = {}
    for hour, value in hours.items():
        if value != 'DNE':
            new_hours[hour] = value
    return new_hours

def convert_time(military_time: datetime) -> str:
    """Converts military time into 12 hour time."""
    military_time_obj = datetime.strptime(military_time, '%H%M')
    twelve_hour_time = military_time_obj.strftime('%I:%M %p')
    return twelve_hour_time

def filter_out_chains(details: dict) -> dict:
    """Optional: can filter out major chains based on search, has to be specifed by user"""

    chains = ["McDonald's", "Dunkin'", "Panera Bread", "Starbucks", "Barnes & Noble"]
    new_details = {}
    for place in details:
        if gd.get_name(details[place]) not in chains:
            new_details[place] = details[place]

    return new_details

def convert_meters_to_miles(radius: float) -> float:
    """Converts meters to miles."""
    return round(radius / 1609, 2)

def validate_data_key(data: dict, key: str) -> str | list:
    """Makes sure that key exists in dictionary."""
    if key in data:
        return data[key]
    else:
        raise KeyError(f"Error: no {key} found.")

def get_business_status(data: dict) -> str | list:
    """Returns business_status value from data."""
    return validate_data_key(data, 'business_status')

def get_address(data: dict) -> str | list:
    """Returns formatted_address values from data."""
    return validate_data_key(data, 'formatted_address')

def get_phone_number(data: dict) -> str | list:
    """Returns formatted_phone_number values from data."""
    return validate_data_key(data, 'formatted_phone_number')

def get_delivery(data: dict) -> str | list:
    """Returns delivery values from data."""
    return validate_data_key(data, 'delivery')

def get_dine_in(data: dict) -> str | list:
    """Returns dine_in values from data."""
    return validate_data_key(data, 'dine_in')

def get_name(data: dict) -> str | list:
    """Returns name values from data."""
    return validate_data_key(data, 'name')

def get_place_id(data: dict) -> str | list:
    """Returns place_id values from data."""
    return validate_data_key(data, 'place_id')

def get_rating(data: dict) -> str | list:
    """Returns rating values from data."""
    return validate_data_key(data, 'rating')

def get_reservable(data: dict) -> str | list:
    """Returns reservable values from data."""
    return validate_data_key(data, 'reservable')

def get_meals(data: dict) -> str | list:
    """Returns serves_breakfast, serves_lunch, serves_brunch, and serves_dinner values from data."""
    return [validate_data_key(data, 'serves_breakfast'), validate_data_key(data, 'serves_lunch'), validate_data_key(data, 'serves_brunch'), validate_data_key(data, 'serves_dinner')]

def get_beer(data: dict) -> str | list:
    """Returns serves_beer values from data."""
    return validate_data_key(data, 'serves_beer')

def get_types(data: dict) -> str | list:
    """Returns types value from data."""
    return validate_data_key(data, 'types')

def get_website(data: dict) -> str | list:
    """Returns website value from data."""
    return validate_data_key(data, 'website')

def get_wine(data: dict) -> str | list:
    """Returns serves_wine value from data."""
    return validate_data_key(data, 'serves_wine')

def get_vegetarian(data: dict) -> str | list:
    """Returns serves_vegatarian_food value from data."""
    return validate_data_key(data, 'serves_vegetarian_food')

def get_price_level(data: dict) -> str | list:
    """Returns price_level value from data."""
    return validate_data_key(data, 'price_level')

def get_takeout(data: dict) -> str | list:
    """Returns takeout value from data."""
    return validate_data_key(data, 'takeout')

def get_wheelchair_accessible(data: dict) -> str | list:
    """Returns wheelchair_accessible_entrance value from data."""
    return validate_data_key(data, 'wheelchair_accessible_entrance')

def get_opening_hours(data: dict) -> dict:
    """Returns opening_hours from data if exists and formats data."""
    try:
        open_close = validate_data_key(data, 'opening_hours.periods')
        if open_close == "DNE":
            return "DNE"
    except KeyError as error:
        print(error)


    days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    final_times = {index: 0 for index in range(0,7)}

    for time in open_close:
        if len(time) == 1:
            final_times[time['open']['day']] = ("2424", "2424") # means that place is open 24/7
        else:
            open = time['open']['time']
            close = time['close']['time']
            final_times[time['close']['day']] = (open, close)
    # maps day titles to numbers
    final_times = {day: final_times[key] for day, key in zip(days, range(0,7))}
    return final_times

def get_zip_code(address) -> str:
    """Returns zip code from address from data."""
    address_list = address.split(",")
    zip = re.sub(r'\D', '', address_list[2])
    return zip

def get_reviews(data: dict) -> dict:
    """Returns reviews values from data and formats into new dictionary."""
    try:
        reviews = validate_data_key(data, 'reviews')
    except KeyError as error:
        print(error)


    full_reviews = []
    for review in reviews:

        if isinstance(review, dict):
            complete = (review['rating'], review['text'])
            full_reviews.append(complete)

    return full_reviews

def get_distance_in_miles(location1: list, location2: list) -> float:
    """Returns distance in miles given latitude and longitude."""
    lon1 = radians(location1[1])
    lon2 = radians(location2[1])
    lat1 = radians(location1[0])
    lat2 = radians(location2[0])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    radius_earth = 3956

    return (c * radius_earth)

def get_exact_location(data: dict) -> tuple:
    """Returns geometry.location values from data."""
    try:
        geometry = validate_data_key(data, 'geometry.location')
    except KeyError as error:
        print(error)

    lat = geometry['lat']
    lng = geometry['lng']

    return (lat, lng)

def get_google_api_key(file: str) -> str:
    """Read text file for Google API key."""
    with open(file, "r") as file:
        return (file.readlines())[0]