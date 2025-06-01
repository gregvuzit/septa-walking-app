# SEPTA Walking App

A Python project built on FastAPI that utilizes the Google Maps API to return walking directions to the nearest SEPTA Regional Rail station. It will accept as input either a set of latitude/longitude coordinates or a valid text address for GMaps (ex: '1 Test St, Philadelphia, PA', 'Philadelphia Museum of Art', etc). It should accept coordinates from anywhere, but will only return a valid match if reasonably within SEPTA's coverage area, otherwise it will return a message saying it was not possible to determine a route.

This is meant for demonstration purposes only, and should by no means be assumed to be 100% accurate in every case, especially for cases close to the limits of SEPTA's coverage.

## Prerequisites

1. Python 3 - <https://www.python.org/downloads/>
2. Docker - <https://www.docker.com/>
3. A Google Maps API Key - <https://developers.google.com/maps/documentation/javascript/get-api-key>


## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fastapi-project
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

The application will spin up a Docker container that runs a FastAPI application with an
endpoint to query Google Maps.

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

TODO: Detail tests

## TODOs

1. Set up Postgres db and Alembic/SQLAlchemy setup to store station data in the db. Create a seed file to populate the stations table on first app startup.
2. A rudimentary React frontend app with a simple interface to call the endpoint and see formatted walking directions
3. Possibly create Terraform script for deployment to AWS. Use Redis for caching station data and RDS or DyanamoDB for the table.

## License

This project is licensed under the MIT License.