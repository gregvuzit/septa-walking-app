from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from ..db.database import BASE


# Join table between GeographicArea and Station
class StationsByGeographicArea(BASE):
    __tablename__ = 'stations_by_geographic_areas'

    # attributes
    id = Column(Integer, primary_key=True, autoincrement=True)
    geographic_area_id = Column(Integer(), ForeignKey("geographic_areas.id"), nullable=False, index=True)
    station_id = Column(Integer(), ForeignKey("stations.id"), nullable=False, index=True)

    # relationships
    geographic_area = relationship("GeographicArea")
    station = relationship("Station")


from .geographic_area import GeographicArea
from .station import Station