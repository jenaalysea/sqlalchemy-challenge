# Import the dependencies.

import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

engine = create_engine("sqlite:///...\sqlalchemy-challenge") 


# reflect the tables


# Save references to each table
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)




#################################################
# Flask Routes
#################################################
app = Flask(__name__)

engine = create_engine("sqlite:///...\sqlalchemy-challenge") 

Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# List all the available routes.
@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/temp-start/<start><br/>"
        f"/api/v1.0/temp-start-end/<start>/<end>"
    )

# Convert the query results from your precipitation analysis to a dictionary.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    latest_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    session.close()

    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
@app.route("/api/v1.0/temperature")
def temperature_observations():
    most_active_station_id = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    latest_date = session.query(func.max(Measurement.date)).scalar()
    last_date = datetime.strptime(latest_date, "%Y-%m-%d")
    one_year_ago = last_date - timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()

    session.close()

    temperature_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(temperature_data)

# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def temperature_stats(start, end=None):
    start_date = datetime.strptime(start, "%Y-%m-%d")

    if end:
        end_date = datetime.strptime(end, "%Y-%m-%d")
    else:
        end_date = session.query(func.max(Measurement.date)).scalar()

    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    session.close()

    temperature_stats_data = {
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }

    return jsonify(temperature_stats_data)

# For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
@app.route("/api/v1.0/temp-start/<start>")
def temperature_start_date(start):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start_date).all()

    session.close()

    temperature_start_data = {
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }
    return jsonify(temperature_start_data)

# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/temp-start-end/<start>/<end>")
def temperature_start_end_date(start, end):
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start_date, Measurement.date <= end_date).all()

    session.close()

    temperature_start_end_data = {
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2]
    }

    return jsonify(temperature_start_end_data)

if __name__ == "__main__":
    app.run(debug=True)