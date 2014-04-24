#import cherrypy
import urllib
import urllib2
import sys
import os
import tempfile
import uuid
import shutil
import datetime
import string
import math
import Image
import sqlite3
import StringIO
from types import *

class GlobalMercator(object):

	def __init__(self, tileSize=256):
		"Initialize the TMS Global Mercator pyramid"
		self.tileSize = tileSize
		self.initialResolution = 2 * math.pi * 6378137 / self.tileSize
		# 156543.03392804062 for tileSize 256 pixels
		self.originShift = 2 * math.pi * 6378137 / 2.0
		# 20037508.342789244

	def LatLonToMeters(self, lat, lon ):
		"Converts given lat/lon in WGS84 Datum to XY in Spherical Mercator EPSG:900913"

		mx = lon * self.originShift / 180.0
		my = math.log( math.tan((90 + lat) * math.pi / 360.0 )) / (math.pi / 180.0)

		my = my * self.originShift / 180.0
		return mx, my

	def MetersToLatLon(self, mx, my ):
		"Converts XY point from Spherical Mercator EPSG:900913 to lat/lon in WGS84 Datum"

		lon = (mx / self.originShift) * 180.0
		lat = (my / self.originShift) * 180.0

		lat = 180 / math.pi * (2 * math.atan( math.exp( lat * math.pi / 180.0)) - math.pi / 2.0)
		return lat, lon

	def PixelsToMeters(self, px, py, zoom):
		"Converts pixel coordinates in given zoom level of pyramid to EPSG:900913"

		res = self.Resolution( zoom )
		mx = px * res - self.originShift
		my = py * res - self.originShift
		return mx, my

	def MetersToPixels(self, mx, my, zoom):
		"Converts EPSG:900913 to pyramid pixel coordinates in given zoom level"

		res = self.Resolution( zoom )
		px = (mx + self.originShift) / res
		py = (my + self.originShift) / res
		return px, py

	def PixelsToTile(self, px, py):
		"Returns a tile covering region in given pixel coordinates"

		tx = int( math.ceil( px / float(self.tileSize) ) - 1 )
		ty = int( math.ceil( py / float(self.tileSize) ) - 1 )
		return tx, ty

	def PixelsToRaster(self, px, py, zoom):
		"Move the origin of pixel coordinates to top-left corner"

		mapSize = self.tileSize << zoom
		return px, mapSize - py

	def MetersToTile(self, mx, my, zoom):
		"Returns tile for given mercator coordinates"

		px, py = self.MetersToPixels( mx, my, zoom)
		return self.PixelsToTile( px, py)

	def TileBounds(self, tx, ty, zoom):
		"Returns bounds of the given tile in EPSG:900913 coordinates"

		minx, miny = self.PixelsToMeters( tx*self.tileSize, ty*self.tileSize, zoom )
		maxx, maxy = self.PixelsToMeters( (tx+1)*self.tileSize, (ty+1)*self.tileSize, zoom )
		return ( minx, miny, maxx, maxy )

	def TileLatLonBounds(self, tx, ty, zoom ):
		"Returns bounds of the given tile in latutude/longitude using WGS84 datum"

		bounds = self.TileBounds( tx, ty, zoom)
		minLat, minLon = self.MetersToLatLon(bounds[0], bounds[1])
		maxLat, maxLon = self.MetersToLatLon(bounds[2], bounds[3])

		return ( minLat, minLon, maxLat, maxLon )

	def Resolution(self, zoom ):
		"Resolution (meters/pixel) for given zoom level (measured at Equator)"

		# return (2 * math.pi * 6378137) / (self.tileSize * 2**zoom)
		return self.initialResolution / (2**zoom)

	def ZoomForPixelSize(self, pixelSize ):
		"Maximal scaledown zoom of the pyramid closest to the pixelSize."

		for i in range(30):
			if pixelSize > self.Resolution(i):
				return i-1 if i!=0 else 0 # We don't want to scale up

	def GoogleTile(self, tx, ty, zoom):
		"Converts TMS tile coordinates to Google Tile coordinates"

		# coordinate origin is moved from bottom-left to top-left corner of the extent
		return tx, (2**zoom - 1) - ty

	def QuadTree(self, tx, ty, zoom ):
		"Converts TMS tile coordinates to Microsoft QuadTree"

		quadKey = ""
		ty = (2**zoom - 1) - ty
		for i in range(zoom, 0, -1):
			digit = 0
			mask = 1 << (i-1)
			if (tx & mask) != 0:
				digit += 1
			if (ty & mask) != 0:
				digit += 2
			quadKey += str(digit)

		return quadKey



# parameters:
#     tileURL:
#          URL where map cache tiles are stored
#          example: www.myserver.com/var/www/mapper/aquifers
#
#     ptInfo:
#          Comma separated tuple describing z coordinate, x coordinate, y coordinate
#          z = Google/Bing/ESRI API zoom level
#          x = Spherical Mercator x coordinate
#          y = Spherical Mercator y coordinate
#          (you could argue that this argument should be more generic, to include
#          for example, longitude and latitude. However this app server is about
#          web mapping and map caches. If the map cache's map projection is something
#          other than web mercator, a developer will to add that functionality.)
#
#     cacheInfo:
#          Comma separted tuple describe cache layer name, cache format, and image extention
#          name = cache layer name. Can be anything, but is also the name of the sqlite database name
#          format = constant indicating the map cache naming "standard" used. Values include TMS, ESRI
#               TMS = z/x/y
#               ESRI = the ESRI tile naming is based on Lxx/Rxxxxxxxx/Cxxxxxx.<extension>
#                      where L=Level, R=Row, and C=Column.
#                      The Level numbers are 0-19 in decimal integers
#                      The Row and Column numbers are  hexidecimal numbers padded with zeros to a filename width of 9 characters.
#                      For example, L12/R00000615/C000002fe.png
#          extension = filename extension for cache's image file format, e.g. png

def tileRGBValue():

	tileURL = request.vars["tileURL"]
	ptInfo = request.vars["ptInfo"]
	cacheInfo = request.vars["cacheInfo"]

	if tileURL == None:
		return "Error Code: Invalid URL argument: tile url"
	if ptInfo == None:
		return "Error Code: Invalid URL argument: point info"
	if cacheInfo == None:
		return "Error Code: Invalid URL argument: cache info"

	# the tile URL should have a path separator
	if tileURL[:1] != "/":
		tileURL = tileURL + "/"

	# tokenize the ptInfo fields
	ptParts = ptInfo.split(",")

	# if there are three values assume, z, x, y
	if len(ptParts) == 3:
		zoomLevel = int(ptParts[0])
		mercX = float(ptParts[1])
		mercY = float(ptParts[2])
	else:
		return "Error Code: Invalid URL argument: point info"

	# tokenize the cacheInfo fields
	cacheParts = cacheInfo.split(",")

	# if there are three values then check values
	if len(cacheParts) == 3:
		cacheName = cacheParts[0]
		cacheFormat = cacheParts[1]
		cacheExt = cacheParts[2]
	else:
		return "Error Code: Invalid URL argument: cache info"

	# first parameter is the cache name. If there is no corresponding sqlite database in
	# the lookup directory then we can't continue. Note the extension .db is used for
	# the sqlite database file, but this is not an actual standard name.

	cacheQuery =  (mapcachedb.caches.name == cacheName)
	cacheSet = mapcachedb(cacheQuery)
	cacheRows = cacheSet.select(mapcachedb.caches.name)
	
	if len(cacheRows) == 0:
		return "Error: Cache Layer Lookup Database Not Found"

	# second parameter is the tile type which defines the tile naming structure
	if cacheFormat != "TMS":
		if cacheFormat != "ESRI":
			return "Error: Cache Type must be either 'TMS' or 'ESRI'"

	# the cache image files extension can be anything or nothing, so no point in
	# checking now - we check later when trying to retrieve the tile.

	# create the object for transformations
	mercator = GlobalMercator()

	# for the zoom level, we need to find the tile index. Since this is the TMS tiling format
	# so we convert it to the google tiling format
	tileX, tileY = mercator.MetersToTile(mercX, mercY, zoomLevel)
	googleX, googleY = mercator.GoogleTile(tileX, tileY, zoomLevel)

	# build the tile name
	tileFile = "http://" + tileURL

	# the ESRI tile naming is based on Lxx/Rxxxxxxxx/Cxxxxxx.png
	if cacheFormat == "ESRI":

		if zoomLevel < 10:
			esriLevel = "L0" + str(zoomLevel)
		else:
			esriLevel = "L" + str(zoomLevel)

		# note the ESRI ROW is the the googleY value
		esriRow =  "R" +  paddedHex(googleY)
		esriCol =  "C" +  paddedHex(googleX)
		tileFile = tileFile + esriLevel + "/" + esriRow + "/" + esriCol + "." + cacheExt

	else:
		tileFile = tileFile + zoomLevel + "/" + mercX + "/" + mercY + "." + cacheExt

	# we have the point the user clicked on and we figured out from that
	# coordinate which tile was clicked on. Now we need the origin of that tile
	mercXmin, mercYmin, mercXmax, mercYmax = mercator.TileBounds(tileX, tileY, zoomLevel)

	# next convert the mercator coordinates back to pixels coordinates. The pixels
	# coordinates are the coordinates if the zoom level were one gigantic image
	xpixO1, ypixO1 = mercator.MetersToPixels(mercXmin, mercYmax, zoomLevel)

	# the functions return TMS pixels, so we have to convert to google rasters
	# which simply reverses the y-scale
	xpixO2, ypixO2 = mercator.PixelsToRaster(xpixO1, ypixO1, zoomLevel)

	# do the same procedure thing for the selected point
	xpixG1, ypixG1 = mercator.MetersToPixels(mercX, mercY, zoomLevel)
	xpixG2, ypixG2 = mercator.PixelsToRaster(xpixG1, ypixG1, zoomLevel)

	# the difference in coordinates between the (G)iven pixel and
	# the (O)origin pixel is the pixel offset in the tile.
	offsetX = int((xpixG2 - xpixO2))
	offsetY = int((ypixG2 - ypixO2))

	# at this point we know the map tile's filename and the pixel in that tile where the user
	# clicked. Now we get the image, get the RGB value at that point and map the values back
	# to the attributes using an SQLite database. We need to see if the tile file actually exists
	# and, if so, can we retrieve it successfully.
	tile = urllib.urlretrieve(tileFile)
	
	# TESTING CHANGE
	# instead of actually saving the tile file, tried just open the url instead.
	# it works, but does not work with PIL because PIL requires file-like objects
	# to implement read(), seek(), and tell() methods which urllib's file object
	# does not implement. So this works, but does not work with PIL
	#       tile = urllib.urlopen(tileFile)

	if tile[0] == "":
		return ("No Tile Found")
	
	try:
		# open the image file with PIL
		im = Image.open(tile[0])

	except:
		return("Unable to Access Tile")

	# there can be lots of image formats, but unless the image is an RGB image,
	# there's not much utility in a program that looks up attributes using RGB values.
	# However, with web mapping overlays, the Alpha channel can be important, so we
	# need to support RGBA images. Whatever image we get we have to convert to RGBA
	# if it's not already
	if im.mode != "RGBA":
		im = im.convert("RGBA")

	# get the pixel's rgba value
	r,g,b,a = im.getpixel((offsetX, offsetY))

	# since we have the rgb value, we should close and delete the temp file
	del im
	os.remove(tile[0])

	# set the header info
	#cherrypy.response.headers['Content-Type'] = 'text/xml;charset=UTF-8'

	# return the tile value
	rgbRecord = lookupRGBValue(cacheRows[0].name, aquifersdb, r, g, b)
	
	return rgbRecord

#tileRGBValue.exposed = True

def paddedHex(x):

	# argument x is an integer, so convert it into a
	# hexadecimal number and then string
	xh = str(hex(x))

	# xh has the "0x" syntax convert to a string, so drop those
	xh = xh.lstrip("0x")

	# now pad the result
	return xh.zfill(8)

def lookupRGBValue(name, dbfile, r, g, b):

	# Each map cache or layer has a name. That name is also the name
	# for an SQLite database. For example, if the map cache has been
	# named aquifers, then there should be an SQLite database named
	# aquifers.db. Within the database there should be at least two
	# tables: rgb and fat. The table named rgb has only four fields,
	# all integer: id, red, green, blue. The table named fat stands
	# (f)eature (a)ttribute (t)able, a semi-generic/semi-ESRI term
	# for the table where feature attributes are stored. Two SQL
	# queries are used to get the feature attribute. A first query
	# is made against the rgb table and finds an ID based on the RGB
	# values. The ID is then used in a second query against the fat
	# table to return feature attribute values.

	try:
		# query the rgb value
		rgbQuery =  (dbfile.rgb.red == r) & (dbfile.rgb.green == g) & (dbfile.rgb.blue == b)
		rgbSet = dbfile(rgbQuery)
		rgbRows = rgbSet.select(dbfile.rgb.id)		
		
		fatQuery = (dbfile.fat.id == rgbRows[0].id)
		fatSet = dbfile(fatQuery)
		fatRows = fatSet.select(dbfile.fat.ALL)
		
		return str(fatRows[0])
				
	
	except:
		return("Problem reading values from database")

