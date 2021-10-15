# CDS API data download tool (C) 2021 HWITW project
#
# Downloads data we are interested in from Copernicus webapi in the form of netcdf files.
# Semi intelligent.. It can't resume a partial individual file, but it knows what files
# it has sucessfully downloaded and will resume at the next file where it left off.
# It will save files to the directory that it is run from.
#
# NOTE:
# The cdsapi library looks for a file called ~/.cdsapirc that holds the auth token.
# I think the first time you run/load it, it will prompt for the token. I forget.. the cds
# website explains it.
#
import math
import datetime
import os.path

import cdsapi
import netCDF4

cds = cdsapi.Client()
app_version = "0.94"
force_download = False;
current_time = datetime.datetime.now()

# download era5 or era5 back extention data to netcdf files
def download_dataset( ds_name, dir_name, start_year, end_year, area_lat_long ):
    years = list( range( start_year, end_year + 1 ) )
    # # calculate a unique number for each quarter degree on the planet.
    # # makes having a unique filename for the coordinates simpler.
    # grid_num = int( ((area_lat_long[0] + 90) * 4) * 360 * 4 + ((area_lat_long[1] + 180) * 4) )
    # print( f'Downloading {ds_name} {area_lat_long} (gn{grid_num}) from {start_year} to {end_year}')

    # download year, variable for entire globe

    for year in reversed( years ):
        for var_name in variables:
            # file naming scheme
            pathname = f'./{dir_name}/{year}/'
            #filename = f'gn{grid_num}-{year}-{var_name}.nc'
            filename = f'global-{year}-{var_name}.nc'
            fullname = pathname + filename

            # see if file already downloaded.. if it exists and is larger then some nonsense amount
            already_exists = os.path.isfile( fullname ) and os.path.getsize( fullname ) > 500
            if already_exists:
                print( f'{filename} exists already' )
                # todo: validate the existing netcdf file

            if not already_exists or force_download:
                print( f'{filename} requested...')
                # remove any existing file
                try:
                    os.remove( fullname )
                except FileNotFoundError:
                    pass
                # create the path if necessary
                os.makedirs( pathname, exist_ok=True )

                # download to temp file
                tempfullname = fullname + '.tempdl' 
                r = cds.retrieve(
                    ds_name,
                    {
                        'product_type': 'reanalysis',
                        'format': 'netcdf',
                        'year': year,
                        'time': 'all',
                        'variable': [ var_name ]
                        #'area': area_lat_long,
                    }, tempfullname )
                # rename completed download
                os.rename( tempfullname, fullname )

# hello
print( f'** HWITW Copernicus data download tool v{app_version} **\n')

# 0.25 degree resolution
inp_lat = 59.64 # homer ak
inp_long = -151.54

# get the containing cell 
lat0 = math.ceil( inp_lat * 4 ) / 4
lat1 = (math.floor( inp_lat * 4 ) / 4) + 0.01 # edge is not inclusive
long0 = math.floor( inp_long * 4 ) / 4
long1 = (math.ceil( inp_long * 4 ) / 4) - 0.01

area0 = [ lat0, long0, lat1, long1 ]
area0 = None  # we are doing global downloads!

# the variables we are interested in
variables = [
    '10m_u_component_of_wind',
    '10m_v_component_of_wind',
    '2m_dewpoint_temperature',
    '2m_temperature',
    'cloud_base_height',
    'precipitation_type',
    'surface_pressure',
    'total_cloud_cover',
    'total_precipitation',
]

# era5 back extension goes from 1950 to 1978
download_dataset(   'reanalysis-era5-single-levels-preliminary-back-extension',
                    'cds_era5_backext',
                    1950, 1978,
                    area0 )

# era5 goes from 1979 to present
download_dataset(   'reanalysis-era5-single-levels',
                    'cds_era5',
                    1979, current_time.year,
                    area0 )