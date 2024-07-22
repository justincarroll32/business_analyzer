import requests
import ast
import json

def get_request_data(url):
    response = requests.get(url)
    status_code = response.status_code
    if status_code != 204:
        final = ast.literal_eval(response.text)
        return final
    else:
        return 1

def map(array):
    counties = {(county.split(",")[0]): code for county, state, code in array}
    return counties

def create_json():
    year = '2019'
    dsource = 'pep'
    dname = 'components'
    
    base_url = f'https://api.census.gov/data/{year}/{dsource}/{dname}'
    
    all_states = {}
    data_url = f'{base_url}?get=NAME&for=state:*'
    mapped_state_codes = (get_request_data(data_url))[1:]
    sorted_data = sorted(mapped_state_codes, key=lambda x: int(x[1]))

    all_states = {state_name: {'CODE': state_code, 'COUNTIES': {}} for state_name, state_code in sorted_data}
    
    for state in all_states:
        
        code = all_states[state]['CODE']
        
        data_url = f'{base_url}?get=NAME&for=county:*&in=state:{code}'
        if get_request_data(data_url) == 1:
            print('NOT ENOUGH COUNTIES')
        else:
            counties = get_request_data(data_url)[1:]
            all_states[state]['COUNTIES'] = map(counties)
    
    file_name = 'state_county_mapping.json'

    with open(file_name, "w") as json_file:
        json.dump(all_states, json_file, indent=4)

    print('Written to json file.')
        
create_json()
