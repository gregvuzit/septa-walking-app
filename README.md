# SEPTA Walking App

A Python project built on FastAPI that utilizes the Google Maps API to return walking directions to the nearest SEPTA Regional Rail station. It will accept as input either a set of latitude/longitude coordinates or a valid text address for GMaps (ex: '1600 Market St, Philadelphia, PA', 'Philadelphia Museum of Art', etc). It should accept coordinates from anywhere, but will only return a valid match and successful response if reasonably within SEPTA's coverage area, otherwise it will return an error response with a message detailing the problem.

This is meant for demonstration purposes only, and should by no means be assumed to be 100% accurate in every case (the station list is a few years out of date), especially for cases close to the limits of SEPTA's coverage.

## Prerequisites

1. Docker - <https://www.docker.com/>
2. A Google Maps API Key - <https://developers.google.com/maps/documentation/javascript/get-api-key>

Nothing else is necessary for a local deployment, as everything needed for the app to work will be setup and managed within the Docker containers. However, if you'd like to do local development on your own environment, you will need the following as well.

For the backend:

Python 3 - <https://www.python.org/downloads/>

For the frontend:

- Node - <https://nodejs.org/en>
- NPM - <https://www.npmjs.com/>

For the database:

Postgres - <https://www.postgresql.org/>

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd septa-walking-app
   ```

2. Create an `.env` and `test.env` file in the root of the `api` directory. Both will include your Google Maps API Key. For .env:

   ```
   GOOGLE_API_KEY=<YOUR GOOGLE KEY HERE>
   DATABASE_URL=postgresql://postgres:postgres@db/septa_walking_app
   CORS_ORIGINS=http://localhost:3000
   ```

And for test.env:

   ```
   GOOGLE_API_KEY=<YOUR GOOGLE KEY HERE>
   DATABASE_URL=postgresql://postgres:postgres@db/septa_walking_app
   ```


3. Run Docker Compose (all commands from the root directory of the repository)
   ```
   docker-compose up --build
   ```

4. Set up database
   ```
   docker-compose exec api alembic upgrade head 
   ```

5. Seed station data
   ```
   docker-compose exec api bash ./scripts/run_seeds.sh
   ```


## Usage

The application will spin up three Docker containers:

1. api
2. frontend
3. db

### API

The backend API container runs a FastAPI application with an endpoint to query Google Maps. After initializing the database, running the seed file `api/scripts/seeds/001_seed_station_data.py` will extract a `doc.kml` file containing the relevant geographical data for SEPTA stations from the `SeptaRegionalRailStations2016.kmz` file.
The seed script will seed this station data into the database, along with setting up groupings for the stations by the geographic areas they are within and, for stations near geographic borders, nearby.

This grouping allows for more efficient querying (Google charges for each location queried, so the less locations queried, the better from a cost standpoint) by only searching the stations in the group of the geographic area that a request address/coordinates lie within.

The station data will be loaded into application memory one time only on the first
API request and then cached. All subsequent requests as long as the application remains up should utilize the cache for an efficient response.

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

## Terraform Deployment to AWS

The `infra` directory contains a suite of Terraform scripts to deploy the application to AWS, utilizing ECS and RDS. See the README located there for setup instructions.

## License

This project is licensed under the MIT License.