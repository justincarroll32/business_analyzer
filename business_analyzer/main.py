import json
import googlemaps
import argparse
import logging
from pathlib import Path

import data as gd
import utilities as ut
from mapper import Mapper
from hours import AnalyzeHours
from servings import AnalyzeServing
from rating import Rating
from demographic import Demographic
from write_document import WriteDocument

def get_parser():
    """Get arguments needed to run whole function."""
    parser = argparse.ArgumentParser()

    parser.add_argument("-k", "--api_key_filename", help='API key filename', type=str, required=False)
    parser.add_argument("-l", "--location", help='Name of place i.e. a town or city', type=str, required=False)
    parser.add_argument("-r", "--radius", help='Radius in which to look for', type=int, required=False)
    parser.add_argument("-t", "--type", help='Type of business to look for', type=str, required=False)
    parser.add_argument("-c", "--county", help='County to research but must be in state', type=str, required=False)
    parser.add_argument("-s", "--state", help='State to research', type=str, required=False)
    args = parser.parse_args()
    return args.api_key_filename, args.location, args.radius, args.type, args.county, args.state

def get_place_lat_lng(api_key: str, place_name: str):
    gmaps = googlemaps.Client(key=api_key)
    # Use the Geocoding API to get the latitude and longitude
    geocode_result = gmaps.geocode(place_name)

    if geocode_result:
        latitude = geocode_result[0]['geometry']['location']['lat']
        longitude = geocode_result[0]['geometry']['location']['lng']
        return (float(latitude), float(longitude))
    else:
        return 1

def get_all_lats_lngs(data: dict):
    place_coordinates = []
    for place in data:
        place_coordinates.append(ut.get_exact_location(data[place]))

    return place_coordinates

def main() -> None:
    """
    This is the main function for the business analyzer.
    Enter a valid .txt file that has your Google API key, location (example: Kings Park, New York), radius (in meters)
    business type, county within the US, and state within the US.
    """
    logging.basicConfig(level=logging.INFO)

    api_key_filename, location, radius, business_type, county, state = get_parser()
    api_key = str(ut.get_google_api_key(str(api_key_filename)))
    location = str(location)
    radius = int(radius)
    business_type = str(business_type)
    county = str(county)
    state = str(state)

    create_mapping = Mapper()
    analyze_hours = AnalyzeHours()
    analyze_servings = AnalyzeServing()
    analyze_ratings = Rating()
    analyze_demographics = Demographic()
    write_to_document = WriteDocument()
    # comment these out to stop calling api and write to json file
    coordinates = get_place_lat_lng(api_key, location)

    if coordinates == 1:
        print('Please enter valid location.')
        exit()

    logging.info('Analyzing demographic trends and data')
    demos = analyze_demographics.get_all_census_data(state, county)

    # get place details using data.py and write to json file
    details = gd.main(str(api_key), coordinates, radius, business_type)
    county = county.replace(" ", "_")
    json_filename = Path("json_files") / Path(f'{county}_{state}_{business_type}.json')
    with open(json_filename, 'w') as file:
        json.dump(details, file, indent=4)
    data = {}
    with open(json_filename, "r") as file:
        data = json.load(file)

    points = get_all_lats_lngs(data)

    logging.info('Creating visual of places')
    visual_map = create_mapping.create_map(coordinates, points, location, business_type, 14)

    logging.info('Analyzing hours')
    hours = analyze_hours.analyze_hours_report(data)

    logging.info('Analyzing servings')
    servings = analyze_servings.analyze_serving_report(data)

    logging.info('Analyzing ratings')
    ratings = analyze_ratings.rating_report(data)

    logging.info('Writing to word document')
    output_doc = Path("analysis_docs") / Path(f'{location.replace(", ", "_")}_{business_type}.docx')
    write_to_document.write_to_document(output_doc, visual_map, str(ut.convert_meters_to_miles(radius)), business_type.capitalize(),
                        location, county, hours, ratings, servings, demos)

    logging.info(f'Successfully written to document: {output_doc}')

    return 0

# example command:
# python3 main.py -k key.txt -l "Albany, New York" -r 4000 -t cafe -c "Albany County" -s "New York"
if __name__ == '__main__':
    main()