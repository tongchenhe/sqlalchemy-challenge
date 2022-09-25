from unittest import result
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



app = Flask(__name__)

@app.route("/")
def index():
    return (f"Available Routes:<br/>" 
    f"/api/v1.0/precipitation<br/>" 
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/'start'<br/>"
    f"/api/v1.0/'start'/'end'")

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #Query the data for most recent year
    #Exactly like climate_analysis.ipynb
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_away = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)
    one_year_away_str = one_year_away.strftime("%Y-%m-%d")
    one_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_away_str).all()
    
    session.close()

    # Create a dictionary from last year's data and append them to a list
    prcp_ls = []
    for date, prcp in one_year_data:
        date_dict = {}
        date_dict['Date'] = date
        date_dict['Precipitation'] = prcp
        prcp_ls.append(date_dict)

        
    return jsonify(prcp_ls)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    return jsonify(list(np.ravel(results)))


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Calculate the date 1 year ago from last date in database


    #Query the data for most recent year
    #Exactly like climate_analysis.ipynb
    recent_date = session.query(func.max(Measurement.date)).first()[0]
    one_year_away = dt.datetime.strptime(recent_date,"%Y-%m-%d") - dt.timedelta(days=365)
    one_year_away_str = one_year_away.strftime("%Y-%m-%d")


    # Query the primary station for all tobs from the last year
    most_active = session.query(Measurement.station, func.count()).group_by(Measurement.station).order_by(func.count().desc()).all()[0][0]
    one_year_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_away_str,Measurement.station==most_active).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    # Return the results
    return jsonify(list(np.ravel(one_year_tobs)))

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    session = Session(engine)
    # Select statement
    if end is not None:
        results = session.query(func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
        ).filter(Measurement.date>start, Measurement.date<end).all()[0]
    else:
        results = session.query(func.min(Measurement.tobs),
        func.avg(Measurement.tobs),
        func.max(Measurement.tobs),
        ).filter(Measurement.date>start).all()[0]
    TMIN = results[0]
    TAVG = results[1]
    TMAX = results[2]


    # Unravel results into a 1D array and convert to a list
    return jsonify([TMIN,TAVG,TMAX])


if __name__ == "__main__":
    app.run(debug=True)