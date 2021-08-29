# -*- coding: utf-8 -*-
"""
Created on Mon Aug 13 10:05:56 2021

@author: anish
"""
import pandas as pd ,numpy as np, matplotlib.pyplot as plt, sqlite3
from scipy.interpolate import make_interp_spline, BSpline
from matplotlib.ticker import MaxNLocator
from api import APIError
from GeoPolRisk import main  

class graphics(main):
    def __init__(self):
        try:
            self._data = pd.read_csv('./output/export.csv')
            self._dataDict = {}
        except Exception as e:
            self.logging.debug(e)
            raise APIError
        try:
            conn = sqlite3.connect('./lib/datarecords.db', isolation_level=None,
                       detect_types=sqlite3.PARSE_COLNAMES)
            db_df = pd.read_sql_query("SELECT * FROM recorddata", conn)
            db_df.to_csv('./output/database.csv', index=False)
        except Exception as e:
            self.logging.debug(e)
        
    def trendplots(self, variable,resource, economicunit, plottype):
        try:
            ResourceList = self._data['Resource'].unique()
        except Exception as e:
            print(e)
        try:
            for i in ResourceList:
                self.inrDict = {}
                temp = self._data.loc[(self._data['Resource'] == i)]
                temp = temp.loc[(temp['Country'] == economicunit)]
                self.inrDict['GeoPolRisk'] = temp.GeoPolRisk.to_list()
                self.inrDict['HHI'] = temp.HHI.to_list()
                self.inrDict['WTA'] = temp['Weighted Trade AVerage'].tolist()
                self.inrDict['Year'] = temp.Year.to_list()
                self.inrDict['RR'] = temp['Recycling Rate'].tolist()
                self.inrDict['RRScenario'] = temp['Recycling Scenario'].tolist()
                self._dataDict[i] = self.inrDict
        except Exception as e:
            self.logging.debug(e)
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

        def plottrend(variable, scenario):
            maxtemp = 0
            fig = plt.figure(figsize=(10, 10), dpi= 200, facecolor='w', edgecolor='k')
            gs = fig.add_gridspec(1, 1)
            fig.suptitle('A '+variable+' comparison', fontsize = 16)
            degree = 2
            ax = fig.add_subplot(gs[0,0])
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            plt.yticks(np.arange(0, 1, 0.1))
            for i in ResourceList:
                if scenario == 0:
                    trend = self._dataDict[i][variable]
                    Year = self._dataDict[i]['Year']
                    x , y = splining(Year,trend, degree)
                    plt.plot(x,y , label = i)
                else:
                   newdf = pd.DataFrame(self._dataDict[i])
                   temp = newdf.loc[(newdf['RRScenario'] == 1)]
                   #Best Case Scenario
                   trend = temp.variable.to_list()
                   Year = temp.Year.to_list()
                   x , y = splining(Year,trend, degree)
                   plt.plot(x,y, '--', label = i)
                   
                   newdf = pd.DataFrame(self._dataDict[i])
                   temp = newdf.loc[(newdf['RRScenario'] == 2)]
                   #Worst Case Scenario
                   trend = temp.variable.to_list()
                   Year = temp.Year.to_list()
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
            
        def individual(variable, resource, scenario, Year):
            fig = plt.figure(figsize=(10, 10), dpi= 200, facecolor='w', edgecolor='k')
            gs = fig.add_gridspec(1, 1)
            fig.suptitle(variable+' score', fontsize = 16)
            ax = fig.add_subplot(gs[0,0])            
            plt.yticks(np.arange(0, 1, 0.1))
            if scenario == 0:
                _Year = self._dataDict[resource]['Year'].index(Year)
                trend = self._dataDict[resource][variable][_Year]
                plt.bar([resource],trend, label = economicunit)
            else:
               newdf = pd.DataFrame(self._dataDict[resource])
               temp = newdf.loc[(newdf['RRScenario'] == 1)]
               #Best Case Scenario
               _Year = temp.Year.to_list().index(Year)
               trend = temp.variable.to_list()[_Year]
               plt.bar([resource],trend, label = economicunit)
               
               newdf = pd.DataFrame(self._dataDict[i])
               temp = newdf.loc[(newdf['RRScenario'] == 2)]
               #Worst Case Scenario
               _Year = temp.Year.to_list().index(Year)
               trend = temp.variable.to_list()[_Year]
               plt.bar([resource],trend, label = economicunit)
            plt.ylabel(variable)
            plt.show
            ax.set_ylim([0.00,trend+0.10])
            handles, labels = ax.get_legend_handles_labels()
            fig.legend(handles, labels, loc='center right')    
            fig.tight_layout()
            fig.subplots_adjust(top=0.95, right = 0.85, left = 0.15)
        
        def scenario(variable,resource, plottype):
            if plottype == "trend":
                plottrend(variable, 1)
            elif plottype == "individual":
                individual(variable,resource, 1)
        
        individual('GeoPolRisk','Bismuth', 0,2016 )
            
            
            
graphics= graphics()
graphics.trendplots(2,"","Australia","")
    