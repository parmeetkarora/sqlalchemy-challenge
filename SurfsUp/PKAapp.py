# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import os
import json
from flask import Flask
from sqlalchemy.orm import sessionmaker 
from datetime import datetime

#################################################
# Database Setup
#################################################

app = Flask(__name__)

@app.route('/data')
def get_data():
    data = {"key": "value"}
    return json.dumps(data)

os.chdir(os.path.dirname(__file__))


# Create an engine
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# reflect the tables
measurement = Base.classes.measurement
station = Base.classes.station


# Save references to each table
try:
    Measurement = Base.classes.measurement
    Station = Base.classes.station
except AttributeError as e:
    print(f"Error: {e}. Available tables are: {Base.classes.keys()}")



# Create our session (link) from Python to the DB

session = Session(engine)
#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return(
        f"Available Routes:<br/>"
        f'Precipitaion data for the past year: /api/v1.0/precipitation <br/>'
        f'List of the stations: /api/v1.0/stations <br/>'
        f'Temperature for the past year: /api/v1.0/tobs <br/>'
        f'Find min, max, and avg temperature from a certain date: /api/v1.0/<start>'
        f'Find min, max, and avg temperature for specified start and end date: /api/v1.0/<start>/<end>'
    )
# for precipitation
import datetime as dt
@app.route('/api/v1.0/precipitation')
def precipitation():
    """Precipitation Data for One year Ago"""
    # Calculate the date one year ago from the last data point in the database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

    # Query for the last year of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}
# Return a JSON list of the calculated values
    return jsonify(precipitation_data)

# for stations
@app.route('/api/v1.0/stations')
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query for the list of stations
    """List of active Weather stations in Hawaii"""
    results = session.query(Station.station).all()
    session.close()
    stations_data = [station for station, in results]
    station_dict = {i: stations_data[i] for i in range(0, len(stations_data))}
# Return a JSON list of the calculated values
    return jsonify(station_dict)


# For temps
@app.route('/api/v1.0/tobs')
def tobs():
    """Temperatures of the most active station"""
    session = Session(engine)

# Query for the most active station
    most_active_station = session.query(Measurement.station).group_by(Measurement.station).order_by(func.count().desc()).first()[0]
# Calculate the date one year ago from the last data point for the most active station
    last_date = session.query(Measurement.date).filter(Measurement.station == most_active_station).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    one_year_ago = last_date - dt.timedelta(days=365)

#Set up query to get temperature

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station, Measurement.date >= one_year_ago).all()
    session.close()

    tobs_results = []

    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        tobs_results.append(temp_dict)
# Return a JSON list of the calculated values
    return jsonify(tobs_results)


from sqlalchemy import create_engine, func, exists
from sqlalchemy.orm import Session
import re
from datetime import datetime

# For start date (search by putting date format e.g 2016-08-23 in place of <start>

@app.route('/api/v1.0/<start>')
def start(start):
    """Temperature data for Start date."""
    
    # Check for valid entry of start date
    valid_entry = session.query(Measurement).filter(Measurement.date == start).first()
 
    if valid_entry is not None:
        results = (session.query(func.min(Measurement.tobs),
                                 func.avg(Measurement.tobs),
                                 func.max(Measurement.tobs))
                            .filter(Measurement.date >= start).all())

        tmin = results[0][0]
        tavg = '{0:.4}'.format(results[0][1])  # Format the average temperature
        tmax = results[0][2]
    
        result_printout = (['Entered Start Date: ' + start,
                            'The lowest Temperature was: ' + str(tmin) + ' F',
                            'The average Temperature was: ' + str(tavg) + ' F',
                            'The highest Temperature was: ' + str(tmax) + ' F'])
        return jsonify(result_printout)
    else:
        return jsonify({'error': 'Start date not found in the dataset'})
# For start and end date, again search by dates in right format
@app.route('/api/v1.0/<start>/<end>')
def temp_start_end(start, end):
    session = Session(engine)
    # Query for the min, max, and avg temperatures from the start date to the end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end).all()
    session.close()
    temp_data = [{"TMIN": result[0], "TAVG": result[1], "TMAX": result[2]} for result in results]
# Return a JSON list of the calculated values
    return jsonify(temp_data)

#Run your Flask app:
if __name__ == "__main__":
    app.run(debug=True)
#################################################
