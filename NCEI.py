
# coding: utf-8

# # Assignment 2
# 
# Before working on this assignment please read these instructions fully. In the submission area, you will notice that you can click the link to **Preview the Grading** for each step of the assignment. This is the criteria that will be used for peer grading. Please familiarize yourself with the criteria before beginning the assignment.
# 
# An NOAA dataset has been stored in the file `data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv`. The data for this assignment comes from a subset of The National Centers for Environmental Information (NCEI) [Daily Global Historical Climatology Network](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt) (GHCN-Daily). The GHCN-Daily is comprised of daily climate records from thousands of land surface stations across the globe.
# 
# Each row in the assignment datafile corresponds to a single observation.
# 
# The following variables are provided to you:
# 
# * **id** : station identification code
# * **date** : date in YYYY-MM-DD format (e.g. 2012-01-24 = January 24, 2012)
# * **element** : indicator of element type
#     * TMAX : Maximum temperature (tenths of degrees C)
#     * TMIN : Minimum temperature (tenths of degrees C)
# * **value** : data value for element (tenths of degrees C)
# 
# For this assignment, you must:
# 
# 1. Read the documentation and familiarize yourself with the dataset, then write some python code which returns a line graph of the record high and record low temperatures by day of the year over the period 2005-2014. The area between the record high and record low temperatures for each day should be shaded.
# 2. Overlay a scatter of the 2015 data for any points (highs and lows) for which the ten year record (2005-2014) record high or record low was broken in 2015.
# 3. Watch out for leap days (i.e. February 29th), it is reasonable to remove these points from the dataset for the purpose of this visualization.
# 4. Make the visual nice! Leverage principles from the first module in this course when developing your solution. Consider issues such as legends, labels, and chart junk.
# 
# The data you have been given is near **Ann Arbor, Michigan, United States**, and the stations the data comes from are shown on the map below.

# In[5]:

import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd

def leaflet_plot_stations(binsize, hashid):

    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))

    station_locations_by_hash = df[df['hash'] == hashid]

    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)

    return mplleaflet.display()

leaflet_plot_stations(400,'fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89')


# In[2]:

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np 
import pandas as pd 
def read_data():
	df = pd.read_csv('data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')
	df.Date= pd.to_datetime(df.Date)
	df=df[(df.Date!='2008-02-29') & (df.Date!='2012-02-29')]
	df_2015 = (df[df.Date.map(lambda d: d.year == 2015)]).groupby('Date').apply(lambda 
		gp: pd.Series({'Tmax':gp.Data_Value.max(),'Tmin':gp.Data_Value.min()})).reset_index()
	df_05_14 = (df[df.Date.map(lambda d: d.year != 2015)].groupby('Date')).apply(lambda 
		gp: pd.Series({'Tmax':gp.Data_Value.max(),'Tmin':gp.Data_Value.min()})).reset_index()
	df_05_14['m-day'] = df_05_14.Date.map(lambda d: '{:02d}-{:02d}'.format(d.month,d.day))
	df_05_14_gp = df_05_14.groupby('m-day').apply(lambda gp: pd.Series({'Tmax':gp.Tmax.max(),'Tmin':gp.Tmin.min()})).reset_index()
	df_merge = df_2015.merge(df_05_14_gp, left_index=True, right_index=True, suffixes=('_2015','_05_14'))
	df_merge['high'] = df_merge[df_merge.Tmax_2015 > df_merge.Tmax_05_14].Tmax_2015
	df_merge['low'] = df_merge[df_merge.Tmin_2015 < df_merge.Tmin_05_14].Tmin_2015
	df_merge.set_index('Date')
	return df_merge, df_05_14_gp
df_merge, df_05_14_gp = read_data()


# In[7]:

# ===== Plot 2D line and scatter
fig = plt.figure(figsize=(16,8))
ax = plt.gca()
plt.plot(df_05_14_gp.index, df_05_14_gp.Tmax, label='2005-2014 record high', color='red', alpha=0.2)
plt.plot(df_05_14_gp.index, df_05_14_gp.Tmin, label='2005-2014 record low', color='green', alpha=0.2)
ax.fill_between(df_05_14_gp.index, df_05_14_gp.Tmin, df_05_14_gp.Tmax, facecolor='grey', alpha=0.2)
plt.scatter(df_merge.index, df_merge.high, label='2015 broke high',color='red', marker='^', s=30, alpha=0.4)
plt.scatter(df_merge.index, df_merge.low, label='2015 broke low',color='blue', marker='v', s=30, alpha=0.4)
# ===== Plot legend
legend = plt.legend(bbox_to_anchor=(0.45,0.2),loc=3, ncol=1, mode='expand', handlelength=3, scatterpoints=1)
legend.get_frame().set_alpha(0.)
for line in legend.get_lines():
    line.set_lw(3)
for s_legend in legend.legendHandles:
    s_legend._sizes = [70]
    s_legend.set_alpha(0.4)
# ===== Plot annotation
m_day = [0] + list(np.cumsum(pd.date_range('2005-01-01', periods=12, freq='M').map(lambda d: d.day)))
x_pos = list(map(lambda x: x+15, m_day[:-1]))
x_label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'] 
for pos, month in zip(x_pos, x_label):
    ax.annotate(s=month, xy =(pos, -350), xycoords='data', alpha=0.8, size=9, va='top', ha='center')
plt.vlines(m_day[1:-1], *ax.get_ylim(), color='k', linestyles='--', lw=0.3, alpha=0.3)
ax.annotate(s='Plot by Lambert Huang',xy=(x_pos[5]+20,-420), xycoords='data', alpha=0.8, size=9, va='bottom', ha='center')
# ==== Plot Celsius and Fahrenheit 
yaxis_tick_left = np.array([-300, -200, -100, 0, 100, 200, 300, 400])
yaxis_tick_right = yaxis_tick_left * 0.18 +32
yaxis_temp_left = list(map(lambda t: '{}$^{{\circ}}$C'.format(int(t*0.1)), yaxis_tick_left))
yaxis_temp_right = list(map(lambda t: '{}$^{{\circ}}$F'.format(int(t)), yaxis_tick_right))
for pos, temp in zip(yaxis_tick_left, yaxis_temp_left):
    ax.annotate(s=temp, xy =(-1, pos), xycoords='data', alpha=0.7, size=9,va='center', ha='right')
for pos, temp in zip(yaxis_tick_left, yaxis_temp_right):
    ax.annotate(s=temp, xy =(380, pos), xycoords='data', alpha=0.7, size=9,va='center', ha='right')
plt.hlines(yaxis_tick_left, *ax.get_xlim(), color='k', linestyles='--', lw=0.3, alpha=0.3)
plt.title('The temperature of 2015 broke record high/low of 2005-2014 near Ann Arbor, Michigan US',size=15, alpha=0.8)
# ===== Remove Axes ticks
plt.tick_params(top='off', bottom='off', left='off', right='off', labelleft='off', labelbottom='off')
for spine in ax.spines.values(): spine.set_visible(False)
plt.show()


# In[ ]:




# In[ ]:



