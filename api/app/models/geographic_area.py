from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..db.database import BASE


class GeographicArea(BASE):
    __tablename__ = 'geographic_areas'

    # attributes
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    # relationships
    stations = relationship('StationsByGeographicArea', back_populates='geographic_area')


from .stations_by_geographic_area import StationsByGeographicArea
