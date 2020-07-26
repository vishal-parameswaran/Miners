import time
import timeit
start = timeit.default_timer()
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup as BSoup
from urllib.parse import urlsplit, parse_qs

driver = webdriver.Chrome()
driver.get("https://www.99acres.com/search/property/rent/residential-all/electronic-city-bangalore-south?search_type=QS&refSection=GNB&search_location=NRI&lstAcn=NR_R&lstAcnId=-1&src=CLUSTER&preference=R&selected_tab=4&city=217&res_com=R&property_type=R&isvoicesearch=N&keyword_suggest=electronic%20city%2C%20bangalore%20south%3B&bedroom_num=2&fullSelectedSuggestions=electronic%20city%2C%20bangalore%20south&strEntityMap=W3sidHlwZSI6ImxvY2FsaXR5In0seyIxIjpbImVsZWN0cm9uaWMgY2l0eSwgYmFuZ2Fsb3JlIHNvdXRoIiwiQ0lUWV8yMTcsIExPQ0FMSVRZXzIyNTksIFBSRUZFUkVOQ0VfUiwgUkVTQ09NX1IiXX1d&texttypedtillsuggestion=electr&refine_results=Y&Refine_Localities=Refine%20Localities&action=%2Fdo%2Fquicksearch%2Fsearch&suggestion=CITY_217%2C%20LOCALITY_2259%2C%20PREFERENCE_R%2C%20RESCOM_R&searchform=1&locality=2259&price_min=null&price_max=15000")
property_list = []
noOfAds = int(driver.find_element_by_class_name("SRHeading").get_attribute("innerHTML").split(" ")[0].strip())
noOfScrolls = (noOfAds - 31)//30
for i in range(0,noOfScrolls):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
bs_obj = BSoup(driver.page_source, 'html.parser')
counter = 1
div = bs_obj.findAll('div',attrs={'class':'flex relative clearfix m-srp-card__container'})
for i in div:
    location = i.findAll('a', {"class":"m-srp-card__title"})[0].text
    
    location = location.replace("\n"," ")
    location = location.replace("  "," ")
    if "Apartment" in location :
        apartment = "Apartment"
    elif "Builder Floor" in location :
        apartment = "Builder Floor"
    else:
        apartment = "House"
    
    location = location.split(" ")
    size = "None"
    if "sqft" in location[::-1]:
        size = " ".join(location[-3::])
        location = location[location.index("rent") + 2:-3:]
        location = " ".join(location)
    else:
        location = location[location.index("rent") + 2::]
        location = " ".join(location)
    price = 0
    if len(i.findAll('span', {"class":"m-srp-card__price"})) > 0:
        price = i.findAll('span', {"class":"m-srp-card__price"})[0].text.replace("\n"," ")
    title = i.findAll('div', {"class":"m-srp-card__summary__title"})
    info = i.findAll('div', {"class":"m-srp-card__summary__info"})
    counter +=1
    print(counter)
    titleinfodict = {}
    titleList = []
    infoList = []
    for i in title:
        titleList.append(i.text.replace("\n","").strip())
    for i in info:
        infoList.append(i.text.replace("\n","").strip())
    titleinfodict = dict(zip(titleList, infoList))   
    if i.findAll('div', {"class":"m-srp-card__link--nearby"}):
        area = str(i.find('div', {"class":"m-srp-card__link--nearby"})["data-link"]).replace("\n"," ") if i.find('div', {"class":"m-srp-card__link--nearby"})["data-link"]  else "No Address" 
    else:
        area = "None"
    
    if area != "None":
        query = urlsplit(area).query
        params = parse_qs(query)
        latlong = params["lat"][0] + "," + params["longt"][0]
    else:
        latlong = "0.0,0.0"   
    property_list.append({"location":location,"size":size,"price":price,"latlong":latlong,"furnishing":titleinfodict["furnishing"] if "furnishing" in titleinfodict.keys() else "None","tenant":titleinfodict["tenants preferred"] if "tenants preferred"  in titleinfodict.keys() else "None","bathroom":titleinfodict["bathroom"] if "bathroom" in titleinfodict.keys() else "None"})
driver.close()

df = pd.DataFrame(property_list)
df.to_csv("properties.csv", index=False)
stop = timeit.default_timer()
print('Time: ', stop - start)  