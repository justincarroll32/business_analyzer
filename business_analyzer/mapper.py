import folium
from selenium import webdriver
from time import sleep
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)

class Mapper:
    def create_map(self, center: tuple, points: list, loco: str, business_type: str, zoom_factor: int):
        try:
            map_center = [center[0], center[1]]
            my_map = folium.Map(location=map_center, zoom_start=zoom_factor)

            marker_locations = points
            for location in marker_locations:
                folium.Marker(location=location, popup="Marker").add_to(my_map)

            html_file_path = f'{loco}_{business_type}_map.html'
            save_path = Path('.') / html_file_path
            my_map.save(save_path)

            driver = webdriver.Firefox()
            driver.get(f'file://{save_path.resolve()}')
            sleep(1)

            screenshot_filename = f'{loco}_{business_type}_map.png'
            maps_dir = Path('maps')
            maps_dir.mkdir(exist_ok=True)
            get_screenshot_path = maps_dir / screenshot_filename
            driver.get_screenshot_as_file(get_screenshot_path)

            driver.quit()

            return str(get_screenshot_path)
        except Exception as e:
            logging.info(f'ERROR: UNABLE TO CREATE VISUAL. {e}')
            return "1"
