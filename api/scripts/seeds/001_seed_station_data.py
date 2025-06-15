import os
import xml.etree.ElementTree as ET
import zipfile
from lxml import etree, html

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.geographic_area import GeographicArea
from app.models.station import Station
from app.models.stations_by_geographic_area import StationsByGeographicArea

def request_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

db = next(request_db())

def create_geographic_area(db: Session, name: str):
    """
    Create new GeographicArea with given info and persist to DB.
    """
    geographic_area = db.query(GeographicArea).filter(GeographicArea.name == name).first()
    if geographic_area:
        pass
    else:
        geographic_area = GeographicArea(name=name)
        db.add(geographic_area)
    db.commit()
    db.refresh(geographic_area)
    return geographic_area

def create_or_update_station(db: Session, kwargs: dict):
    """
    Create new Station with given info and persist to DB.
    """
    station = db.query(Station).filter(Station.station_name == kwargs['station_name']).first()
    if station:
        station.line = kwargs['line']
        station.latitude = kwargs['latitude']
        station.longitude = kwargs['longitude']
        station.address = kwargs['address']
        station.city = kwargs['city']
        station.state = kwargs['state']
        station.zip = kwargs['zip']
    else:
        station = Station(**kwargs)
        db.add(station)
    db.commit()
    db.refresh(station)
    return station

def create_station_by_geographic_area(
    db: Session, geographic_area_id: int, station_id: int
):
    """
    Create new StationsByGeographicArea with given info and persist to DB.
    """
    sbga = db.query(StationsByGeographicArea).filter(
        StationsByGeographicArea.geographic_area_id == geographic_area_id,
        StationsByGeographicArea.station_id == station_id
    ).first()
    if sbga:
        pass
    else:
        sbga = StationsByGeographicArea(
            geographic_area_id=geographic_area_id, station_id=station_id
        )
        db.add(sbga)
    db.commit()
    db.refresh(sbga)
    return sbga

def extract_kmz(kmz_file, output_dir):
    '''
    Unzip kmz and extract underlying files
    '''
    with zipfile.ZipFile(kmz_file, 'r') as kmz:
        kmz.extractall(output_dir)

def parse_kml(db, kml_file):
    '''
    Extract relevant station data from kml file and add it to Stations table.
    Also create StationsByGeographicArea entries based on station's county or
    just state if in NJ or DE.
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
        # Transform station_info to new format
        station_for_db = {
            'line': station_info['Name'],
            'station_name': station_info['Station_Na'],
            'latitude': station_info['Latitude'],
            'longitude': station_info['Longitude'],
            'address': station_info['Street_Add'],
            'city': station_info['City'],
            'state': station_info['State'],
            'zip': station_info['Zip']
        }
        # Save station to db
        station = create_or_update_station(db, station_for_db)

        # Save station in its corresponding geographic area
        if station.state == 'NJ' or station.state == 'DE':
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == station.state).first()
        else:
            # Use counties if in PA
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == station_info['County']).first()

        create_station_by_geographic_area(db, geographic_area.id, station.id)

        # Add stations close to county borders to the adjacent county for
        # a more thorough search
        if station.station_name in ['Link Belt', 'Somerton', 'Torresdale']:
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == 'Bucks').first()
            create_station_by_geographic_area(db, geographic_area.id, station.id)
        if station.station_name == 'Wayne':
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == 'Chester').first()
            create_station_by_geographic_area(db, geographic_area.id, station.id)
        if station.station_name in [
            'Strafford', 'Rosemont', 'Bryn Mawr', 'Haverford', 'Ardmore', 'Wynnewood', 'Angora',
            'Airport Terminal A', 'Eastwick'
        ]:
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == 'Delaware').first()
            create_station_by_geographic_area(db, geographic_area.id, station.id)
        if station.station_name in [
            'Lawndale', 'Cheltenham', 'Ryers', 'Fox Chase', 'Forest Hills', 'Somerton', 'Mount Airy',
            'Chestnut Hill East', 'Gravers', 'Wyndmoor', 'Manayunk', 'Overbrook', 'Villanova', 'Bala',
            'Cynwyd'
        ]:
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == 'Montgomery').first()
            create_station_by_geographic_area(db, geographic_area.id, station.id)
        if station.station_name in [
            'Miquon', 'Melrose Park', 'Bethayres', 'Philmont', 'Trevose', 'Eddington'
        ]:
            geographic_area = db.query(GeographicArea).filter(GeographicArea.name == 'Philadelphia').first()
            create_station_by_geographic_area(db, geographic_area.id, station.id)


print('Seeding geographic areas...')
create_geographic_area(db, 'DE')
create_geographic_area(db, 'NJ')
create_geographic_area(db, 'Bucks')
create_geographic_area(db, 'Chester')
create_geographic_area(db, 'Delaware')
create_geographic_area(db, 'Montgomery')
create_geographic_area(db, 'Philadelphia')

# Extract kml from kmz to get station data
base_dir = os.path.dirname(os.path.abspath(__file__))
kml_file = os.path.join(base_dir, 'doc.kml')  # Assuming the KML file is named 'doc.kml'
if not os.path.exists(kml_file):
    print('Extracting KML file from KMZ...')
    kmz_file = os.path.join(base_dir, 'SEPTARegionalRailStations2016.kmz')
    output_dir = base_dir
    extract_kmz(kmz_file, output_dir)

print('Seeding stations from KML...')
parse_kml(db, kml_file)

