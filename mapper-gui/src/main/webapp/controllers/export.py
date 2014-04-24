import urllib
from xml.dom import minidom

import datetime
import sys
import os
import tempfile
import uuid
import shutil
import datetime
import string
import zipfile
import xlwt
import shapefile

# url and parameters to query site file and deliver output file
# parameters:
#     Bounding Box: bBox=xmin,ymin,xmax,ymax
#
#     siteCodes:    scodes="TSC" where T=type,       1=SW,     2=GW,      3=SP, 4=AT, 5=OT
#                                      S=status,     1=Active, 0=Inactive
#                                      C=data codes, 1=all,    2=iv,      3=dv, 4=qw, 5=pk, 6=sv, 7=ad
#
#     File format:  fformat=1=html, 2=txt, 3=Excel, 4=csv, 5=rdb, 6=kml, 7=shp

#create a global variables
global globalSiteRecords
global global_web_query_url

def exportFile():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]
	
	# verify url arguments - to some degree - we are sending the url not the user so it should be
	# reasonably well formed
	if bbox == None:
		return "Error Code: Invalid URL argument: bounding box"

	if scodes == None:
		return "Error Code: Invalid URL argument: site codes"

	# build base url
	web_query_url = "http://waterservices.usgs.gov/nwis/site?"

	# add the bouunding box parameters
	web_query_url = web_query_url + "bBox=" + bbox

	# add format
	web_query_url = web_query_url + "&format=mapper,1.0"	

	# add the sitetype
	web_query_url = web_query_url + "&siteType=" + getSiteType(scodes)

	# decode the site status
	web_query_url = web_query_url + "&siteStatus=" + getSiteStatus(scodes)

	# add the dataType
	web_query_url = web_query_url + "&hasDataTypeCd=" + getSiteDataCode(scodes)

	# pass the query to the NWIS Sitefile Web Service
	try:
		sitesDOM  = minidom.parse(urllib.urlopen(web_query_url))

	except:
		return "Error reading DOM"

	# loop through the nodes 
	# have to move to the "sites" node because there is also a "colocated sites" node
	for rootNode in sitesDOM.getElementsByTagName("sites"):

		# build a header record, note that siteRecord is a list
		# siteRecords = [("site_no", "site_name", "cat_code", "agency", "longitude", "latitude", "url")]
		siteRecords = []

		# get the site data from each site node
		for sites in rootNode.getElementsByTagName("site"):

			# build the tuple records
			site_no = sites.getAttribute("sno")
			site_name = sites.getAttribute("sna")
			site_cat  = sites.getAttribute("cat")
			site_agc = sites.getAttribute("agc")
			site_lng = sites.getAttribute("lng")
			site_lat = sites.getAttribute("lat")
			site_url = "http://waterdata.usgs.gov/nwis/inventory?agency_code=" + site_agc + "&site_no=" + site_no

			# create a new list from the variables
			siteRecord = [site_no, site_name, site_cat, site_agc, site_lng, site_lat, site_url]

			# append to siteRecords tuple
			siteRecords.append(siteRecord)

	#create a global variable to hold siteRecords for use in export funcitons
	session.globalSiteRecords = list(siteRecords)
	session.global_web_query_url = web_query_url

	#insert metadata as first row in siteRecords
	metaData = getHTMLMetaData(bbox, scodes, len(siteRecords))
	siteRecords.insert(0,metaData)
	return dict(message=siteRecords)

def sendTXT():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]

	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, len(session.globalSiteRecords))

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	#fp.write("\n\n")

	# close the file
	fp.close()

	txtOut  = ""
	# add each agency code each site number separated by a newline
	for site in session.globalSiteRecords:
		site_agency = formatAgency(site[3])
		txtOut += site_agency + site[0] + "\r\n"

	# the last character is a comma, but instead of checking
	# during the loop, we will just chop it off the end
	i = len(txtOut) - 1
	txtOut = txtOut[0:i]
	txtOut += "\r\n"

	# open the data fle
	# create the metadata file
	fp = open("NWISMapperExport.txt", "w")
	fp.write(txtOut)
	fp.close()

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")
	
	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")
	zipFile.write("NWISMapperExport.txt")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def sendExcel():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]
	
	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, len(session.globalSiteRecords))

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	#fp.write("\n\n")

	# close the file
	fp.close()

	# create an excel workbook
	fpBook = xlwt.Workbook()
	# create a worksheet in the workbook
	nwisSheet = fpBook.add_sheet("NWIS Mappper Export Sheet")

	# write a header for the data, start with row 2
	nwisSheet.write(1, 0, "SiteNumber")
	nwisSheet.write(1, 1, "SiteName")
	nwisSheet.write(1, 2, "SiteCategory")
	nwisSheet.write(1, 3, "SiteAgency")
	nwisSheet.write(1, 4, "SiteLongitude")
	nwisSheet.write(1, 5, "SiteLatitude")
	nwisSheet.write(1, 6, "SiteNWISURL")

	# add each site data to the spreadsheet
	row = 2
	for site in session.globalSiteRecords:
		siteNum = site[0]
		siteName = site[1]
		siteCat = site[2]
		siteAgc = site[3]
		siteLng = site[4]
		siteLat = site[5]
		siteURL = site[6]
		nwisSheet.write(row, 0, siteNum)
		nwisSheet.write(row, 1, siteName)
		nwisSheet.write(row, 2, siteCat)
		nwisSheet.write(row, 3, siteAgc)
		nwisSheet.write(row, 4, siteLng)
		nwisSheet.write(row, 5, siteLat)
		nwisSheet.write(row, 6, xlwt.Formula('HYPERLINK("' + siteURL + '";"Access Data")'))
		row = row + 1

	# create the excel file
	fpBook.save("NWISMapperExport.xls")

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")

	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")
	zipFile.write("NWISMapperExport.xls")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName  + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def sendCSV():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]	

	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, len(session.globalSiteRecords))

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	fp.write("\n\n")

	# close the file
	fp.close()

	csvOut  = "SiteNumber, SiteName, SiteCategory, SiteAgency, SiteLongitude, SiteLatitude, SiteNWISURL\n"
	for site in session.globalSiteRecords:
		csvRec = ""
		for i in range(0,7):
			if i == 4 or i == 5:
				csvRec += site[i] + ","
			else:
				csvRec += '"' + site[i] + '"' + ","

		# the last character is a comma, but instead of checking
		# during the loop, we will just chop it off the end and add a linefeed
		i = len(csvRec) - 1
		csvRec = csvRec[0:i]
		csvRec += "\n"

		csvOut += csvRec

	# open the data fle
	# create the metadata file
	fp = open("NWISMapperExport.csv", "w")
	fp.write(csvOut)
	fp.close()

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")
	
	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")
	zipFile.write("NWISMapperExport.csv")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName  + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def sendRDB():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]
	
	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, len(session.globalSiteRecords))

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	fp.write("\n\n")

	# close the file
	fp.close()

	rdbOut = "# Tab-delimited output format (http://waterdata.usgs.gov/nwis?tab_delimited_format_info)\n"
	rdbOut += "SiteNumber\tSiteName\tSiteCategory\tSiteAgency\tSiteLongitude\tSiteLatitude\tSiteNWISURL\n"
	rdbOut += "25S\t50S\t2S\t10S\t15N\t15N\t100S\n"
	for site in session.globalSiteRecords:
		rdbOut += site[0] + "\t" + site[1] + "\t" + site[2]  + "\t" + site[3] + "\t" + site[4] + "\t" + site[5]  + "\t" +  site[6] + "\n"

	# open the data fle
	# create the metadata file
	fp = open("NWISMapperExport.rdb", "w")
	fp.write(rdbOut)
	fp.close()

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")

	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")
	zipFile.write("NWISMapperExport.rdb")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName  + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def sendKML():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]	

	#punt on this for now until a better solution, should only have to do one request
	sitesDOM  = minidom.parse(urllib.urlopen(session.global_web_query_url))

	#get KML version from web services
	fpKML = urllib.urlopen(session.global_web_query_url.replace("mapper,1.0","ge,1.0"))
	sitesKML = fpKML.read()

	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# the metadata includes the number of sites returned in the
	# request. For KML we don't know this because we just pass
	# KML straight through from the web service. So we have
	# count the number of sites from the KML
	nSites = 0
	for rootNode in sitesDOM.getElementsByTagName("Document"):
		nSites = 0
		# get the site data from each site node
		for sites in rootNode.getElementsByTagName("Placemark"):
			nSites = nSites + 1

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, nSites)

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	fp.write("\n\n")

	# close the file
	fp.close()

	# open the data fle
	# create the metadata file
	fp = open("NWISMapperExport.kml", "w")
	fp.write(sitesKML)
	fp.close()

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")

	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")	
	zipFile.write("NWISMapperExport.kml")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName  + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def sendShape():

	bbox = request.vars["bbox"]
	scodes = request.vars["scodes"]
	
	# change dir to the mappers exporter / temp director
	os.chdir(request.folder + '/uploads');

	# create a temporary directory name using a uuid
	tempDirName = str(uuid.uuid4())

	# create the directory
	os.mkdir(tempDirName)

	# change dir to the temp dir
	os.chdir(tempDirName)

	# build a metadata string from the scodes
	metaData = getMetaData(bbox, scodes, tempDirName, len(session.globalSiteRecords))

	# create the metadata file
	fp = open("Metadata.txt", "w")

	# write the metadata
	fp.write(metaData)
	fp.write("\n\n")

	# close the file
	fp.close()

	# create an shapefile writer object
	fpShape  = shapefile.Writer(shapefile.POINT)

	# shapefile fields
	fpShape.field("SITENO", "C", "25")
	fpShape.field("SITENAME", "C", "50")
	fpShape.field("CATEGORY", "C", "2")
	fpShape.field("AGENCY", "C", "10")
	fpShape.field("LONGDD", "C", "15" )
	fpShape.field("LATDD" , "C", "15")
	fpShape.field("SITEURL", "C", "100")

	# add points to the shapefile
	for site in session.globalSiteRecords:
		if (site[4] is not None) and (site[5] is not None): 
			siteNum = site[0]
			siteName = site[1]
			siteCat = site[2]
			siteAgc = site[3]
			siteLng = float(site[4])
			siteLat = float(site[5])
			siteURL = site[6]
	
			# create the geometry
			fpShape.point(siteLng, siteLat)
			fpShape.record(siteNum, siteName, siteCat, siteAgc, siteLng, siteLat, siteURL)
	fpShape.save("NWISMapperExport")

	# copy the readme file
	shutil.copyfile(request.folder + "static/templates/Readme.txt", "./Readme.txt")
	shutil.copyfile(request.folder + "static/templates/Readme.html", "./Readme.html")

	# copy the projection  file
	shutil.copyfile(request.folder + "static/templates/NWISMapperExport.prj", "./NWISMapperExport.prj")

	# now create the zip file
	zipFile = zipfile.ZipFile(tempDirName + ".zip", mode="w")

	# add the files
	zipFile.write("Readme.txt")
	zipFile.write("Readme.html")	
	zipFile.write("NWISMapperExport.shp")
	zipFile.write("NWISMapperExport.shx")
	zipFile.write("NWISMapperExport.dbf")
	zipFile.write("NWISMapperExport.prj")
	zipFile.write("Metadata.txt")
	zipFile.close()

	response.headers['Content-Type']='application/zip'
	response.headers['Content-Disposition'] = "attachment;filename=" + tempDirName  + ".zip"
	return open(request.folder + "/uploads/" + tempDirName+ "/" + tempDirName + ".zip")

def getSiteType(scodes):

	siteType = scodes[0]

	if siteType == "1":
		return "ES,GL,LK,OC,ST,WE"
	elif siteType == "2":
		return "GW,SB"
	elif siteType == "3":
		return "SP"
	elif siteType == "4":
		return "AT"
	elif siteType == "5":
		return "AG,AS,FA,LA"
	else:
		return ""


def getSiteStatus(scodes):

	siteStatus = scodes[1]

	if siteStatus == "1":
		return "active"
	else:
		return "inactive"


def getSiteDataCode(scodes):

	siteCode = scodes[2]

	if siteCode == "1":
		return "all"
	elif siteCode == "2":
		return "iv"
	elif siteCode == "3":
		return "dv"
	elif siteCode == "4":
		return "qw"
	elif siteCode == "5":
		return "pk"
	elif siteCode == "6":
		return "sv"
	elif siteCode == "7":
		return "ad"
	else:
		return ""

def getMetaData(bbox, scodes, GUID, nSites):

	# get current time and date
	currDateTime = datetime.datetime.now()

	metaData =  "Metadata for NWIS Sites exported from NWIS Mapper\r\n"
	metaData += "(Exporter Version 1.1.0)\r\n"
	metaData += "Time and Date data were exported: "
	metaData += currDateTime.strftime("%Y-%m-%d %H:%M") + "\r\n"
	metaData += "Request Number: " + GUID + "\r\n"
	metaData += "Number of sites in request: " + str(nSites) + "\r\n"
	metaData += "Longitude and Latitude extent of request:\r\n"
	metaData += "\tWest: "  + bbox.split(",")[0] + "\r\n"
	metaData += "\tSouth: " + bbox.split(",")[1] + "\r\n"
	metaData += "\tEast: "  + bbox.split(",")[2] + "\r\n"
	metaData += "\tNorth: " + bbox.split(",")[3] + "\r\n"

	# add the site type
	siteType = scodes[0]

	metaData += "Sites Type: "
	if siteType == "1":
		siteTypeText = "Surface-Water\r\n"
	elif siteType == "2":
		siteTypeText = "Groundwater\r\n"
	elif siteType == "3":
		siteTypeText = "Springs\r\n"
	elif siteType == "4":
		siteTypeText = "Atmospheric\r\n"
	elif siteType == "5":                
		siteTypeText = "Other\r\n"
	else:
		siteTypeText = "Unknown\r\n"

	metaData += siteTypeText

	# add the status
	siteStatus = scodes[1]

	metaData += "Sites Status: "
	if siteStatus == "1":
		siteStatusText = "Active\r\n"
	else:
		siteStatusText = "Inactive\r\n"

	metaData += siteStatusText

	# add the data type
	siteCode = scodes[2]

	metaData += "Requested type of data for sites: " 
	if siteCode == "1":
		siteCodeText = "All Data"
	elif siteCode == "2":
		siteCodeText = "Instantaneous Values"
	elif siteCode == "3":
		siteCodeText = "Daily Value"
	elif siteCode == "4":
		siteCodeText = "Water Quality"
	elif siteCode == "5":
		siteCodeText = "Peak Value"
	elif siteCode == "6":
		siteCodeText = "Measurements"
	elif siteCode == "7":
		siteCodeText = "Annual Water Data Report"
	else:
		siteCodeText = "Unknown"

	metaData += siteCodeText

	#write to log file
	#with open("/var/www/mapper/exporter/logs/log.txt", "a") as myfile:
	#	myfile.write(currDateTime.strftime("%Y-%m-%d %H:%M") + " UTC,ExportType:" + globalfformat + ",GUID:" + GUID + ",NumSites:" + str(nSites) + ",SiteType:" + siteTypeText.rstrip() + ",SiteStatus:"+ siteStatusText.rstrip() + ",SiteCode:" + siteCodeText + ",West:" + bbox.split(",")[0] + ",South:" + bbox.split(",")[1] + ",East:" + bbox.split(",")[2] + ",North:" + bbox.split(",")[3] + "\r\n")

	return metaData

def getHTMLMetaData(bbox, scodes, nSites):

	metaData = []

	# get current time and date
	currDateTime = datetime.datetime.now()

	metaData.append(currDateTime.strftime("%Y-%m-%d %H:%M") + " UTC")
	
	
	metaData.append(str(nSites))
	metaData.append([bbox.split(",")[0], bbox.split(",")[1], bbox.split(",")[2], bbox.split(",")[3]])

	# add the site type
	siteType = scodes[0]
	
	if siteType == "1":
		siteTypeText = "Surface-Water"
	elif siteType == "2":
		siteTypeText = "Groundwater"
	elif siteType == "3":
		siteTypeText = "Springs"
	elif siteType == "4":
		siteTypeText = "Atmospheric"
	elif siteType == "5":
		siteTypeText = "Other"
	else:
		siteTypeText = "Unknown"

	metaData.append(siteTypeText)

	# add the status
	siteStatus = scodes[1]

	if siteStatus == "1":
		siteStatusText = "Active"
	else:
		siteStatusText = "Inactive"

	metaData.append(siteStatusText)

	# add the data type
	siteCode = scodes[2]

	if siteCode == "1":
		siteCodeText = "All Data"
	elif siteCode == "2":
		siteCodeText = "Instantaneous Values"
	elif siteCode == "3":
		siteCodeText = "Daily Value"
	elif siteCode == "4":
		siteCodeText = "Water Quality"
	elif siteCode == "5":
		siteCodeText = "Peak Value"
	elif siteCode == "6":
		siteCodeText = "Measurements"
	elif siteCode == "7":
		siteCodeText = "Annual Water Data Report"
	else:
		siteCodeText = "Unknown"

	#add to metadata string
	metaData.append(siteCodeText);

	#write to log file
	#with open("/var/www/mapper/exporter/logs/log.txt", "a") as myfile:
	#	myfile.write(currDateTime.strftime("%Y-%m-%d %H:%M") + " UTC,ExportType:" + globalfformat + ",GUID:htmlTable,NumSites:" + str(nSites) + ",SiteType:" + siteTypeText + ",SiteStatus:"+ siteStatusText + ",SiteCode:" + siteCodeText + ",West:" + bbox.split(",")[0] + ",South:" + bbox.split(",")[1] + ",East:" + bbox.split(",")[2] + ",North:" + bbox.split(",")[3] + "\r\n")

	return metaData

def formatAgency(agency):

	if len(agency) == 0:
		return "USGS "

	if len(agency) == 5:
		return agency

	if len(agency) > 5:
		return agency[0:4]

	if len(agency) < 5:
		nSpaces = 5- len(agency)
		for i in range(nSpaces):
			agency = agency + " "
		return agency

	return "USGS "