# CityZones Web

CityZones Web is a web interface for riskzones Python script.

## How to deploy

First of all, clone this repository into your server folder. After cloning, `cd` into the cloned repository and follow these steps:

First, create a Python 3 virtual environment.

`python3 -m venv venv`

Then activate the virtual environment.

`. venv/bin/activate`

Install the dependencies.

`python3 -m pip install flask flask-sqlalchemy flask-mysqldb python-dotenv flask-alembic`

Copy `.env.example` file and set the configuration for your server.

`cp .env.example .env`

To run CityZones Web you will need Passenger WSGI enabled in your server. Follow your HTTP daemon instructions to setup Passenger and finish the deployment.