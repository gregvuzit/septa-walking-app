from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.database import request_db
from app.services.location_service import LocationService

ApiRouter = APIRouter()

class Location(BaseModel):
    location_type: str
    latitude: float = None
    longitude: float = None
    address: str = None

def validate_coordinate(value, name, min_val, max_val):
    if value is not None:
        try:
            value = float(value)
            if not min_val <= value <= max_val:
                raise ValueError
            return value
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"{name} must be a valid number between {min_val} and {max_val}"
            )
    return value

@ApiRouter.post("")
async def nearest_station_with_walking_directions(
    location: Location,
    db: Session = Depends(request_db),
):
    if location.location_type == "address" and location.address is None:
        raise HTTPException(
            status_code=400, 
            detail="Address must be provided"
        )

    if location.location_type == "coordinates":
        if location.latitude is None or location.longitude is None:
            raise HTTPException(
                status_code=400, 
                detail="Latitude and longitude must be provided"
            )
    
        # Validate latitude and longitude values
        validate_coordinate(location.latitude, "Latitude", -90, 90)
        validate_coordinate(location.longitude, "Longitude", -180, 180)

    try:
        location_service = LocationService(db)
        origin_param = location.address if location.location_type == "address" else (location.latitude, location.longitude)
        # Is origin reasonably within SEPTA's coverage area? If not, return an error.
        validation_message = location_service.validate_origin_in_septa_area(origin_param)
        if validation_message:
            raise HTTPException(
                status_code=400,
                detail=validation_message
            )
        
        # Geocode origin and use that to find the geographic area that contains it.
        # For this, it will either be NJ, DE, or a county in PA (Delaware,
        # Montgomery, Chester, Bucks, or Philadelphia).
        origin_geocode = location_service.origin_geocode(location.location_type, origin_param)
        matching_searchable_area = location_service.origin_within(origin_geocode)

        # Get the closest station in the geographic area
        closest_station = location_service.shortest_walk_in_area(
            origin_param,
            matching_searchable_area
        )
        return {
            "station": location_service.station_to_geojson(closest_station),
            "directions": location_service.walking_directions(origin_param, closest_station),
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )