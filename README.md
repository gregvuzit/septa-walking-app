# SEPTA Walking App

A Python project built on FastAPI that utilizes the Google Maps API to return walking directions to the nearest SEPTA Regional Rail station. It will accept as input either a set of latitude/longitude coordinates or a valid text address for GMaps (ex: '1600 Market St, Philadelphia, PA', 'Philadelphia Museum of Art', etc). It should accept coordinates from anywhere, but will only return a valid match and successful response if reasonably within SEPTA's coverage area, otherwise it will return an error response with a message detailing the problem.

This is meant for demonstration purposes only, and should by no means be assumed to be 100% accurate in every case (the station list is a few years out of date), especially for cases close to the limits of SEPTA's coverage.

## Prerequisites

1. Python 3 - <https://www.python.org/downloads/>
2. Docker - <https://www.docker.com/>
3. A Google Maps API Key - <https://developers.google.com/maps/documentation/javascript/get-api-key>
4. Node - <https://nodejs.org/en>
5. NPM - <https://www.npmjs.com/>

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd septa-walking-app
   ```

2. Create an `.env` and `test.env` file in the root of the `api` directory. Insert your Google Maps API Key in both like this:
```
GOOGLE_API_KEY=<YOUR GOOGLE KEY HERE>
```

3. Run Docker Compose
   ```
   docker-compose up --build
   ```

## Usage

The application will spin up two Docker containers:

1. api
2. frontend

### API

The backend API container runs a FastAPI application with an endpoint to query Google Maps. On startup, a `doc.kml` file containing the relevant geographical data for SEPTA stations is extracted from the `SeptaRegionalRailStations2016.kmz` file. The stations are further grouped together in code by geographic area for more efficient querying (Google charges for each location queried, so the less locations queried, the better from a cost standpoint.)

By default, the endpoint will be available at `http://127.0.0.1:8000/api`.

Swagger documentation is available at `http://127.0.0.1:8000/docs`.

The endpoint takes a json payload in one of two forms.

1. Address

```
{
   "location_type": "address",
   "address": "1 Test St, Philadelphia, PA"
}
```

or

2. Coordinates

```
{
   "location_type": "coordinates",
   "latitude": 40.004817,
   "longitude": -75.287184
}
```

### Frontend

This container runs a very basic React application with a simple form for sending requests to the API endpoint, which will also show the results for a request.

The form will be available at `http://localhost:3000/` on startup.

### Testing

A suite of pytest tests is located in `api/tests/test_api_router.py`. These tests all run a variety of various scenarios against the api endpoint. WARNING: These tests utilize the actual Google Maps API calls so you must have a `test.env` file setup with your Google API Key as detailed above for them to work properly.

To run, make sure the api container is running. Then from the root directory of the repo: `docker-compose exec api pytest`

## TODOs

1. Set up Postgres db and Alembic/SQLAlchemy setup to store station data in the db. Create a seed file to populate the stations table on first app startup.
2. Possibly create Terraform script for deployment to AWS. Use Redis for caching station data and RDS or DyanamoDB for the table.

## License

This project is licensed under the MIT License.