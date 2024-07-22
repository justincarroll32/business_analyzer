import time
import googlemaps
import requests

def store_all_keys(dictionary: dict, result_dict: dict, parent_key=""):
    """Format all keys into neater format."""
    for key, value in dictionary.items():
        new_key = parent_key + "." + key if parent_key else key
        result_dict[new_key] = value
        if isinstance(value, dict):
            store_all_keys(value, result_dict, new_key)

def get_all_place_ids(data: dict):
    """Return all place ids into a list."""
    place_ids = []
    for place in data:
        if place['place_id'] not in place_ids:
            place_ids.append(place['place_id'])

    return place_ids

def get_details(key, place_id):
    """Return all details for each place."""
    url = f'https://maps.googleapis.com/maps/api/place/details/json?key={key}&place_id={place_id}'
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200 and data['status'] == 'OK':
        place_details = data['result']
        return place_details
    else:
        print('Failed to retrieve place details.')
        return None

def get_place_details_per_place(api_key: str, location: str, radius: int, type: str):
    """Call Google Places API and get all data."""
    gmaps = googlemaps.Client(key=api_key)
    places = gmaps.places_nearby(location=location, radius=radius,
                                 open_now=False, type=type)
    time.sleep(5)
    next_places = gmaps.places_nearby(page_token=places['next_page_token'])
    results = places['results']
    next_results = next_places['results']
    for place in next_results:
        results.append(place)

    place_ids = get_all_place_ids(results)

    all_details = {key: 0 for key in place_ids}
    for id in place_ids:
        result = {}
        details = get_details(api_key, id)
        store_all_keys(details, result)
        all_details[id] = result

    return all_details

def check_and_add(data, key):
    """Format data to custom tag for not defined instead of Google defined label."""
    if key not in data:
        data[key] = "DNE"
    return data

def get_unique_keys(list_of_dicts: list) -> list:
    """Return all unique keys in data."""
    all_keys = set().union(*list_of_dicts)
    common_keys = set.intersection(*[set(d.keys()) for d in list_of_dicts])
    unique_keys = all_keys - common_keys
    return list(unique_keys)

def standardize_data(data):
    """Make data uniform by reformatting and cleaning."""
    lst = [value for key, value in data.items()]
    adder = get_unique_keys(lst)

    data_copy = {}
    for place in data:
        for key in adder:
            check_and_add(data[place], key)
        data_copy[place] = data[place]

    return data_copy

def main(api_key: str, location: str, radius: int, type:str):
    """Main function to get all data and standardize it."""
    try:
        details = get_place_details_per_place(api_key, location, radius, type)
        details_standardized = standardize_data(details)
        return details_standardized
    except KeyError as error:
        print(error)
