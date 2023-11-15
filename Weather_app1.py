#Import the dependencies.

import pandas as pd
import numpy as np
import datetime as dt

#Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from sqlalchemy import Column, String, Float, Integer

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
path = "Resources/tomato.sqlite"
engine = create_engine(f"sqlite:///{path}")
# reflect an existing database into a new model
# reflect the tables
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)
#Base.prepare(engine, reflect=True)
# Save references to each table
mes = Base.classes.measurement
st = Base.classes.station



# Create our session (link) from Python to the DB
session = Session(bind= engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def landing():
    """List all available api routes."""
    routes= (
    '/Available Routes:',
    '/api/v1.0/precipitation',
    "/api/v1.0/stations",
    "/api/v1.0/tobs",
    "/api/v1.0/{start}",
    "/api/v1.0/{start}/{end}"
    )
    return '<br/>'.join(routes)

# ################################################
@app.route("/api/v1.0/precipitation")
def precip():
    # Create our session (link) from Python to the DB
   # session = Session(engine)
 #calculate previous year's precipitation
    # Find the most recent date in the data set.
    lst = session.query(mes.date).order_by(mes.date.desc()).first()
    #calulate last year
    year_ago = dt.datetime.strptime(lst[0], 
                        '%Y-%m-%d') - dt.timedelta(days=365)

    results = session.query(mes.station, mes.date, 
                    mes.prcp).filter(mes.date > year_ago).all()
    session.close()        
    #dictionary of values
    Prcp =[]
    for station, date, prcp in results:
        precip = {}
        precip['Station']= station,
        precip['Date']= date, 
        precip['Precipitation'] =prcp
        Prcp.append(precip)

    return jsonify(Prcp)

# ################################################  
@app.route('/api/v1.0/stations')
def stat():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""

    results = session.query(st.station, st.name).all()

    session.close()

# Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)
# ################################################
@app.route('/api/v1.0/tobs')
def tobs():
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    m_act = 'USC00519281'
    st_act = session.query(func.min(mes.tobs), func.max(mes.tobs), func.avg(mes.tobs))\
        .filter(mes.station== m_act).all()
    st_act= {'Min': st_act[0][0], "Max": st_act[0][1], 'Average': st_act[0][2]}
    session.close() 
    return jsonify(st_act)

# ################################################
@app.route('/api/v1.0/<start>')
def pic_date(start):   

# Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    m_act = 'USC00519281'
    st_act = session.query(func.min(mes.tobs), func.max(mes.tobs), func.avg(mes.tobs))\
        .filter(mes.station== m_act, mes.date > start).all()
    dic = {}
    for a,b,c in st_act:
        dic['Min']= a
        dic['Max']= b
        dic["Average"]=c
    jf_Sdf = dic
    session.close() 
    return jsonify(jf_Sdf)


# ################################################
@app.route("/api/v1.0/<start>/<end>")
def cho_date(start, end):
    # Using the most active station id from the previous query, calculate the lowest, highest, and average temperature.
    m_act = 'USC00519281'
    st_act = session.query(func.min(mes.tobs), func.max(mes.tobs), func.avg(mes.tobs))\
        .filter(mes.station== m_act, mes.date > start, mes.date<end).all()
    SE_ED =  {'Min': st_act[0][0], "Max": st_act[0][1], 'Average': st_act[0][2]}
    session.close() 
    return jsonify(SE_ED)

################################################

if __name__ == "__main__":
    app.run(debug=True)
