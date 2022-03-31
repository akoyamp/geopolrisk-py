# Copyright 2020-2021 by Anish Koyamparambath and University of Bordeaux. All Rights Reserved.
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



"""
A simple guided step by step method for new users. This method can be called 
to any console based application if needed.
"""
#Method 4   
def simplerun(self):
#4.1 Call Method 1
    self.run()

def matchwords(word, List):
    word = word.lower()
    List = [x.lower() for x in List]
    if word in List:
        index = List.index(word)
        return index
    else:
        return -1
    
    

"""
List of available production information of metals which is later cross
verified for confirmation with the hs code. Also, the production information
is organized using the common name of the raw material which can later be altered
when automatic download of data is created.
"""
#4.2 Extracting data from linking database
Metals = self.resource.id.tolist()
HS = self.resource.hs.tolist()

"""
Connect country to country codes. These codes and files are only necessary
for guided run.
"""
#4.3 Extracting data from ISO country codes database
Country = self.reporter.Country.tolist()


"""
Following section gets the input of the resource/raw material from the user.
Keeping in mind the possibility of error from the user, get close matches 
library is used and reverified by the user. If found cumbersome an additional 
code to verify letter to letter can be created. The input is fed as key to 
fetch the resource hscode to be used in the API. Sections 4.5 also follows
the same pattern.
"""
#4.4 Input information on raw material
_exit = True
while _exit:
    print('Enter the name the resource whose supply risk you want to assess or type exit to exit')
    metal = input('Resource Name : ')
    Metalcloselist = get_close_matches(metal, Metals)
    if matchwords(metal, Metals) > -1:
        resource = Metals[matchwords(metal, Metals)]
        print("Selected resource is {} \n".format(resource))
        _exit = False
    elif len(Metalcloselist) > 1:
        print("The following metals are found close to your query ")
        print(Metalcloselist)
        try:
            index = int(input("Enter the selected resources as 1, 2 etc., :" ))
            resource = Metalcloselist[index - 1]
            print("Selected resource is {} \n".format(resource))
            _exit = False
        except ValueError:
            print("Please enter proper value!")
    elif len(Metalcloselist) == 0 and metal.lower() != "exit":
        print("The entered resource is not found")
    elif len(Metalcloselist) == 1 and metal != Metalcloselist[0]:
        print("The entered resource is not found")
    elif metal.lower() == "exit":
        sys.exit(1)
    else:
        resource = Metalcloselist[0]
        print("Selected resource is {} \n".format(resource))
        _exit = False
        
"""
self.resource countains data that is formated to general audience. i.e
a description of a hs code is more detailed and not usually known to
every user. Hence it is concised to the detail of the raw material name.
However, for the assessment, neither the description nor consice name
can be used and hence the following code extracts the hscode of the 
raw material.
"""
metal = resource
HSCode = HS[Metals.index(resource)]

#4.5 Input information on country/region
_exit = True
while _exit:
    print('Enter the name the country whose supply risk you want to assess or type exit to exit')
    Ctry = input('Country Name : ')
    countrycloselist = get_close_matches(Ctry, Country)
    if matchwords(Ctry, Country) > -1:
        country = Country[matchwords(Ctry, Country)]
        print("Selected country is {} \n".format(country))
        _exit = False
    elif len(countrycloselist) > 1:
        print("The following countries are found close to your query ")
        print(countrycloselist)
        try:
            index = int(input("Enter the selected country as 1, 2 etc., :" ))
            country = countrycloselist[index-1]
            print("Selected country is {} \n".format(country))
            _exit = False
        except ValueError:
            print("Please enter a proper value!")
    elif len(countrycloselist) == 0 and metal.lower() != "exit":
        print("The entered Country not found")
    elif metal.lower() == "exit":
        raise APIError
    else:
        country = countrycloselist[0]
        print("Selected country is {} \n".format(country))
        _exit = False
        
"""
Similar to hscode data, the assessment requires the iso digit code of
the country/region in question.
"""
reporter = self.reporter.iloc[Country.index(country),0]


_exit = True
while _exit:
    period = input("Enter the year of assessment :")
    try:
        period = int(period)
        _exit = False
    except Exception as e:
        self.logging.debug(e)

_exit = True
while _exit:
    print("Enter the rate of domestic recycling input of the raw material (in fractions) or type exit to exit")
    recyclingrate = input("Enter the recycling input rate: ")
    try:
        if float(recyclingrate) in range(0,101):
            recyclingrate = float(recyclingrate)
            _exit = False
        elif recyclingrate.lower() == 'exit':
            raise APIError
    except Exception as e:
        print("Provide correct inputs! Try again")
        self.logging.debug(e)
        

print("Select 0 for assuming a best case scenario where the imports from a riskier country is reduced")
print("Select 1 for assuming a worst case scenario where the imports from a stable country is reduced")
scenario = input("Select 1 or 0: ")

_exit=True
while _exit:
    try:
        if int(scenario) in [0, 1]:
            scenario = int(scenario)
            _exit = False
    except Exception as e:
        print("Provide correct inputs! Try again")
        self.logging.debug(e)


#4.6 Calculating GeoPolRisk, calling method from api module
print("Calculating the GeoPolRisk of "+str(resource)+" for "+
str(country)+" over the period "+str(period))

"""
Raw material name as defined in the hs file is important to reassure the user
of which kind of assessment they are following. The following code has no other 
purpose.
"""
#4.7 Extracting information of hs files
try:
    hs_element = self.commodity.iloc[self.commodity.HSCODE.to_list().index(HSCode),2]
except Exception as e:
    self.logging.debug(e)
    raise APIError
print("Info: The HS code used for the analysis is "+str(hs_element))

#4.8 API CALL
self.TotalCalculation(period = int(period), 
                      reporter = int(reporter), 
                      HSCode = int(HSCode),
                      recyclingrate = recyclingrate,
                      scenario = scenario)

print("The GeoPolRisk Value for "+metal+" during "+str(period)+" for "+country+" is "+str(round(self.GPRS,3)))
print("The Geopolitical supply risk potential characterization factor calculated is {} $/metric tonne".format(str(round(self.GPSRP,3))))
self.endlog()

