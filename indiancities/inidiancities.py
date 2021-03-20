from bs4 import BeautifulSoup
import requests
import re
import json
import time

class CityList:
	def __init__(self):
		#List of district name of india
		self.dist_name_list=["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]

		#base url to fetch data from distict
		self.dist_base_url="https://en.wikipedia.org/w/index.php?title=Category:Cities_and_towns_in_India_by_district&from="

		#base url of wikipedia
		self.base_url="https://en.wikipedia.org"

		#list contain  districts address
		self.dist_add_list=list()
		self.cur_id=1
		self.cities_data={}

	def getDistAdd(self):
		#Fetch all district of India and store in list as address
		#using Address we can fetch all the cities of particular district
		for dist_name in self.dist_name_list:
		 	#url for district which start with name "dist_name"
		 	url=f"{self.dist_base_url}{dist_name}"
		 	source= requests.get(url).text
		 	#Response HTML
		 	soup= BeautifulSoup(source,'lxml')

		 	#Format to get district address
		 	dist_name_container=soup.find(class_="mw-content-ltr").find(class_="mw-content-ltr")
		 	for loc in dist_name_container.find("ul").find_all("li"):
		 		self.dist_add_list.append(self.base_url+loc.find("a")['href'])

		for dist_add in self.dist_add_list:
			self.getCitiesAdd(dist_add)
			time.sleep(0.001)

	def getCitiesAdd(self,dist_url):
		cities_add_list=list()
		#Request wikipedia to get cities of requested district url
		source= requests.get(dist_url).text
		soup= BeautifulSoup(source,'lxml')

		#list of addresses of cities
		loc_parent_list=soup.find(id="mw-pages").find(class_="mw-content-ltr").find_all("a")
		#Store the address in list
		for loc in loc_parent_list:
			cities_add_list.append(self.base_url+loc['href'])

		#get district name from dist_url
		dist_name=dist_url.split("_in_")[-1]\
						  .split("_district")[0]\
						  .replace("_"," ")\
						  .strip()

		for city_add in cities_add_list:
			self.getCitiesDetails(dist_name,city_add)


	def getCitiesDetails(self,dist_name,city_url):
		#Request wikipedia to get city detail 
		source= requests.get(city_url).text
		soup= BeautifulSoup(source,'lxml')
		try:
			#get the latitude/longitude stored in Format (78°17′00″)(deg min sec)
			longi=soup.find(class_="longitude").get_text()[ :-1]
			latti=soup.find(class_="latitude").get_text()[ :-1]

			# convert the latitude/longitude from (deg min sec) format to (deg.deg) format
			deg_latt=0.0
			deg_longi=0.0
			latt_matches=self.getLoc(latti)
			long_matches=self.getLoc(longi)

			#iterate through match
			#match[3]=sec
			#match[2]=min
			#match[1]=deg
			# 60sec=1 min
			# 60min=1 deg
			for i in range(3,0,-1):
				try:
					if(i!=1):
						deg_latt=(deg_latt+int(latt_matches[i]))/60
						deg_longi=(deg_longi+int(long_matches[i]))/60

					else:
						deg_latt =round(deg_latt+int(latt_matches[i]),5)
						deg_longi=round(deg_longi+int(long_matches[i]),5)

				except (TypeError,IndexError):
					pass

		#if city detail obtainted from cit _url  does not contain longitude/lattitde 
		except AttributeError:
			deg_longi=None
			deg_latt=None

		#Get state name 
		try:
			state=soup.find(class_="mergedrow").find("td").find_all("a")
			if(len(state)>1):
				state=state[1].get_text()
			else:
				state=state[0].get_text()

			#get city name from url
			city=city_url.split("/")[-1]
			city=re.sub(r',.*',"",city)
			city=re.sub(r"_"," ",city)

		# If city does not have state,make state and city to null 
		except (AttributeError,IndexError):
			state=None
			city=None
		if(city is not None or state is not None ):
			self.storeCitiesDetails(deg_longi,deg_latt,city,state,dist_name)


	def storeCitiesDetails(self,longi,latti,city_name,state_name,dist_name):
		#Data Format

		# "cityName":{
		# 	"id":id,
		# 	"Name":cityName,
		# 	"State":state,
		# 	"District":district,
		# 	"Longitude":longitude(DD.DDDD)
		# 	"Latitude":latitiude(DD.DDDD)
		# }

		if(city_name!=None or state_name!=None):
			self.cities_data[city_name]={"id":self.cur_id,"Name":city_name,"State":state_name,"District":dist_name,"Longitude":str(longi) if longi is not None else str("N/A"),
								"Latitude":str(latti) if latti is not None else str("N/A")}
			self.cur_id+=1

			print(self.cities_data[city_name])

	def saveCitiesDet(self):
		print(self.cities_data)
		with open("indian_cities.json","w") as file:
			json.dump(self.cities_data,file,indent=2)


	#The matched result contain degree ,minute and second of given latitude/longitude
	def getLoc(self,src_string):
		# lattitude/longitude=89°
		patt1=r"(\d+)."

		# lattitude/longitude=27°12′
		patt2=r"(\d+).(\d+)."

		# lattitude/longitude=78°17′00″
		patt3=r"(\d+).(\d+).(\d+)."

		patt3_res=re.search(patt3,src_string)
		patt2_res=re.search(patt2,src_string)
		patt1_res=re.search(patt1,src_string)

		if(patt3_res): return patt3_res
		elif(patt2_res):return patt2_res
		elif (patt1_res):return patt1_res








if __name__=="__main__":
	cityList=CityList()
	cityList.getDistAdd()
	cityList.saveCitiesDet()