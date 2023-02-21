# jumpingminds-elevator-system

Django application for an elevator system.
The system can be initialized with the number of floors in a building and the number of elevators or lifts.

The live demo is hosted on render [here](https://jumpingminds-elevators-test.onrender.com/swagger/). This is the swagger API documentation page. Use the [API Guide](#api-guide) mentioned below to use the APIs.

## Project setup

To quickly setup locally:
- Clone the repository and go to the directory
- Setup a virtual environment and install dependencies from `requirements.txt`

        python -m venv .venv

        source .venv/bin/activate

        pip install --upgrade pip

        pip install -r requirements.txt

- Setup up a local PostgreSQL database and a user. Update the database credentials in `config/settings/dev` or setup using following commands to use the same credentials.
  - first run `psql postgres`

        postgres=# CREATE DATABASE myproject;

        postgres=# CREATE USER myprojectuser WITH PASSWORD 'password';
        
        postgres=# ALTER ROLE myprojectuser SET client_encoding TO 'utf8';

        postgres=# ALTER ROLE myprojectuser SET default_transaction_isolation TO 'read committed';

        postgres=# GRANT ALL PRIVILEGES ON DATABASE myproject TO myprojectuser;

        postgres=# \q

- Then migrate from django and the project can be run

        python manage.py makemigrations; python manage.py migrate

        python manage.py runserver


## API Guide

The project has **Swagger API Documentation** at `/swagger/`
  - i.e. at `localhost:8000/swagger/` or `https://jumpingminds-elevators-test.onrender.com/swagger/`


### APIs

**NOTE:**
All URLs must have trailing forward slash or the server will respond with a `404_NOT_FOUND`

- `/elevator-system/` 
  - POST - initialize the elevator system
    
        Request body example:
        {
            "floors": 10,
            "lifts": 3
        }
  - GET - get elevator system details
  - DELETE - delete the elevator system

- `/lift/`
  - GET - fetch list of lifts
- `/lift/id/`
  - GET - fetch details of specific lift
- `/lift/id/requests/`
  - GET - fetch all destination of specific lift
  - PATCH - choose destination floor from inside the lift

        Request body example:
        {
            "destination": 9
        }
- `/lift/id/door/`
  - GET - fetch the door status of specific lift
  - PATCH - open or close door of specific lift

        Request body example: (true -> open, false -> close)
        {
            "door": true
        }
- `/lift/id/maintenance`
  - PATCH - mark specific lift as out of order

        Request body example: (true -> out of order, false -> running)
        {
            "out_of_order": true
        }
- `/request/`
  - POST - request for lift at a specific floor

        Request body example: (true -> open, false -> close)
        {
            "floor": 7
        }

## Approach

There are mainly two objects: `ElevatorSystem` and `Lift`. The `ElevatorSystem` holds the number of floors and lifts in the system. 

The operations available are:
- initialize the system
- fetch current status of all lifts or that of individual lifts
- request for a lift at a particular floor
- open and close door of lifts
- choose destination of lift from inside the lift

REST APIs are built using `DjangoRestFramework` and `PostgreSQL` is used as database. 

### Assigning lifts to requests

The logic is implemented in `elevators/utils.py` using `assign_lift()` function that calls `get_lift_score()`
- Request comes from a specific floor (`/request/`)
- Each lift is given a score using `get_lift_score`. The process goes as follows:
  - The score is just the total distance traveled by a lift to reach the request floor. Example of distance: to reach from floor 7 to floor 2, the distance is 5; to go back to floor 19 now, distance is 2+17 = 19
  - If the floor from the request and current floor of a lift are the same, then score=0. the lift is assigned immediately
  - Else, if the floor lies in between two consecutive destinations of the lift, then the score would be the distance upto there.
  - If the floor is not in between any of the covered destinations, the score is the sum of all intermediate distances
- The lift with the least score is assigned to the request

### Updating destinations

The logic is implemented in `elevators/utils.py` using `update_destinations()`. This function is responsible for placing a new destination at the right position in the list of existing destinations of the lift
- If the new destination is the same as the current floor of the lift, return existing list of destinations
- If there are no pending destinations, append the floor to the list and return the list
- If the new destination comes in between two consecutive destinations of the lift, then place the new destination there and shift the other destinations that follow one position right.

### Lift movement
- The lift stores incoming requests from various without moving if the door is open.
- Once the door is closed, if there is one, the lift goes to the next destination and the door is opened. Else if there are no destinations, the lift door is closed and lift remains still.
- `get_lift_movement()` and `go_to_next_destination()` are implemented in `elevators/utils.py`

### Choosing destinations from inside the lift
- `/lift/id/request/`
- Request is made to go to a specific floor
- The new destination is added to the existing destinations of the lift using `update_destinations()`
- If the door is open, the door is closed and the lift goes to the next destination

### Project file structure
- The settings and other core files are present in the `config` directory
  - `settings` directory is inside `config`
  - `settings` is divided into `base.py`, `dev.py`, `prod.py`
  - `dev.py` has specific settings for local (development) version while `prod.py` has production settings 
  - `prod.py` is used when run with `gunicorn` and `dev.py` is used when run with `manage.py`
  - `gunicorn` cannot server static files by itself, so `nginx` must be setup. `nginx` acts as reverse-proxy and also serves static files
- The `elevators` directory contains the application files
  - `utils.py` contains helper functions to avoid repeating code (DRY) and cleaner code in `views.py`
  - `serializers.py` contains model serializers to serialize JSON to database format and deserialize vice versa.

  
## Deploy

The project can be containerized using the `Dockerfile`. It uses `entrypoint.sh` containing commands to be run.
There is also a `docker-compose.yml` file.

`docker build` and `docker run` can be used to build and run the image respectively. Or `docker-compose up --build` can be used to build and `docker compose up` to run
