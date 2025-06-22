import googlemaps
import os
from functools import lru_cache
from itertools import islice
from sqlalchemy.orm import Session
from app.models.geographic_area import GeographicArea

class LocationService():
    def __init__(self, db: Session):
        self.db = db
        self.gmaps = googlemaps.Client(key=os.getenv('GOOGLE_API_KEY'))
        self.stations_by_searchable_area = self.__get_stations_by_searchable_area()

    ######    Private Methods    ######

    @lru_cache(maxsize=1)
    def __get_stations_by_searchable_area(self):
        """
        Cached version of stations by searchable area. The result will be cached after
        the first call and reused for subsequent calls.
        """
        return self.__build_stations_by_searchable_area()

    def __build_stations_by_searchable_area(self):
        """
        Break the stations down by categories based on geographic location. Only stations
        in the matching category for the input will be used for the destination list in the
        call to the distance matrix to keep costs down.
        """
        stations_by_searchable_area = {}

        geographic_areas = self.db.query(GeographicArea).all()
        for geographic_area in geographic_areas:
            stations = []
            for station_in_ga in geographic_area.stations:
                station = station_in_ga.station
                stations.append({
                    'Line': station.line,
                    'Name': station.station_name,
                    'Latitude': station.latitude,
                    'Longitude': station.longitude,
                    'Address': station.address,
                    'City': station.city,
                    'State': station.state,
                    'Zip': station.zip,
                })

            stations_by_searchable_area[geographic_area.name] = stations

        return stations_by_searchable_area
    
    def __chunked_iterable(self, iterable, size):
        """Yield successive chunks of a given size from an iterable."""
        it = iter(iterable)
        while chunk := list(islice(it, size)):
            yield chunk

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
                county = component['long_name'].split()[0] # Remove 'County'
        
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

                    if closest_destination is None or distance < min_distance:
                        min_distance = distance
                        closest_destination = chunk[i]

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
                "name": station['Name'],
                "address": station['Address'],
                "city": station['City'],
                "state": station['State'],
                "zip": station['Zip']
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
            in self.stations_by_searchable_area['Philadelphia']
            if station['Name'] == 'Suburban Station'
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
