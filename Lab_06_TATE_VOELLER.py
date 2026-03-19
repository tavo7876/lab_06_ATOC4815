import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
##write what the figure is showing
##we are going to calculate dewpoint depression 
url = "https://sundowner.colorado.edu/weather/atoc1/wxobs20240314.txt"

df = pd.read_fwf(url, header = [0,1], skiprows = [2])


date_col = [c for c in df.columns if c[1] == "Date"][0]
time_col = [c for c in df.columns if c[1] == "Time"][0]

t = (
    df[time_col]
    .astype(str)
    .str.strip()
    .str.replace(r"a$", "AM", regex=True)
    .str.replace(r"p$", "PM", regex=True)
)

dt = pd.to_datetime(
    df[date_col].astype(str).str.strip() + " " + t,
    format="%m/%d/%y %I:%M%p",
    errors="coerce",
)

df = df.set_index(dt).drop(columns=[date_col, time_col])
df.index.name = "datetime"

df.columns = [
    "_".join([str(a).strip(), str(b).strip()]).replace(" ", "_").strip("_")
    for a, b in df.columns
]







temp_f = df['Temp_Out'] #pull tempf
temp_f_1h = temp_f.resample('1h').mean() #resample tempf to tempf 1hr mean

dewpoint_f = df['Dew_Pt.']  #repeat with dewpoint
dewpoint_f_1h = dewpoint_f.resample('1h').mean()


def convert_tempature(temp): #function converts our temps from f to c
    temps_c = (temp - 32)* 5/9
    return temps_c

#RH: =100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
def realtive_humidity(dewpoint,temp):
    rh_1hr = 100*( np.exp( (17.625 * dewpoint)/(243.04 + dewpoint) ) ) / np.exp(((17.625*temp)/(243.05+temp))) 
    return rh_1hr

temp_c_1hr = convert_tempature(temp_f_1h)#calling convert tempature function
dewpoint_c_1hr = convert_tempature(dewpoint_f_1h)
rh_1hr = realtive_humidity(dewpoint_c_1hr,temp_c_1hr)

dewpoint_depression_1hr = temp_c_1hr - dewpoint_c_1hr# calculating dewpoint depression

less_than_2_datetime = dewpoint_depression_1hr[dewpoint_depression_1hr < 2].index.to_numpy() # get values that are less than 2 deg C, very possilbe dew
greater_than_2_datetime = dewpoint_depression_1hr[dewpoint_depression_1hr >= 2].index.to_numpy() # greater than 2C less possilbe dew






fig, ax1 = plt.subplots(figsize=(9, 5))#create subplot if we want to add more graphs later

# ax1.fill_between(less_than_2_datetime,20, color = 'lime', alpha = .2, label = "Highest Likleyhood of rain")
# ax1.fill_between(greater_than_2_datetime,20, color = 'salmon', alpha = .2, label = "Lower Likleyhood of rain")

ax1.plot(dewpoint_depression_1hr.index, dewpoint_depression_1hr.values,#.index for time, .values for value at that time
        marker='o', linewidth = 2, color='steelblue',label = 'dewpoint depression')
#set labels 
ax1.set_title("Dewpoint Depression on 03/14/24 ATOC1 Weather Station")
ax1.set_xlabel("Datetime in UTC")
ax1.set_ylabel("Dewpoint Depression (C°)")
ax1.grid(True, alpha = .3)


#plot realitve Humidity 
ax2 = ax1.twinx()
ax2.plot(rh_1hr.index, rh_1hr.values,
        marker = 'o', linewidth = 1, color = 'r',label = "Realtive Humidity %")
ax2.set_xlabel("Datetime in UTC")
ax2.set_ylabel("Realtive Humidity %")

#shared details
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc = "upper left")

plt.xticks(rotation = 45) 
plt.tight_layout()
plt.savefig("dewpoint_depression_20240314.png",dpi = 250)
plt.show()