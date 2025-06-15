from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.orm import relationship
from ..db.database import BASE


class Station(BASE):
    __tablename__ = 'stations'

    # attributes
    id = Column(Integer, primary_key=True, autoincrement=True)
    line = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    station_name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    zip = Column(String, nullable=False)

    # relationships
    geographic_areas = relationship('StationsByGeographicArea', back_populates='station')


from .stations_by_geographic_area import StationsByGeographicArea
