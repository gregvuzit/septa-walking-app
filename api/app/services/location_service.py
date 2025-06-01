import googlemaps
import os
import xml.etree.ElementTree as ET
import zipfile
from functools import lru_cache
from itertools import islice
from lxml import etree, html

class LocationService():
    def __init__(self):
        self.gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))

        # TODO: stations should come from a database
        self.stations = []

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kml_file = os.path.join(base_dir, 'doc.kml')  # Assuming the KML file is named 'doc.kml'
        if not os.path.exists(kml_file):
            print('Extracting KML file from KMZ...')
            kmz_file = os.path.join(base_dir, 'SEPTARegionalRailStations2016.kmz')
            output_dir = base_dir
            self.__extract_kmz(kmz_file, output_dir)

        self.__parse_kml(kml_file)
        self.stations_by_searchable_area = self.__get_stations_by_searchable_area()
    

    ######    Private Methods    ######

    @lru_cache(maxsize=1)
    def __get_stations_by_searchable_area(self):
        """
        Cached version of stations by searchable area. The result will be cached after
        the first call and reused for subsequent calls.
        """
        return self.__build_stations_by_searchable_area(self.stations)

    def __build_stations_by_searchable_area(self, stations):
        """
        Break the stations down by categories based on geographic location. Only stations
        in the matching category for the input will be used for the destination list in the
        call to the distance matrix to keep costs down.
        """
        stations_by_searchable_area = {
            'NJ': [],
            'DE': [],
            'Bucks County': [],
            'Chester County': [],
            'Delaware County': [],
            'Montgomery County': [],
            'Philadelphia County': [],
        }

        for station in stations:
            if station['State'] == 'NJ':
                stations_by_searchable_area['NJ'].append(station)
            elif station['State'] == 'DE':
                stations_by_searchable_area['DE'].append(station)
            elif station['County'] == 'Bucks':
                stations_by_searchable_area['Bucks County'].append(station)
            elif station['County'] == 'Chester':
                stations_by_searchable_area['Chester County'].append(station)
            elif station['County'] == 'Delaware':   
                stations_by_searchable_area['Delaware County'].append(station)
            elif station['County'] == 'Montgomery':
                stations_by_searchable_area['Montgomery County'].append(station)
            elif station['County'] == 'Philadelphia':
                stations_by_searchable_area['Philadelphia County'].append(station)

            # Add stations close to county borders to the adjacent county for
            # a more thorough search
            if station['Station_Na'] in ['Link Belt', 'Somerton', 'Torresdale']:
                stations_by_searchable_area['Bucks County'].append(station)
            if station['Station_Na'] == 'Wayne':
                stations_by_searchable_area['Chester County'].append(station)
            if station['Station_Na'] in [
                'Strafford', 'Rosemont', 'Bryn Mawr', 'Haverford', 'Ardmore', 'Wynnewood', 'Angora',
                'Airport Terminal A', 'Eastwick'
            ]:
                stations_by_searchable_area['Delaware County'].append(station)
            if station['Station_Na'] in [
                'Lawndale', 'Cheltenham', 'Ryers', 'Fox Chase', 'Forest Hills', 'Somerton', 'Mount Airy',
                'Chestnut Hill East', 'Gravers', 'Wyndmoor', 'Manayunk', 'Overbrook', 'Villanova', 'Bala',
                'Cynwyd'
            ]:
                stations_by_searchable_area['Montgomery County'].append(station)
            if station['Station_Na'] in [
                'Miquon', 'Melrose Park', 'Bethayres', 'Philmont', 'Trevose', 'Eddington'
            ]:
                stations_by_searchable_area['Philadelphia County'].append(station)

        return stations_by_searchable_area
    
    def __chunked_iterable(self, iterable, size):
        """Yield successive chunks of a given size from an iterable."""
        it = iter(iterable)
        while chunk := list(islice(it, size)):
            yield chunk

    def __extract_kmz(self, kmz_file, output_dir):
        '''
        Unzip kmz and extract underlying files
        '''
        with zipfile.ZipFile(kmz_file, 'r') as kmz:
            kmz.extractall(output_dir)

    def __parse_kml(self, kml_file):
        '''
        Extract relevant station data from kml file and put it in a more easily
        utilizable object format
        '''
        tree = ET.parse(kml_file)
        root = tree.getroot()
        # Namespace handling
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        for c, placemark in enumerate(root.findall('.//kml:Placemark', ns)):
            description = placemark.find('.//kml:description', ns).text.replace('<![CDATA[', '').replace(']]>', '')
            
            # Convert description text string to HTML then convert back to XML to parse it
            html_element = html.fromstring(description)
            xml_string = etree.tostring(html_element, encoding='unicode', method='xml', pretty_print=True)
            description_xml = ET.fromstring(xml_string)
            station_info = {
                'Name': None,
                'Latitude': None,
                'Longitude': None,
                'Station_Na': None,
                'Street_Add': None,
                'City': None,
                'State': None,
                'Zip': None,
                'County': None,
            }
            if description_xml is not None:
                items = list(description_xml.iter())
                for i, subelement in enumerate(items):
                    if subelement.text is not None and subelement.text in list(station_info.keys()):
                        station_info[subelement.text] = items[i + 1].text

            station_info['Name'] = placemark.find('kml:name', ns).text
            self.stations.append(station_info)

    def __station_coordinates(self, station):
        """Return the coordinates of a station as a tuple."""
        lat = station['Latitude']
        lon = station['Longitude']
        return (lat, lon)


    ######    Public Methods    ######

    def origin_geocode(self, location_type, origin):
        """
        Returns geocode result for a given origin.
        """
        if location_type == 'coordinates':
            return self.gmaps.reverse_geocode(
                origin, location_type=['ROOFTOP', 'GEOMETRIC_CENTER', 'RANGE_INTERPOLATED']
            )
        else:
            # Use a bounding box that corresponds to SEPTA's service area to limit the
            # search area for the address
            bounds = {
                'southwest': {'lat': 39.662903, 'lng': -75.794681},
                'northeast': {'lat': 40.367891, 'lng': -74.659266}
            }
            return self.gmaps.geocode(origin, bounds=bounds)
        
    def origin_within(self, geocode_result):
        """
        Extract state and county from geocode result
        """
        state = None
        county = None
        for component in geocode_result[0]['address_components']:
            if 'administrative_area_level_1' in component['types']:
                state = component['short_name']
            if 'administrative_area_level_2' in component['types']:
                county = component['long_name']
        
        # Return state if NJ or DE, otherwise return county
        if state in ['NJ', 'DE']:
            return state
        return county
        
    def shortest_walk_in_area(self, location, matching_searchable_area):
        """
        Get the station with shortest walk to location. Break up stations
        into chunks of 25 and call Google Maps Distance Matrix API to find
        the shortest walk. 
        """
        # Initialize variables to track the closest destination
        closest_destination = None
        min_distance = 0
        stations = self.stations_by_searchable_area[matching_searchable_area]
        distance_miles = 0
        time = None

        # Process destinations in chunks of 25. This is the limit for the
        # distance matrix API.
        for chunk in self.__chunked_iterable(stations, 25):
            matrix = self.gmaps.distance_matrix(
                location,
                [self.__station_coordinates(station) for station in chunk],
                units='imperial',
                mode='walking',
            )
            for i, row in enumerate(matrix['rows'][0]['elements']):
                if row['status'] == 'OK':  # Ensure the API returned a valid result
                    distance = row['distance']['value']  # Distance in meters
                    # print(f"{chunk[i]['Station_Na']}: {distance} meters")

                    if closest_destination is None or distance < min_distance:
                        # print(f"New shortest destination found: {chunk[i]['Station_Na']} with distance {distance} meters")
                        min_distance = distance
                        closest_destination = chunk[i]
                        distance_miles = row['distance']['text']
                        time = row['duration']['text']

        # Print the shortest destination and its distance
        # print(f"Closest destination: {closest_destination}, Distance: {min_distance} meters, Miles: {distance_miles}, Time: {time}")
        return closest_destination
    
    def station_to_geojson(self, station):
        """Convert a station dictionary to GeoJSON Feature format"""
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(station['Longitude']), float(station['Latitude'])]
            },
            "properties": {
                "name": station['Station_Na'],
                "address": station['Street_Add'],
                "city": station['City'],
                "state": station['State'],
                "zip": station['Zip'],
                "county": station['County']
            }
        }

    def validate_origin_in_septa_area(self, origin):
        """
        Checks if origin is at a reasonable distance in SEPTA's service area.
        Returns a message for graceful error handling if not.
        """
        # Check if the coordinates are within 74000 meters of Suburban Station.
        # This is the distance from Suburban Station to the furthest station in the
        # dataset, Newark, DE (69156), plus the distance in meters for around a 20
        # minute walk, which is a reasonable upper limit.
        suburban_station = next(
            station for station
            in self.stations_by_searchable_area['Philadelphia County']
            if station['Station_Na'] == 'Suburban Station'
        )
        distance_from_suburban = self.gmaps.distance_matrix(
            self.__station_coordinates(suburban_station), origin
        )
        if distance_from_suburban['rows'][0]['elements'][0]['status'] == 'OK':
            distance = distance_from_suburban['rows'][0]['elements'][0]['distance']['value']
            if distance > 71000:
                # Anything outside this limit is too far for a walk to any station
                return f"Sorry, {origin} is too far from any stations to walk. Please try again."
        else:
            # If the result is not OK, then this means there is no viable route, ie,
            # they entered a location in the middle of the ocean or on another continent, etc
            return f"Sorry, no viable route for walking can be found for {origin}. Please try again."
        
        return None

    def walking_directions(self, origin, closest_station):
        """
        This method will return walking directions to a given station.
        """
        directions = self.gmaps.directions(
            origin,
            self.__station_coordinates(closest_station),
            mode='walking',
            units='imperial',
        )
        direction_steps = [
            {
                'instruction': step['html_instructions'],
                'distance': step['distance']['text'],
            } for step in directions[0]['legs'][0]['steps']
        ]
        return direction_steps