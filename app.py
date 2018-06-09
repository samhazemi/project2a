import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import cast
from sqlalchemy import create_engine, inspect, func
from sqlalchemy.orm import Session, aliased
from datetime import datetime
import numpy as np
import pandas as pd

from flask import Flask, jsonify, render_template, request, flash, redirect, url_for


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///chicagobnbnew.db", echo=False)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

        # cd 09cd cdSave references to the measurement and station tables
Listings = Base.classes.listings_table
Crime=Base.classes.crime_table


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# Return the dashboard homepage
@app.route("/")
def index():
    return render_template("index.html")


@app.route('/scatterplot', methods=['GET', 'POST'])
def scatterplot():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('scatterplot.html')


# return List of neighbourhood names
@app.route('/names')
def names():
   
    neighbourhood_results = session.query(Listings.neighbourhood).group_by(Listings.neighbourhood).all()
    neighbourhood_list = list(np.ravel(neighbourhood_results))

    return jsonify(neighbourhood_list)
    

# return List of airbnb neighborhood crime count. 
@app.route('/crimecount/<neighbourhood>')
def crimecount(neighbourhood):
    crimecount_result=session.query(Crime.number_of_crimes).filter(Crime.neighbourhood == neighbourhood).all()
    crimecount= np.ravel(crimecount_result)
    return jsonify(int(crimecount[0]))

# return List of airbnb neighborhood crime rate. 

@app.route('/crimerate/<neighbourhood>')
def crimerate(neighbourhood):
   # Return only the first integer value for crime rate
    crimerate_result=session.query(Crime.crime_rate).filter(Crime.neighbourhood == neighbourhood).all()
    crimerate= np.ravel(crimerate_result)
    return jsonify(int(crimerate[0]))

# return crimeData for a given neighbourhood  
@app.route('/crimedata/<neighbourhood>')
def crimedata(neighbourhood):
    crimedata = []
    crimedata_dict = {}
    crime_results = session.query(Crime.neighbourhood, Crime.number_of_crimes, Crime.crime_rate).group_by(Crime.neighbourhood).filter(Crime.neighbourhood == neighbourhood).all()
    
    for result in crime_results :
        crimedata_dict["Neighbourhood"] = result[0]
        crimedata_dict["Number_of_Crimes"] = result[1]
        crimedata_dict["Crime_Rate"] = result[2]
    
        crimedata.append(crimedata_dict)

        print(crimedata)
    return jsonify(crimedata)


# return Entire_home information for a given neighbourhood
@app.route('/entirehome/<neighbourhood>')
def entirehome(neighbourhood):
    Entire_home_Listings_results = session.query(Listings.neighbourhood, func.avg(Listings.price ),\
                func.avg(Listings.number_of_reviews ), func.avg(Listings.reviews_per_month ),\
                func.avg(Listings.availability_365)).group_by(Listings.neighbourhood).\
                filter(Listings.room_type == 'Entire home,apt').\
                filter(Listings.neighbourhood == neighbourhood).all()
    
    Entire_home_data= []
    Entire_home_dict = {}
    for result in Entire_home_Listings_results:
        
        Entire_home_dict["Average_Entire_home_Price"] = result[1]
        Entire_home_dict["Average_Number_of_Reviews"] = result[2]
        Entire_home_dict["Average_Reviews_per_Month"] = result[3]
        Entire_home_dict["Average_Availability_365"] = result[4]


        Entire_home_data.append(Entire_home_dict)
        print (Entire_home_data)
    
    return jsonify(Entire_home_data)
        

# return Private_room information for a given neighbourhood
@app.route('/privateroom/<neighbourhood>')
def privateroom(neighbourhood):
    Private_room_Listings_results = session.query(Listings.neighbourhood,func.avg(Listings.price ),\
                func.avg(Listings.number_of_reviews ),  func.avg(Listings.reviews_per_month ),\
                func.avg(Listings.availability_365)).group_by(Listings.neighbourhood).\
                filter(Listings.room_type == 'Private room').\
                filter(Listings.neighbourhood == neighbourhood).all()
    
    Private_room_data= []
    Private_room_dict = {}
    for result in Private_room_Listings_results:
        
        
        Private_room_dict["Average_Private_room_Price"] = result[1]
        Private_room_dict["Average_Number_of_Reviews"] = result[2]
        Private_room_dict["Average_Reviews_per_Month"] = result[3]
        Private_room_dict["Average_Availability_365"] = result[4]

        Private_room_data.append(Private_room_dict)
        print(Private_room_data)
    
    return jsonify(Private_room_data)
        

# return Shared_room information for a given neighbourhood
@app.route('/sharedroom/<neighbourhood>')
def sharedroom(neighbourhood):
    Shared_room_Listings_results = session.query(Listings.neighbourhood,func.avg(Listings.price ),\
                func.avg(Listings.number_of_reviews ),  func.avg(Listings.reviews_per_month ),\
                func.avg(Listings.availability_365)).group_by(Listings.neighbourhood).\
                filter(Listings.room_type == 'Shared room').\
                filter(Listings.neighbourhood == neighbourhood).all()
    
    Shared_room_data= []
    Shared_room_dict = {}
    for result in Shared_room_Listings_results:
        
        
        Shared_room_dict["Average_shared_room_price"] = result[1]
        Shared_room_dict["Average_Number_of_Reviews"] = result[2]
        Shared_room_dict["Average_Reviews_per_Month"] = result[3]
        Shared_room_dict["Average_Availability_365"] = result[4]

        Shared_room_data.append(Shared_room_dict)
        print(Shared_room_data)

    
    return jsonify(Shared_room_data)



# return airbnb IDs and Price Values for a given neighbourhood.
@app.route('/listprice/<neighbourhood>')
def listprice(neighbourhood):

    stmt = session.query(Listings).statement
    df = pd.read_sql_query(stmt, session.bind)
    eachNH_df=df.loc[df['neighbourhood'] == neighbourhood]
    eachNH_df= eachNH_df.sort_values(by="price", ascending=0)
     # Format the data to send as json
    price_data = [{

        "airbnb_ids": eachNH_df ["airbnb_id"].values.tolist(),
        "price": eachNH_df["price"].values.tolist(),
        "number_of_reviews": eachNH_df ["number_of_reviews"].values.tolist(),
        "host_id": eachNH_df["host_id"].values.tolist(),
        "calculated_host_listings_count":eachNH_df ["calculated_host_listings_count"].values.tolist(),
        "room_type": eachNH_df["room_type"].values.tolist(),
        "minimum_nights": eachNH_df["minimum_nights"].values.tolist(),
        "availability_365": eachNH_df["availability_365"].values.tolist(),
           
    }]
    print(price_data)
    return jsonify(price_data)

@app.route('/correlation')
def correlation():
            
    NH_compare_data = pd.read_csv("neighbourhood_compare_data.csv")

    neighbourhood_compare_data = [{
        "neighbourhood": NH_compare_data["neighbourhood"].values.tolist(),
        "airbnb_counts_per_neighbourhood": NH_compare_data["airbnb_counts_per_neighbourhood"].values.tolist(),
        "total_reviews_per_neighbourhood": NH_compare_data["total_reviews_per_neighbourhood"].values.tolist(),
        "number_of_crimes": NH_compare_data ["number_of_crimes"].values.tolist()

    }]

    print(neighbourhood_compare_data)
    return jsonify(neighbourhood_compare_data)

if __name__ == "__main__":
    app.run(debug=True)


