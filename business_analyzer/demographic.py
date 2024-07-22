import logging
import os
import tempfile
import requests
import ast
import json
from typing import Union

import matplotlib.pyplot as plt
logging.basicConfig(level=logging.INFO)

class Demographic:

    def state_lookup(self, data_lookup_flag: str, target_state: int, target_code: int, file: str) -> Union[int, str]:
        with open(file, "r") as f:
            data = json.load(f)

        for state in data:
            if data_lookup_flag == 'CODE':
                if state == target_state:
                    return data[state]['CODE']
            else:
                if target_code == data[state]['CODE']:
                    return state
        return 1029384756

    def county_lookup(self, data_lookup_flag: str, target_state: str, target_county: str, target_code: int, file: str) -> Union[int, str]:

        with open(file, "r") as f:
            data = json.load(f)
        counties = data[target_state]['COUNTIES']

        for county_name, code in counties.items():
            if data_lookup_flag == 'CODE':
                if county_name == target_county:
                    return code
            else:
                if code == target_code:
                    return county_name
        return 1029384756

    # done
    def get_request_data(self, url: str) -> Union[list, int]:
        """Access API data and interpret it literally to get dict or list."""
        response = requests.get(url)
        if response.status_code == 200:
            final = ast.literal_eval(response.text)
            return final
        else:
            return 0
    # done - used for getting population of intended api call
    def get_target_county_population(self, data: list) -> int:
        """Return population number with given data (same format everytime)"""
        if not isinstance(data, list):
            return data
        else:
            return data[1:][0][1]

    def add_up(self, data: dict) -> tuple:
        """Get remainder of population that is not accounted for (certain RACE/AGE codes not asked for)"""
        all = 0
        total = 0
        for key, value in data.items():
            if key == 'Total Population':
                all = int(value)
            else:
                total = total + int(value)

        return (all, total)

    def get_percents(self, data: dict, total: int) -> dict:
        """Get percentages for data and return dictionary of calculated percents."""
        data.pop('Total Population')
        percents = {}
        if total == 0:
            for key, value in data.items():
              percents[key] = 0
            return percents

        for key, value in data.items():
          percents[key] = round((float(int(value) / int(total))) * 100, 2)

        return percents

    def plot_demographic_data(self, demo_dict: dict, county_name: str, state_name: str, data_type: str) -> tuple:
        data = {key: int(value) for key, value in demo_dict.items()}
        percents = self.get_percents(data, data['Total Population'])
        labels = list(percents.values())

        legend_labels = []
        for key, percent in zip(list(percents.keys()), list(percents.values())):
            legend_labels.append(str(key) + ", " + str(percent))

        sizes = [value for value in data.values()]

        # Create the pie chart
        plt.figure(figsize=(10, 8))

        plt.pie(sizes, labels=labels, startangle=140)
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title(f'{data_type.capitalize()} Distribution for {county_name}, {state_name}')
        plt.legend(legend_labels, loc="upper right", bbox_to_anchor=(1.1,1.1))

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, str(data_type) + ".png")

        plt.savefig(temp_path)
        plt.close()

        return (temp_dir, temp_path)

    # done
    def get_demographic_data(self, target_state: int, target_county: int, filename: str) -> list:
        base_url = "https://api.census.gov/data/2019/pep/charagegroups"
        # urls for getting all data
        # get all race data for every county in given state

        state_name = self.state_lookup("NAME", "", target_state, filename)
        county_name = self.county_lookup("NAME", state_name, "", target_county, filename)

        race_codes = {'Total Population':0, 'White':1, 'Black':2, 'Native':3, 'Asian':4, 'Hawaiian':5}
        total_queries = len(race_codes)
        count_queries = 1
        # race_codes = {'Total Population': 0, 'White': 1}
        for key, value in race_codes.items():
            logging.info(f'Accessing United States Census Bureau data with RACE code {value}: Query {count_queries}/{total_queries}')
            count_queries = count_queries + 1
            population = self.get_request_data(f'{base_url}?get=NAME,POP&RACE={value}&for=county:{target_county}&in=state:{target_state}')
            final = self.get_target_county_population(population)
            race_codes[key] = final
        nums = self.add_up(race_codes)
        race_codes['Other'] = str(nums[0] - nums[1])


        # get all age group data
        age_codes = {'Total Population':0, 'Under 18': 19, '18-24':23, '24-44':24, '45-64':25}
        total_queries = len(age_codes)
        count_queries = 1
        for key, value in age_codes.items():
            logging.info(f'Accessing United States Census Bureau data with AGE code {value}: Query {count_queries}/{total_queries}')
            count_queries = count_queries + 1
            population = self.get_request_data(f'{base_url}?get=NAME,POP&AGEGROUP={value}&for=county:{target_county}&in=state:{target_state}')
            final = self.get_target_county_population(population)
            age_codes[key] = final

        nums = self.add_up(age_codes)
        age_codes['Above 64'] = str(nums[0] - nums[1])


        # # get all sex group data
        sex_codes = {'Total Population': 0, 'Male':1, 'Female':2}
        total_queries = len(sex_codes)
        count_queries = 1
        for key, value in sex_codes.items():
            logging.info(f'Accessing United States Census Bureau data with SEX code {value}: Query {count_queries}/{total_queries}')
            count_queries = count_queries + 1
            population = self.get_request_data(f'{base_url}?get=NAME,POP&SEX={value}&for=county:{target_county}&in=state:{target_state}')
            final = self.get_target_county_population(population)
            sex_codes[key] = final

        nums = self.add_up(sex_codes)
        sex_codes['Other'] = str(nums[0] - nums[1])

        races = self.plot_demographic_data(race_codes, county_name, state_name, 'race')
        ages = self.plot_demographic_data(age_codes, county_name, state_name, 'age')
        sexs = self.plot_demographic_data(sex_codes, county_name, state_name, 'sex')
        return [races, ages, sexs]

    def extract_migration_data(self, data: list) -> dict:
        if data == 0:
            return {'Domestic Migration': 0, 'International Migration': 0, 'Net Migration': 0}
        else:
            data = data[1]

            ndm = data[1]
            im = data[2]
            nm = data[3]

            return {'Domestic Migration': ndm, 'International Migration': im, 'Net Migration': nm}

    def plot_migration_data(self, data: dict, migration_key: str, target_state: str, target_county: str) -> tuple:

        place = f'{target_county}, {target_state}'
        x = [year for year in list(data.keys()) if data[year][migration_key] != 0]
        y = [float(data[year][migration_key]) for year in list(data.keys()) if data[year][migration_key] != 0]

        if len(x) == 1:
            between_years = [x[0]]
        elif len(x) == 0:
            between_years = []
        else:
            between_years = [x[0], x[-1]]

        fig, ax = plt.subplots()

        plt.figure(figsize=(10, 6))
        plt.plot(x, y, marker='o', linestyle='-', color='blue')

        plt.xlabel('Year')
        plt.ylabel(migration_key)

        if migration_key == 'Net Migration':
            plt.ylabel('Net Migration (thousands)')

        if len(between_years) == 0:
            plt.title(f'No Data Between Years 2010-2021 for {place}')
            plt.grid(True)

            plt.ylim(100, -100)
        elif len(between_years) == 1:
            plt.title(f'{migration_key} for {between_years[0]} for {place}')
            plt.grid(True)
            ax.autoscale(axis='y')
        else:
            plt.title(f'{migration_key} Between Years {between_years[0]}-{between_years[1]} for {place}')
            plt.grid(True)
            ax.autoscale(axis='y')

        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, str(migration_key) + ".png")

        plt.savefig(temp_path)
        plt.close()

        return (temp_dir, temp_path)

    def get_migration_data(self, target_state: int, target_county: int, filename: str) -> list:
        state_name = self.state_lookup("NAME", "", target_state, filename)
        county_name = self.county_lookup("NAME", state_name, "", target_county, filename)

        dsource='pep'
        dname='components'
        cols='COUNTY,DOMESTICMIG,INTERNATIONALMIG,RNETMIG,LASTUPDATE'
        years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021']
        years_data = {key: 0 for key in years}

        for year in years:
            base_url = f'https://api.census.gov/data/{year}/{dsource}/{dname}'
            data_url = f'{base_url}?get={cols}&for=county:{target_county}&in=state:{target_state}'
            logging.info(f'Accessing United States Census Bureau MIGRATION data for {year}')
            final = self.get_request_data(data_url)
            if final == 0:
                logging.info(f'No data for year {year}')
            migration_data = self.extract_migration_data(final)
            years_data[year] = migration_data
            # if 0 then there is no data for this year

        domestic = self.plot_migration_data(years_data, 'Domestic Migration', state_name, county_name)
        international = self.plot_migration_data(years_data, 'International Migration', state_name, county_name)
        net = self.plot_migration_data(years_data, 'Net Migration', state_name, county_name)


        return [domestic, international, net]

    def get_all_census_data(self, target_state: str, target_county: str) -> tuple:

        map_file = 'state_county_mapping.json'
        state_code = self.state_lookup('CODE', target_state, 00, map_file)
        county_code = self.county_lookup('CODE', target_state, target_county, 00, map_file)

        demographic_data = self.get_demographic_data(state_code, county_code, map_file)
        migration_data = self.get_migration_data(state_code, county_code, map_file)

        return (demographic_data, migration_data)
