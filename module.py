import datetime as dt
import meteomatics.api as api
import numpy as np
from shapely.geometry import Point



# No OUTPUT: Downloads filedata.nc
def get_netcdf(coordinates, resolution, parameter, interval=12, before=0, after=7, model='mix', filepath=".", filename=""):

    '''
    Get netcdf file from meteomatics API.
    Coordinates format: [North latitude, West longitude, South Latitude, West longitude]
    Resolutions format: [Latitude Resolution, Longitude Resolution]
    Parameter: Climatologic parameter
    Interval: hours
    Before: Days before now (past)
    After: Days after now (forecast)
    '''

    # Credentials
    username = 'burgos_alexander'
    password = 'NF0xCcC38p'

    # Coordinates of the area and its resolution
    lat_N, lon_W, lat_S, lon_E = coordinates
    res_lat, res_lon = resolution
    
    # Date and time limits
    today = dt.datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    startdate = today - dt.timedelta(days=before)
    enddate = today + dt.timedelta(days=after)
    interval = dt.timedelta(hours=interval)
    
    # Parameter name for filename
    if not filename:
        if parameter == str:
            parameter_name = parameter.replace(":","")
            # .nc filename
            filename = f"{parameter_name}__{startdate.year}_{startdate.month}_{startdate.day}__{enddate.year}_{enddate.month}_{enddate.day}-{startdate.hour}_{startdate.minute}.nc"
        else:
            filename = f"{len(parameter)}_var_"
    
    # filepath
    filepath = filepath + "/"

    # Query to the meteomatics API
    try:
        api.query_netcdf(filepath+filename, startdate, enddate, interval, parameter, 
                        lat_N, lon_W, lat_S, lon_E, res_lat, res_lon, username, password, model)
        print("Filename: {}".format(filename))

    except Exception as e:
        print("Failed, exception is {}.".format(e))


# Get dataframe timeseries for different parameters and locations
def get_timeseries(coordinates, parameters, interval=12, before=0, after=7, model='mix'):

    '''
    Get dataframe from meteomatics API.
    Coordinates format: [(x1,y1),(x2,y2),...]
    Parameters format: ["t_2m:C","precip_1h:mm"] 
    Intervals: hours
    Before: Days before now (past)
    After: Days after now (forecast)
    '''

    # Credentials
    username = 'burgos_alexander'
    password = 'NF0xCcC38p'
    
    # Date and time limits
    today = dt.datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0)
    startdate = today - dt.timedelta(days=before)
    enddate = today + dt.timedelta(days=after)
    interval = dt.timedelta(hours=interval)
    
    print("time series:")
    # Query to the meteomatics API
    try:
        df = api.query_time_series(coordinates, startdate, enddate, interval, parameters, username, password, model)
        return df

    except Exception as e:
        print("Failed, exception is {}.".format(e))



# Make a mask acoording to a polygon object
def make_mask(longitudes, latitudes, polygon, parameter):

    # Uniformize shape
    lons2d, lats2d = np.meshgrid(longitudes, latitudes)

    # Create the mask
    mask = np.array( [ [polygon.contains(Point(lon, lat)) for lon, lat in zip(lon_row, lat_row)] for lon_row, lat_row in zip(lons2d, lats2d) ] )

    # Get the parameter matrix masked
    P_masked = np.where(mask, parameter, np.nan)

    return P_masked