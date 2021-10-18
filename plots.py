# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Anish Koyamparambath (AK) or 
# University of Bordeaux (UBx) will not be used in advertising or publicity pertaining 
# to distribution of the software without specific, written prior permission.
# BOTH AK AND UBx DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# BOTH AK AND UBx BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.


import pandas as pd ,numpy as np, matplotlib.pyplot as plt, sqlite3
from scipy.interpolate import make_interp_spline, BSpline
from matplotlib.ticker import MaxNLocator
from geopolrisk.__init__ import APIError, _outputfile, _libfile
from geopolrisk.main import operations
from textwrap import wrap  

"""
This module generates graphs based on the result of the geopolrisk calculation.
Unless modified, an export file based on a calculation must exist in the output
folder inorder to use the following methods withing this module. 
This module generates two graphs: A trend based representation of the data if a
period of more than one year is defined; a individual representation, a vertical
bar graph that can also accomodate multiple resources and countries for one year.
"""
#Class of graphs

class graphics(operations):
    """
    Initialize the graphics by calling the variables from the main class required
    for logging. 
    Current initialization loads the exported csv file from the calculation.
    """
    def __init__(self, data="" ):
        try:
            data=pd.read_csv(_outputfile+'/export.csv')
        except:
            self.logging.debug("Export file failed to access")
        operations.__init__(self)
        try:
            self.logging.debug("graphics class accessed!")
        except Exception as e:
            print("Logging error {}".format(e))
        try:
            self._data = data
            self._data= self._data.drop(self._data.columns[0], axis = 1)
            self._data.columns = ["Year", "Resource", "Country", "RR", 
                                  "RRScenario", "GeoPolRisk", "CF", "HHI", "WTA"]
        except Exception as e:
            self.logging.debug(e)
            raise APIError
            
        """
        The following code extracts the maximum value of a variable for plotting 
        alongside the individual bar graphs for analysis
        """
        try:
            conn = sqlite3.connect(_libfile+'/datarecords.db', isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
            db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
            GPRS = [float(x) for x in db_df.geopolrisk.to_list()]
            HHI = [float(x) for x in db_df.hhi.to_list()]
            WA = [float(x) for x in db_df.wta.to_list()]
            maxGPRS = ["for "+str(db_df.country[GPRS.index(max(GPRS))]), db_df.year[GPRS.index(max(GPRS))], db_df.resource[GPRS.index(max(GPRS))], max(GPRS)]
            maxHHI = ["", db_df.year[HHI.index(max(HHI))], db_df.resource[HHI.index(max(HHI))], max(HHI)]
            maxWA = ["for "+str(db_df.country[WA.index(max(WA))]), db_df.year[WA.index(max(WA))], db_df.resource[WA.index(max(WA))], max(WA)]
            self.maxdict = {'GeoPolRisk': maxGPRS, 'HHI': maxHHI, 'WTA': maxWA }
        except Exception as e:
            self.logging.debug(e)
            
            
    """
    Each data contains 3 scenarios; GeoPolRisk value with or without substitutation,
    GeoPolRisk value of a resource whose recycling rate is above 0 considered 
    in best case scenario, GeoPolRisk value of a resource whose recycling rate
    is above 0 considered in worst case scenario.
    """
    
    """
    The plottrend method plots the data based on time series. The individual 
    method plots the data in vertical bar graphs along with scatters to indicate
    the maximum recorded values for each variable.
    """
        
    def plots(self, variable,resource, Country, Year, degree, scenario, plottype):
        try:
            ResourceList = self._data['Resource'].unique()
        except Exception as e:
            print(e)
            

        def splining(x , y, degree ):
            try:
                x = np.array(x)
                y = np.array(y)
                xnew = np.linspace(x.min(), x.max(), 1000) 
                spl = make_interp_spline(x, y, k=degree)  # type: BSpline
                smooth = spl(xnew)
            except Exception as e:
                self.logging.debug(e)
            return xnew, smooth    

        def plottrend(variable, scenario, Country):
            maxtemp = 0
            fig = plt.figure(figsize=(10, 10), dpi= 200, facecolor='w', edgecolor='k')
            gs = fig.add_gridspec(1, 1)
            fig.suptitle('A '+variable+' comparison', fontsize = 16)
            ax = fig.add_subplot(gs[0,0])
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.yticks(np.arange(0, 1, 0.1))
            for i in ResourceList:
                if scenario == 0:
                    trend = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country), variable].values
                    Year = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country), 'Year'].values
                    x , y = splining(Year,trend, degree)
                    plt.plot(x,y , label = i)
                else:

                   #Best Case Scenario
                   trend = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 2), variable].values
                   Year = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 2), 'Year'].values
                   x , y = splining(Year,trend, degree)
                   plt.plot(x,y, '--', label = i)
                   
                   #Worst Case Scenario
                   trend = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 1), variable].values
                   Year = self._data.loc[(self._data['Resource'] == i) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 1), 'Year'].values
                   x , y = splining(Year,trend, degree)
                   plt.plot(x,y, label = i)
                getmax = max(trend)
                if getmax-maxtemp > 0:
                    maxtemp = getmax
            plt.xlabel('Year')
            plt.ylabel(variable)
            plt.show
            ax.set_ylim([0,maxtemp+0.1])
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc='center right')    
            fig.tight_layout()
            fig.subplots_adjust(top=0.95, right = 0.85, left = 0.15)
            return fig
            
        def individual(variable, resource, scenario, Year):
            maxvalues = self.maxdict[variable]
            fig = plt.figure(figsize=(10, 10), dpi= 200, facecolor='w', edgecolor='k')
            gs = fig.add_gridspec(1, 1)
            fig.suptitle(variable+' score', fontsize = 16)
            ax = fig.add_subplot(gs[0,0])            
            plt.yticks(np.arange(0, 1, 0.1))
            if scenario == 0:
                _Year = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country), 'Year'].values.tolist().index(Year)
                trend = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country), variable].values[_Year]
                plt.bar([resource],trend, label = Country)
                plt.scatter([resource], maxvalues[3], label = "Max "+variable+" recorded is of "+str(maxvalues[2])+ " in "+str(maxvalues[1])+" "+str(maxvalues[0]) )
            else:
               #Best Case Scenario
               _Year = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 2), 'Year'].values.tolist().index(Year)
               trend = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 2), variable].values[_Year]
               plt.bar([resource],trend, label = Country)
               

               #Worst Case Scenario
               _Year = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 1), 'Year'].values.tolist().index(Year)
               trend = self._data.loc[(self._data['Resource'] == resource) & (self._data['Country'] == Country) & (self._data['RRScenario'] == 1), variable].values[_Year]               
               plt.bar([resource],trend, label = Country)
            plt.ylabel(variable)
            plt.show
            ax.set_ylim([0.00,maxvalues[3]+0.10])
            handles, labels = ax.get_legend_handles_labels()
            labels = [ '\n'.join(wrap(l, 10)) for l in labels ]
            fig.legend(handles, labels, loc='center right')    
            fig.tight_layout()
            fig.subplots_adjust(top=0.95, right = 0.85, left = 0.15)
            return fig, self._data
        
        try:
            if plottype == "trend":
                fig = plottrend(variable, scenario, Country)
            elif plottype == "individual":
                fig = individual(variable, resource, scenario, Year)
        except Exception as e:
            self.logging.debug(e)

        
        return fig
            
            
    