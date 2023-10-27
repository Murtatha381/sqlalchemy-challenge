# Import the dependencies
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables from the database
Base.prepare(engine, reflect=True)

# Save the references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creating the session (link) from Python to the DB
Session = sessionmaker(bind=engine)
session = Session()

# Flask Setup
app = Flask(__name__)

# Landing Page:
@app.route("/")
def home():
    available_routes = {
        "Precipitation": "/api/v1.0/precipitation",
        "Stations": "/api/v1.0/stations",
        "Temperature Observations (TOBS)": "/api/v1.0/tobs",
        "Temperature Statistics (Start Date)": "/api/v1.0/<start>",
        "Temperature Statistics (Start & End Date)": "/api/v1.0/<start>/<end>"
    }
    return jsonify(available_routes)

# Precipitation Route:
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculating the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    # Querying precipitation data for the last 12 months
    results = (
        session.query(Measurement.date, Measurement.prcp)
        .filter(Measurement.date >= one_year_ago)
        .all()
    )

    # Converting the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    # Querying the list of stations
    results = session.query(Station.station).all()

    # Converting the query results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

# TOBS Route
@app.route("/api/v1.0/tobs")
def tobs():
    # Finding the most active station
    active_stations = (
        session.query(Measurement.station, func.count(Measurement.station))
        .group_by(Measurement.station)
        .order_by(func.count(Measurement.station).desc())
        .first()
    )

    most_active_station = active_stations[0]

    # Calculating the date one year ago from the most recent date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)).strftime("%Y-%m-%d")

    # Querying temperature observations for the most active station for the previous year
    results = (
        session.query(Measurement.date, Measurement.tobs)
        .filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago)
        .all()
    )

    # Converting the query results to a list of dictionaries
    temperature_data = [{"date": date, "tobs": tobs} for date, tobs in results]

    return jsonify(temperature_data)

# Start Date Route
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    # Defining query for temperature statistics based on start date
    results = (
        session.query(
            func.min(Measurement.tobs).label("min_temp"),
            func.avg(Measurement.tobs).label("avg_temp"),
            func.max(Measurement.tobs).label("max_temp"),
        )
        .filter(Measurement.date >= start)
        .all()
    )

    # Converting the query results to a dictionary
    temperature_stats_data = {
        "start_date": start,
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2],
    }

    return jsonify(temperature_stats_data)

# Start and End Date Route
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_start_end(start, end):
    # Defining query for temperature statistics based on start and end dates
    results = (
        session.query(
            func.min(Measurement.tobs).label("min_temp"),
            func.avg(Measurement.tobs).label("avg_temp"),
            func.max(Measurement.tobs).label("max_temp"),
        )
        .filter(Measurement.date >= start, Measurement.date <= end)
        .all()
    )

    # Converting the query results to a dictionary
    temperature_stats_data = {
        "start_date": start,
        "end_date": end,
        "min_temperature": results[0][0],
        "avg_temperature": results[0][1],
        "max_temperature": results[0][2],
    }

    return jsonify(temperature_stats_data)

if __name__ == "__main__":
    app.run(debug=True)
