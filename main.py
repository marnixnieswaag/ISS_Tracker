import os
import tkinter as tk
import tkintermapview
from PIL import Image, ImageTk
import requests
from PIL import ImageTk, Image
from datetime import timedelta
import pytz
from skyfield.api import EarthSatellite, wgs84, load
from timezonefinder import TimezoneFinder

# Constants
ISS_API_URL = "https://api.wheretheiss.at/v1/satellites/25544"
TLE_API_URL = "https://api.wheretheiss.at/v1/satellites/25544/tles"

y=0

# Function to fetch ISS data
def fetch_iss_data():
    response = requests.get(ISS_API_URL)
    return response.json()

# Function to fetch TLE data
def fetch_tle_data():
    response = requests.get(TLE_API_URL)
    return response.json()

# Function to update ISS marker position
def update_iss_marker():
    iss_data = fetch_iss_data()
    latitude = iss_data["latitude"]
    longitude = iss_data["longitude"]
    marker.set_position(int(latitude), int(longitude))
    window.after(2000, update_iss_marker)

def degrees_cardinal(d):
    dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW',
             'WSW', 'W', 'WNW', 'NW', 'NNW']
    ix = round(d / (360. / len(dirs)))
    return dirs[ix % len(dirs)]


# Function to handle the 'Submit' button click
def submit():
    global y
    while y <9:
        global text_label  # Declare text_label as a global variable
        location_str = ", ".join([entry.get() for entry in Entries])
        address = tkintermapview.convert_address_to_coordinates(location_str)
        tz = TimezoneFinder().timezone_at(lng=address[1], lat=address[0])
        timezone = pytz.timezone(tz)
        ts = load.timescale()
        t = ts.now().astimezone(timezone)
        
        tle_data = fetch_tle_data()
        line1 = tle_data["line1"]
        line2 = tle_data["line2"]
    
        satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)
        difference = satellite - wgs84.latlon(address[0], address[1])
        
        t0 = ts.now()
        t1 = ts.now() + timedelta(days=1)
        eph = load('de421.bsp')
        t, events = satellite.find_events(wgs84.latlon(address[0], address[1]), t0, t1, altitude_degrees=30.0)
        event_names = 'Begin', 'Max', 'End'
        sunlit = satellite.at(t).is_sunlit(eph)

        count=0
        x=0
        global data_frame
        data_frame = tk.Frame(master=text_frame)

        
        for ti, event, sunlit_flag in zip(t, events, sunlit):
            topocentric = difference.at(ti)
            alt, az, dis = topocentric.altaz()
            name = event_names[event]
            state = ('in shadow', 'in sunlight')[sunlit_flag]
            
            
            t_d_a_s = ("Time:", "Direction:", "Altitude:")

            datetime_str = f'{ti.astimezone(timezone)}'
            formated_datetime_str = datetime_str[:-13]
            date_str = formated_datetime_str[:10]
            time_str = formated_datetime_str[11:]
            string_1 = str(name)
            string_2 = f' {alt}'
            string_2 = string_2[:-13]
            string_2 += '°'
            string_3 =f'{az}'
            if 'd' in string_3:
                string_3 = f'{degrees_cardinal(int(string_3[:2]))}'
            elif 'de' in string_3:
                string_3.strip('de')
                string_3 = f'{degrees_cardinal(int(string_3[:1]))}'
            else:
                string_3 = f'{degrees_cardinal(int(string_3[:3]))}'
            
            
            string_4 = f'{state}'

            #strings = string_1,(string_2[:-13]+string_4), string_3

            
            if count == 0:
                #Shows the Date + 
                #The words 'Time', 'Direction', 'Altitude'
                info_block = tk.Frame(master=data_frame) 
                date_label = tk.Label(master=info_block,
                                text=date_str
                )
                date_label.grid(
                    row=0,
                    column=0,
                    sticky='w',
                    padx=5,
                    pady=5,
                )

                for i, t in enumerate(t_d_a_s):
                    text_label = tk.Label(
                        master=info_block,
                        text= t
                        )
                    text_label.grid(
                        row=1+i,
                        column=0,
                        sticky='w',
                        padx=5,
                        pady=5,
                    )
                info_block.grid(row=x,
                                column=count,
                                padx=5,
                                pady=5)
                data_block = tk.Frame(master=data_frame)

                event_label = tk.Label(master=data_block,
                                        text=string_1)

                event_label.grid(
                    row=0,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
                time_label = tk.Label(master=data_block,
                                    text=time_str
                )
                time_label.grid(
                    row=1,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
            
                direction_label = tk.Label(master=data_block,
                                        text=string_3
                )
                direction_label.grid(
                    row=2,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
                
                altitude_label = tk.Label(master=data_block,
                                        text=string_2
                )
                altitude_label.grid(
                    row=3,
                    sticky='w',
                    padx=5,
                    pady=5,
                )

                if count <3:
                    data_block.grid(row=x,
                                    column=count+1,
                                    padx=5,
                                    pady=5
                    )
                    count+=1
                    y+=1
                else:
                    data_block.grid(row=x,
                                    column=count+1,
                                    padx=5,
                                    pady=5
                    )
                    x+=1
                    y+=1 
                    count=0
                    
                count+=1
                
            else:

                data_block = tk.Frame(master=data_frame)

                event_label = tk.Label(master=data_block,
                                        text=string_1)

                event_label.grid(
                    row=0,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
                time_label = tk.Label(master=data_block,
                                    text=time_str
                )
                time_label.grid(
                    row=1,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
            
                direction_label = tk.Label(master=data_block,
                                        text=string_3
                )
                direction_label.grid(
                    row=2,
                    sticky='w',
                    padx=5,
                    pady=5,
                )
                
                altitude_label = tk.Label(master=data_block,
                                        text=string_2
                )
                altitude_label.grid(
                    row=3,
                    sticky='w',
                    padx=5,
                    pady=5,
                )

            
                if count <3:
                    data_block.grid(row=x,
                                    column=count+1,
                                    padx=5,
                                    pady=5
                    )
                    count+=1
                    y+=1
                else:
                    data_block.grid(row=x,
                                    column=count+1,
                                    padx=5,
                                    pady=5
                    )
                    x+=1 
                    y+=1
                    count=0

            data_frame.pack(padx=5, pady=5)

def clear():
    global y
    data_frame.destroy()
    y-=y
# Create and configure the main window
window = tk.Tk()
window.title("ISS Tracker")
window.geometry("750x750")

# Load images
current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
satellite_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "satellite.png")).resize((60, 60)))

# Create frames
map_frame = tk.Frame(master=window, relief="sunken", borderwidth=5)
map_frame.pack(side="right")

left_frame = tk.Frame(master=window, borderwidth=5)
left_frame.pack(side="right")

text_frame = tk.Frame(master=left_frame, borderwidth=5)
text_frame.pack(anchor="center")

entry_frame = tk.Frame(master=left_frame, borderwidth=5)
entry_frame.pack(anchor="center")

button_frame = tk.Frame(master=left_frame)
button_frame.pack(anchor="center")

# Create map widget
map_widget = tkintermapview.TkinterMapView(master=map_frame, width=1000, height=750, corner_radius=0)
map_widget.pack()

# Create and configure text label
text_label = tk.Label(text_frame, text='Enter your address to see when the ISS is visible near your location.')
text_label.config(font=("Courier", 9))
text_label.pack()

# Create labels and entry widgets
Labels = ["Street + House Number:", "City:", "Country:"]
Entries = []

for count, text in enumerate(Labels):
    label = tk.Label(master=entry_frame, text=text)
    label.grid(row=count, column=0, sticky="e")
    entry = tk.Entry(master=entry_frame, width=50)
    entry.grid(row=count, column=1)
    Entries.append(entry)

# Fit map bounding box
map_widget.fit_bounding_box((85, -180), (-85, 180))

# Create and configure 'Submit' button
submit_button = tk.Button(
    master=button_frame,
    width=10, height=6,
    text="Submit",
    command=submit
)
submit_button.pack(side="left")

# Create and configure 'Clear' button
clear_button = tk.Button(
    master=button_frame,
    width=10,
    height=6,
    text='Clear',
    command=clear
)
clear_button.pack(side='left', padx=20)

# Set tile server
map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

# Set ISS marker
iss_data = fetch_iss_data()
latitude = iss_data["latitude"]
longitude = iss_data["longitude"]
marker = map_widget.set_marker(
    int(latitude), int(longitude), text="ISS", icon=satellite_image)

# Start the main loop
window.after(2000, update_iss_marker)
window.mainloop()
