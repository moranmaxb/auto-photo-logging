### DivaPhotoProject_2024-07-31

# Set Working Directory to folder with photos
import os
path = r"C:\Users\might\Documents\2024-07-31_DivaSoftwareProject\2024-10-27_Westlake-Road-Repair\ParkwoodCt" #r in front is for the back slashes
os.chdir(path)

##### Function to grab data needed
def metaDataFunction(current_image):
    #print("Current Image:",current_image)

    # Get Date & Time
    from PIL import Image, ExifTags
    img = Image.open(current_image)
    exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }
    gpsInfo = exif['GPSInfo']

    #print(exif)

    direction = gpsInfo[17] # direction correction (17 if with normal camera app, 6 if with other app)
    if direction>=337.5 or direction<=22.5:
        direction = "N," + str(direction)
    elif direction>22.5 and direction<67.5:
        direction = "NE," + str(direction)
    elif direction>=67.5 and direction<=112.5:
        direction = "E," + str(direction)
    elif direction>112.5 and direction<157.5:
        direction = "SE," + str(direction)
    elif direction>=157.5 and direction<=202.5:
        direction = "S," + str(direction)
    elif direction>202.5 and direction<247.5:
        direction = "SW," + str(direction)
    elif direction>=247.5 and direction<=292.5:
        direction = "W," + str(direction)
    elif direction>292.5 and direction<337.5:
        direction = "NW," + str(direction)

    ### Get GPS Data
    from exif import Image
    def dms_to_dd(gps_coords, gps_coords_ref):
        d, m, s =  gps_coords
        dd = d + m / 60 + s / 3600
        if gps_coords_ref.upper() in ('S', 'W'):
            return -dd
        elif gps_coords_ref.upper() in ('N', 'E'):
            return dd
        else:
            raise RuntimeError('Incorrect gps_coords_ref {}'.format(gps_coords_ref))

    with open(current_image, 'rb') as image_file:
        my_image = Image(image_file)
        latitude = dms_to_dd(my_image.gps_latitude, my_image.gps_latitude_ref)
        longitude = dms_to_dd(my_image.gps_longitude, my_image.gps_longitude_ref)
        coordinates = "(" +str(latitude) + ", " + str(longitude) + ")"
    
    return exif['DateTimeDigitized'], coordinates, direction

###############

### Create new row for data frame
def importImageData(current_image):
    dateNTime, coordinates, direction = metaDataFunction(current_image)
    date,time = dateNTime.split(" ")

    #print("File name:",current_image)
    #print("Date:",date)
    #print("Time:",time)
    #print("Coordinates: ",coordinates)

    newRow = {'File Name': current_image, 'Date': date, 'Time': time, 'Coordinates': coordinates, 'Direction': direction}
    return newRow

###################

import pandas as pd

#### Create empty data frame
data = {
    "File Name": [],
    "Date": [],
    "Time": [],
    "Coordinates": []
}
df = pd.DataFrame(data)

for filename in os.listdir(path):
    current_image = os.path.join(filename)
    # checking if it is a file
    if os.path.isfile(current_image):
        newRow = importImageData(current_image)
        df = df._append(newRow, ignore_index = True)

### Grab nearest address to coordinates
#from geopy.geocoders import Photon (old one that worked)
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

geolocator = Nominatim(user_agent="measurements")
geocode = RateLimiter(geolocator.reverse, min_delay_seconds=1)
df['Coordinates'] = df['Coordinates'].apply(lambda x: tuple(map(float, x.strip('()').split(','))))
df['location'] = df['Coordinates'].apply(geocode)
print(df)

### Upload Data Frame as CSV
df.to_csv('out.csv', index=False)