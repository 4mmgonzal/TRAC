import os
import os
import netCDF4 as nc4
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import imageio
import cartopy
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from cartopy import feature as cfeature
from cartopy.feature import NaturalEarthFeature, LAND, COASTLINE, OCEAN, LAKES, BORDERS
import matplotlib.ticker as mticker
import imageio
from IPython.display import Image       


def map_var(ds,res):

    """
    This function transfers data from dataset into mappable variables
    
    Parameters:
    ===========
    ds  : netCDF4 dataset
    res : int - time resolution for animation
    
    Returns:
    ===========
    lon        : array - longitude values
    lat        : array - latitude values
    temp       : array - temperature values
    year       : list - years (repetition dependent on res)
    year_range : array - index value of years with (res) intervals    
    """
    
    #dataset variables
    time = ds.variables['time']
    lat = ds.variables['lat'][:]
    lon = ds.variables['lon'][:]
    z = ds.variables['z'][:]
    temp_var = ds.variables['anom'] #(time, z, lat, lon)

    #sync time with temperature data and res
    years = nc4.num2date(time[:], time.units) #transferring time data from 'Days since 01-01-1800'
    years = np.array(years)
    #lists to reorganize year data
    y = []
    year = []
    #for loops to organize years into YYYY
    for i in range(len(years)):
        y.append(str(years[i]))
    for i in range(len(y)):
        year.append(y[i][:4]) #years in YYYY
    year_range = np.arange(0,len(year),res) #determines how many figures to create
    
    #cleaning temp_var from dataset
    t = np.array(temp_var)
    t = np.where(t > -900,t,np.nan) #removing artifacts of sentinal values
    
    #taking np.ptp (statistical range) of temperature values in original dataset format
    temp = [[[np.ptp(t[k:k+12,0,j,i])for i in range(len(lon))]for j in np.arange(0,len(lat),1)]for k in np.arange(0,len(year),12)]
    temp = np.array(temp)
    
    #values used in map2png
    return lon,lat,temp,year, year_range


def map2png(lon,lat,temp,year, year_range,**kwargs):
    """
    This function creates a map figure and saves a '.png' file in the 'Fig' directory.
    
    Parameters:
    ============
    lon        : 1d array - longitude values 
    lat        : 1d array - latitude values
    temp       : 4d array - temperatures in shape (len(lat),len(lon))
    year       : 1d array - dates measured
    year_range : 1d array - date range by increments
    kwargs     : dictionary - projection types
    
    Returns:
    ============
    None  
    
    """

    #creating new 'Fig' directory
    L = os.listdir("./")
    if 'Fig' not in L:
        os.mkdir('Fig')
    for m in L:
        if '.png' in m:
            os.remove('Fig/' + m)
    
    #transferring variables into mappable format for each frame (date spread decided by year_range)
    for i in range(len(year_range)):
        temps,years,year_ranges = temp[round(year_range[i]/12),:,:],year[year_range[i]],year_range[i]

    
        #plot
        plt.clf() # Clear the plot in case you call it multiple times
        plt.figure(1, (6, 6),dpi=900)

        #choosing projection type
        for key in kwargs:
            if kwargs[key] == 'LambertConformal':
                ax = plt.axes(projection=ccrs.LambertConformal(central_longitude=260.0, central_latitude=33.0))        
            elif kwargs[key] == 'Orthographic':
                ax = plt.axes(projection=ccrs.Orthographic(-75, 42))
            elif kwargs[key] == 'Mollweide':
                ax = plt.axes(projection=ccrs.Mollweide(central_longitude=180.0))
            elif kwargs[key] == 'Mercator':
                ax = plt.axes(projection=ccrs.Mercator(central_longitude=180.0, min_latitude=-70.0, max_latitude=70.0, globe=None))
            else:
                ax = plt.axes(projection=ccrs.Orthographic(-75, 42)) #make Orthographic the default proj type
                kwargs[key] = 'Orthographic' #this is for naming files later
            p = kwargs[key] #projection type


        #formatting
        gl = ax.gridlines(crs=ccrs.PlateCarree(), color='black', linewidth=1, linestyle='dotted')
        gl.ylocator = mticker.FixedLocator(np.arange(-80, 81, 20))
        gl.xlocator = mticker.FixedLocator(np.arange(-180, 181, 60));
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        X, Y = np.meshgrid(lon, lat)
        levels = np.arange(0, 29, 1) # Define contour intervals
        #color plot
        m = ax.contourf(X, Y, temps,levels,\
                        transform=ccrs.PlateCarree(),
                        cmap=cm.jet)
        ax.coastlines()
        ax.set_global()

        cbar = plt.colorbar(m) # Put on a color bar of temperatures    
        plt.title('Temperature Range - Year: '+ years + '\n($T_{Max} - T_{Min}$[˚C])', fontsize=12);
        plt.savefig('Fig/' + years +p+ str(year_ranges) + '.png') # Saves the figure to a file
        #file name example: 1880Mercator100.png
        
def animate_map(spf):    
    
    """
    This function creates a map animation and saves a '.GIF' file in the 'Fig' directory.
    
    Parameters:
    ===========
    spf : float - seconds per frame
    
    Returns:
    ===========
    None
    """
    #recalling files from 'Fig' directory
    filenames = sorted(os.listdir('Fig/')) # Listing of the directory
    images = [] # Make a container to put the image files in
    for file in filenames:                          # Step through all the maps
        if '.png' in file:                          # Skip hidden files
            filename = 'Fig/' + file               # Make filename from the folder name and the file name
            images.append(imageio.imread(filename)) # Read it in and stuff in the container
    kwargs = {'duration': spf}                       # Use spf for second delay between frames
    imageio.mimsave('Fig/map_1.gif', images, 'GIF', **kwargs) # Save to an animated gif.  

    return Image(filename="Fig/map_1.gif") #display GIF

