// MJS 02/04/2014 

// global variables
var map,map_gw,map_sp,map_at,map_ot; 
var sidebar;
var exportURLmodal = exportURL;
var globalExportURL;
var mapArray = [];
var siteTypes;
var isMobile = false;
var lastZoomLevel_sw = 4;
var lastZoomLevel_gw = 4;
var lastZoomLevel_sp = 4;
var lastZoomLevel_at = 4;
var lastZoomLevel_ot = 4;
var clusterMarker;
var markerIcon;
var basemapNameArray = [["ESRIgrayBasemap","ESRI Gray","active"],["ESRIstreetsBasemap","ESRI Streets"],["ESRIimageryBasemap","ESRI Imagery"],["ESRIusaTopoBasemap","ESRI USA Topo"],["ESRInatGeoBasemap","ESRI Nat Geo"],["tnmBasemap","National Map"]];

//set up basemap layers
var ESRIgrayBasemap = L.tileLayer("http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {attribution: 'Copyright: &copy; 2013 Esri, DeLorme, NAVTEQ'});
var ESRIstreetsBasemap = L.tileLayer("http://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}", {attribution: 'Sources: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2013'});
var ESRIimageryBasemap = L.tileLayer("http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {attribution: 'Source: Esri, DigitalGlobe, GeoEye, i-cubed, USDA, USGS, AEX, Getmapping, Aerogrid, IGN, IGP, swisstopo, and the GIS User Community'});
var ESRIusaTopoBasemap = L.tileLayer("http://server.arcgisonline.com/ArcGIS/rest/services/USA_Topo_Maps/MapServer/tile/{z}/{y}/{x}", {opacity: 0.7,attribution: 'Copyright:&copy; 2013 National Geographic Society, i-cubed'});
var ESRInatGeoBasemap = L.tileLayer("http://services.arcgisonline.com/ArcGIS/rest/services/NatGeo_World_Map/MapServer/tile/{z}/{y}/{x}", {attribution: 'National Geographic, Esri, DeLorme, NAVTEQ, UNEP-WCMC, USGS, NASA, ESA, METI, NRCAN, GEBCO, NOAA, iPC>'});
var tnmBasemap = L.tileLayer('http://navigator.er.usgs.gov/tiles/tcr.cgi/{z}/{x}/{y}.png', {maxZoom: 20,attribution: '<a href="http://www.doi.gov">U.S. Department of the Interior</a> | <a href="http://www.usgs.gov">U.S. Geological Survey</a> | <a href="http://www.usgs.gov/laws/policies_notices.html">Policies</a>'});

//set up tile layers
var swActTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/sw_act_tms/{z}/{y}/{x}.png", {zIndex:999,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var swInaTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/sw_ina_tms/{z}/{y}/{x}.png", {zIndex:998,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var gwActTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/gw_act_tms/{z}/{y}/{x}.png", {zIndex:997,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var gwInaTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/gw_ina_tms/{z}/{y}/{x}.png", {zIndex:996,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var spActTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/sp_act_tms/{z}/{y}/{x}.png", {zIndex:995,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var spInaTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/sp_ina_tms/{z}/{y}/{x}.png", {zIndex:994,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var atActTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/at_act_tms/{z}/{y}/{x}.png", {zIndex:993,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var atInaTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/at_ina_tms/{z}/{y}/{x}.png", {zIndex:993,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var otActTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/ot_act_tms/{z}/{y}/{x}.png", {zIndex:991,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});
var otInaTileLayer = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/ot_ina_tms/{z}/{y}/{x}.png", {zIndex:990,maxZoom:8,errorTileUrl:"http://nwis-mapper-tiles.s3.amazonaws.com/blank.png"});

//set up overlay layers
var swActLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'gray'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"sw_act"); } });	
var swInaLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'lightgray'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"sw_ina"); } });	
var gwActLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'red'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"gw_act"); } });
var gwInaLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'lightpink'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"gw_ina"); } });
var spActLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'purple'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"sp_act"); } });
var spInaLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'plum'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"sp_ina"); } });
var atActLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'royalblue'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"at_act"); } });
var atInaLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'lightblue'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"at_ina"); } });
var otActLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'lime'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"ot_act"); } });	
var otInaLayer = new L.MarkerClusterGroup({ polygonOptions: {color: 'palegreen'}, showCoverageOnHover:true, zoomToBoundsOnClick:true, removeOutsideVisibleBounds:true, disableClusteringAtZoom:12, iconCreateFunction: function (cluster) {return createClusterMarker(cluster,"ot_ina"); } });	

clusterMarker = L.Icon.Label.extend({ options: { iconUrl: '',shadowUrl: null,iconSize: new L.Point(42, 40),iconAnchor: new L.Point(0, 1),labelAnchor: new L.Point(2, -2),wrapperAnchor: new L.Point(12, 13),labelClassName: 'placeMarks-label'}	});

//add items to basemap dropdown
$.each(basemapNameArray, function(i, v) {
	$("#basemapMenu").append('<li role="presentation" id="' + v[0] + '" ><a role="menuitem" tabindex="-1"><div name="basemapLayers" ><span>' + v[1] + '</span></div></li>');
	
	//make default layer active
	if (v[2]) {
		$("#basemapMenu li ").addClass('active');
	}

});

//get site types data as an object this can happen in the background
$.getJSON( "/mapper/static/json/siteTypes.json", function( data ) {
	siteTypes = data;
	
	//call init function
	init();

});


function init() {

	map = new L.Map('map');

	L.control.scale().addTo(map);
	
	var searchControl = new L.esri.Controls.Geosearch().addTo(map);
	
	L.control.locate().addTo(map);

	sidebar = L.control.sidebar("sidebar", {
	    closeButton: true,
	    position: "right"
	}).addTo(map);

	//draw sites on map load
	map.on('load', function(evt) {
		//add active sites by default
		map.addLayer(swActTileLayer);
	});

	map.setView([39.8, -98.6], 4);

	map.addLayer(ESRIgrayBasemap);

	$("#loading").hide();

	//mobile test
	if( screen.width <= 480 ) { isMobile = true;}

	//show initial map zoom level
	$( ".mapZoom" ).html( "<b>Zoom Level: </b>" + map.getZoom());

	//refresh sites on extent change
	map.on('zoomend dragend', function(evt) {
		$( ".mapZoom" ).html( "<b>Zoom Level: </b>" + map.getZoom());
		if (isMobile) {
			$( ".latlng" ).html(map.getCenter().lng.toFixed(3) + ", " + map.getCenter().lat.toFixed(3));
		}
		
		//refresh active layers
		refreshActiveLayers(map);
		
		//update zoom level if we've gone thru the site type loop completely
		lastZoomLevel_sw = map.getZoom();
		
	});

	//show mouse coordinates
	map.on('mousemove', function(evt) {
		if (!isMobile) {
			$( ".latlng" ).html(evt.latlng.lng.toFixed(3) + ", " + evt.latlng.lat.toFixed(3));
		}
	});

	//get IV data for popup if it exists
	map.on('popupopen', function(evt) {
		//kill any existing iv value in table
		var popupContent = evt.popup.getContent().split('link</a></td></tr>')[0] + 'link</a></td></tr></table>';
		var site_no = popupContent.split('Site Number:</th><td>')[1].split('</td>')[0];
	
		var ivURL = "http://waterservices.usgs.gov/nwis/iv/?site=" + site_no + "&format=nwjson";
		$.getJSON( ivURL, function( data ) {
			var params = data.data;
			//var updateContent = "<br><table class='table table-striped table-bordered table-condensed'>";
			var updateContent;
			if (params) {

				$(params).each(function () {
					updateContent += "<tr><th>" + this.parameter_desc + ":</th><td>" + this.most_recent_value + "</td></tr>";	
				});
				
				//have to do some manipulation with jquery to the table to get it to work properly
				var updateHTML = $(popupContent).append(updateContent).html().replace('<tbody>','<table class="table table-striped table-bordered table-condensed">').replace('</tbody>','</table>');
				
				//update the popup
				evt.popup.setContent(updateHTML);
			}
			
		});

	});

	//control for basemap dropdown
	$('#basemapMenu li').click(function(){

		//dont do anything if the current active layer is clicked
		if (!map.hasLayer(window[$(this).attr("id")])) {
			
			//remove currently active basemap
			$("#basemapMenu li.active").each(function () {
				//console.log("removing ",$(this).attr("id"));
				map.removeLayer(window[$(this).attr("id")]);
				$(this).removeClass("active");
			});
			
			//make new selection active and add to map
			$(this).addClass('active');
			map.addLayer(window[$(this).attr("id")]);
		}
	});

	//add hover function to keep menus open
	$('ul.nav li.dropdown').hover(function() {
	  $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeIn();
	}, function() {
	  $(this).find('.dropdown-menu').stop(true, true).delay(100).fadeOut();
	});

	//sync the maps
	$('#syncButton').on('click', function() {
		$(this).toggleClass('active');
		sidebar.toggle();
	
		if ($(this).hasClass('active')) {
			syncMaps(); 
			$("#syncButton").html('<i class="glyphicon glyphicon-picture"></i>&nbsp;&nbsp;Unsync Maps');
		}
		else {
			unSyncMaps(); 
			$("#syncButton").html('<i class="glyphicon glyphicon-picture"></i>&nbsp;&nbsp;Sync Maps');
		}
	});
	

	//export button
	$('#exportButton').on('click', function() {

		if (map.getZoom() >= 8) {

			$( "#exportModal .modal-body" ).empty();
			$("#loadingExport").show();

		    var xmin = Math.round(map.getBounds().getWest() * 1000) / 1000;
			var ymin = Math.round(map.getBounds().getSouth() * 1000) / 1000;
			var xmax = Math.round(map.getBounds().getEast() * 1000) / 1000;
			var ymax = Math.round(map.getBounds().getNorth() * 1000) / 1000;

			globalExportURL = exportURLmodal + "?bbox=" + xmin + "," + ymin + "," + xmax + "," + ymax + "&scodes=111";

			$( "#exportModal .modal-body" ).load( globalExportURL, function() {
				$("#loadingExport").hide();
			});
		}

		else {
			$("#loadingExport").hide();
			$( "#exportModal .modal-body" ).html('<div class="alert alert-danger">No sites are exportable at this level or window size</div>');
		}
	});

	mapArray.push(map);

	createOverlayMenu("sw", map);

	createThumnailMaps();
	
}

function createThumnailMaps() {

		//create a map for each site type
	$.each(["gw","sp","at","ot"], function (i,v) {
			
		// initialize the map to the custom div
		window["map_" + v] = new L.Map('map_' + v);
		
		//refresh sites on extent change
		window["map_" + v].on('zoomend dragend', function(evt) {

			//refresh active layers
			refreshActiveLayers(window["map_" + v]);
			
			//update zoom level if we've gone thru the site type loop completely
			window["lastZoomLevel_" + v] = window["map_" + v].getZoom();
			
		});
			
		//draw sites on map load
		window["map_" + v].on('load', function(evt) {
			//add active sites by default
			window["map_" + v].addLayer(window[v + "ActTileLayer"]);
		});
		
		//add scale bar		
		window["map_" + v].setView([39.8, -98.6], 2);

		
		var ESRIgrayBasemap = L.tileLayer("http://services.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Light_Gray_Base/MapServer/tile/{z}/{y}/{x}", {opacity: 0.5});
		
		window["map_" + v].addLayer(ESRIgrayBasemap);
		
		//add current map object to array
		mapArray.push(window["map_" + v]);

		//refresh sites on extent change
		window["map_" + v].on('zoomend dragend', function(evt) {
			console.log("zooming map_" + v,window["map_" + v].getZoom());

			//refresh active layers
			refreshActiveLayers(window["map_" + v]);
			
			//update zoom level if we've gone thru the site type loop completely
			window["lastZoomLevel_" + v] = window["map_" + v].getZoom();
			
		});
		
	});
	
	$(".thumbmap").click(function() {
	
		var alertDiv = $(this).parent().find(".thumbmap-alert");

		//console.log("you clicked a thumbmap",this, $(this).parent().find(".thumbmap-alert").html());
		
		//only recreate the alert if it hasn't been created already
		if ($(this).parent().find(".thumbmap-alert").html() == '') {
		
			//console.log("is empty");
			
			var alertHTML = '<div class="alert alert-default fade in" style="margin:0px;"><button type="button" class="close" aria-hidden="true">&times;</button><h4>Add content</h4><p>Here you can add this data theme to the map</p><p><div class="btn-toolbar" role="toolbar"><button type="button" class="btn btn-info add-btn">Add</button></div></p></div>';
		
			var siteType = $(this).parent().attr("id").split("-map-panel")[0];
		
			$(this).parent().find(".thumbmap-alert").html(alertHTML);
		
			//this is weird, have to redefine the tile layer here or else you can only draw one layer
			window[siteType + "ActTileLayer"] = L.tileLayer("http://nwis-mapper-tiles.s3.amazonaws.com/" + siteType + "_act_tms/{z}/{y}/{x}.png", {zIndex:997,maxZoom:9});	
			
			$( ".add-btn" ).click(function() {
				
				var btn = $(this);
				//console.log(btn.html());
				if (btn.html() == "Add")
				{
					btn.html("Remove");
					btn.addClass("btn-warning")
					//console.log("add was clicked",siteType + "_act", window["map_" + siteType]);

					updateOverlayMenu(siteType, map, "add")
					
					drawSitesByType(siteType + "_act", map)
					
				}
				else {
					btn.html("Add");
					btn.removeClass("btn-warning")
					//console.log("remove was clicked",siteType + "_act");

					updateOverlayMenu(siteType, map, "remove")
					
					removeSitesByType(siteType + "_act", map)
					removeSitesByType(siteType + "_ina", map)

				}
			});
		}
		
		else {
			//console.log("not empty");
			$(this).parent().find(".thumbmap-alert").show();
		}

		$('.close').click(function () {
		
					//just hide it instead of replacing
					alertDiv.hide();	
				})

	});
}

function syncMaps() {
	$.each(mapArray, function (index,value) {
		
		$(mapArray).each( function() {
			
			if (this != value) {
				value.sync(this);
			}
		});
	});
}

function unSyncMaps() {
	$.each(mapArray, function (index,value) {
		
		$(mapArray).each( function() {
			
			if (this != value) {
				value.unsync(this);
				//return false;
			}
		});
	});
}

function updateOverlayMenu(v, currentMap, updateType) {

	if (updateType == "add") {
		
		//populate overlay dropdown with active and inactive
		$([[v + "_act"],[v + "_ina"]]).each( function() {
		
				var curSiteTypeInfo = getSiteInfo("siteTypeStatus",this[0]);	
		
				$("#overlayMenu.sw").append('<li role="presentation" id="' + curSiteTypeInfo.overlayLayerName + '" class="' + curSiteTypeInfo.overlayLayerName  + '"><a role="menuitem" tabindex="-1"><div name="overlayLayers" ><img src="' + curSiteTypeInfo.singleMarkerURL + '"/><span>' + curSiteTypeInfo.legendLayerName + '</span></div></li>');
				
				//make default layer active
				$("#overlayMenu.sw").find("#" + v + "ActLayer").addClass('active');

		});
	}
	else if (updateType == "remove") {
		
		$("#overlayMenu.sw").find("#" + v + "ActLayer").remove();
		$("#overlayMenu.sw").find("#" + v + "InaLayer").remove();

	}
}

function createOverlayMenu(v, currentMap) {

	//remove any existing li
	$("#overlayMenu." + v).empty();
	
	//populate overlay dropdown with active and inactive
	$([[v + "_act"],[v + "_ina"]]).each( function() {
			
			var curSiteTypeInfo = getSiteInfo("siteTypeStatus",this[0]);			
	
			$("#overlayMenu." + v).append('<li role="presentation" id="' + curSiteTypeInfo.overlayLayerName + '" class="' + curSiteTypeInfo.overlayLayerName  + '"><a role="menuitem" tabindex="-1"><div name="overlayLayers" ><img src="' + curSiteTypeInfo.singleMarkerURL + '"/><span>' + curSiteTypeInfo.legendLayerName + '</span></div></li>');
			
			//make default layer active
			if (curSiteTypeInfo.drawOnMapLoad == "checked") {				
				$("#overlayMenu." + v + " li").addClass('active');
			}

	});
	
	//control for overlay dropdown-- listens for future DOM changes which we need here
	$(document).on('click', '#overlayMenu.' + v + ' li', function(){

		//if clicked layer is active then turn it off
		if ($(this).hasClass('active')) {

			$(this).removeClass("active");
			
			//use lookup to find deactivated layer
			var curSiteTypeInfo = getSiteInfo("overlayLayerName",$(this).attr("id"));
			
			//use global reference to clear layer
			window[curSiteTypeInfo.overlayLayerName].clearLayers();
			currentMap.removeLayer(window[curSiteTypeInfo.overlayLayerName]);
			currentMap.removeLayer(window[curSiteTypeInfo.tileLayerName]);
			
		}
		
		//otherwise make clicked layer active and draw it
		else {
			
			//make new selection active and add to map
			$(this).addClass('active');
			
			//use lookup to find activated layer
			var layerToDraw = getSiteInfo("overlayLayerName",$(this).attr("id")).siteTypeStatus;

			//draw the layer
			drawSitesByType(layerToDraw, currentMap);	
		}
	});

}

function createClusterMarker(cluster,siteTypeStatus) {

	//get site info for this site type
	var curSiteTypeInfo = getSiteInfo("siteTypeStatus",siteTypeStatus);

	var markers = cluster.getAllChildMarkers();
	
	//single digit labels use default
	if(markers.length < 10){
		markerIcon = new clusterMarker({ labelText:markers.length, iconUrl:curSiteTypeInfo.clusterMarkerURL});
	}
	//if a 2 digit label then shift the anchor
	else if(markers.length > 9 && markers.length < 100){
		markerIcon = new clusterMarker({ labelAnchor:new L.Point(0, -2), labelText:markers.length, iconUrl:curSiteTypeInfo.clusterMarkerURL});
	}
	//if a 3 digit label then shift the anchor
	else {
		markerIcon = new clusterMarker({ labelAnchor:new L.Point(-4, -2), labelText:markers.length, iconUrl:curSiteTypeInfo.clusterMarkerURL});
	}

	return markerIcon;

}

function getSiteInfo(searchKey,searchValue) {

	var returnValue = "";

	$.each(siteTypes, function(i, v) {
		if (v[searchKey] == searchValue) {   

			returnValue = v;
			return;
		}
	});
	return returnValue;
	
}

function refreshActiveLayers(map_obj) {

	var map_id =$(map_obj._container).attr('id');

	if (map_id == "map") {
		var v = "sw";
	}
	else {
		var v = map_id.split("_")[1];

		//for thumbnail maps, call drawsitesbytype
		drawSitesByType(v + "_act", map_obj);
	}

	// Add checked layer
	$("#overlayMenu." + v + " li.active").each(function () {
	
		//use lookup to find layer info used for redraw
		var curSiteTypeInfo = getSiteInfo("overlayLayerName",$(this).attr("id"));
		
		console.log(curSiteTypeInfo.siteTypeStatus, " currentZoom: ",map_obj.getZoom()," lastZoom: ",window["lastZoomLevel_" + v]," overlayMinZoom: ",curSiteTypeInfo.overlayMinZoom);
		
		//if event is a pan, and under minoverlay zoom, do nothing
		if (map_obj.getZoom() == window["lastZoomLevel_" + v] && map_obj.getZoom() < curSiteTypeInfo.overlayMinZoom) {
			//console.log("action is a pan at tile level: ",curSiteTypeInfo.siteTypeStatus);
		}
		
		else if (map_obj.getZoom() > window["lastZoomLevel_" + v] && map_obj.getZoom() < curSiteTypeInfo.overlayMinZoom) {
			//console.log("action is zoom in at tile level: ",curSiteTypeInfo.siteTypeStatus);
		}

		else if (map_obj.getZoom() > window["lastZoomLevel_" + v] && map_obj.getZoom() > curSiteTypeInfo.overlayMinZoom && window["lastZoomLevel_" + v] >= curSiteTypeInfo.overlayMinZoom) {
			//console.log("action is zoom in at overlay level: ",curSiteTypeInfo.siteTypeStatus);
		}
		
		//otherwise, refresh sites
		else {
			//console.log("either changing levels or pan at overlay level (calling drawSitesByType): ",curSiteTypeInfo.siteTypeStatus);
			
			//only redraw layers if zoom level is ok
			drawSitesByType(curSiteTypeInfo.siteTypeStatus, map_obj);

		}
	});
}

function removeSitesByType(siteTypeStatus, map) {

	//get site info for this site type
	var curSiteTypeInfo = getSiteInfo("siteTypeStatus",siteTypeStatus);

	//turn off layers
	window[curSiteTypeInfo.overlayLayerName].clearLayers();
	map.removeLayer(window[curSiteTypeInfo.overlayLayerName]);
	map.removeLayer(window[curSiteTypeInfo.tileLayerName]);
}

function drawSitesByType(siteTypeStatus, map) {
	//console.log(map);
	
	//get site info for this site type
	var curSiteTypeInfo = getSiteInfo("siteTypeStatus",siteTypeStatus);
	
	//console.log(siteTypeStatus, map.getZoom(), curSiteTypeInfo.overlayMinZoom, map);
	
	//zoom logic  if we are greater than the mapZoom then query site service and draw sites
	if (map.getZoom() >= curSiteTypeInfo.overlayMinZoom) {

		console.log("clickable level (redrawing sites): ",curSiteTypeInfo.siteTypeStatus);
	
		//turn off tile layer	
		if (map.hasLayer(window[curSiteTypeInfo.tileLayerName])) {
			map.removeLayer(window[curSiteTypeInfo.tileLayerName]);
		}

		//clear existing and add overlay layer
		window[curSiteTypeInfo.overlayLayerName].clearLayers();	
		map.addLayer(window[curSiteTypeInfo.overlayLayerName]);
		window[curSiteTypeInfo.overlayLayerName].bringToFront();
		
		//delcare custom leaflet icon
		var singleMarkerIcon = L.icon({iconUrl: curSiteTypeInfo.singleMarkerURL,iconSize: [22, 30]});
			
		// round the latitude and longitude values				
		var xmin = Math.round(map.getBounds().getWest() * 1000) / 1000;
		var ymin = Math.round(map.getBounds().getSouth() * 1000) / 1000;
		var xmax = Math.round(map.getBounds().getEast() * 1000) / 1000;
		var ymax = Math.round(map.getBounds().getNorth() * 1000) / 1000;

		//create request URL
		//new active definitiion
		var web_proxy_url = "http://waterservices.usgs.gov/nwis/site/?bBox=" + xmin + "," + ymin + "," + xmax +  ","  + ymax + "&format=mapper,1.0&siteStatus=" + curSiteTypeInfo.siteStatusUrl + "&siteType=" + curSiteTypeInfo.siteTypeUrl + "&hasDataTypeCd=all"; 	//&period=P7D";
		
		//setup loader
		var opts = {lines: 9, length: 5, width: 3, radius: 6, corners: 0.8, rotate: 0, direction: 1, color: curSiteTypeInfo.spinnerOptions.split(",")[0], speed: 1, trail: 87, shadow: false, hwaccel: false, className: 'spinner', zIndex: 2e9, top: curSiteTypeInfo.spinnerOptions.split(",")[1], left: curSiteTypeInfo.spinnerOptions.split(",")[2] };
		var target = document.getElementById("map");
		var loadingSpinner = new Spinner(opts).spin(target);
		
		//do ajax call
		$.ajax({
			type: "GET",
			url: web_proxy_url,
			dataType: "xml",
			complete: function(){ loadingSpinner.stop(); },
			success: function(xml){
				
				//check zoom level AGAIN before drawing--make sure user hasn't zoomed out before completion of call
				if (map.getZoom() >= curSiteTypeInfo.overlayMinZoom) {

					// there are two groups of sites possible: 
					var single_sites = xml.getElementsByTagName("sites");
					var colo_sites = xml.getElementsByTagName("colocated_sites");

					// combinations:single = N, colo = N | single = Y, colo = N | single = Y, colo = Y | single = N, colo = Y

					// single = N, colo = N
					if (single_sites.length == 0 && colo_sites.length == 0){
						return;
					}

					// single = Y
					if (single_sites.length == 1) {
						var markers = single_sites[0].getElementsByTagName("site");
						
						// it's possible to have an XML tag but with no markers
						if (markers.length == 0) {
							
							// so if there really are no single sites and no colocated sites we can exit
							if (colo_sites.length == 0) {
								return;
							} 
						// otherwise process the single sites			
						} else {

							// loop through the marker elements
							var nmarkers = 0;
							while( nmarkers < markers.length) {
														
								//use lookup function to get site type text
								var siteTypeText = curSiteTypeInfo.siteTypeLookup[markers[nmarkers].getAttribute("cat")];
								
								var site_no = markers[nmarkers].getAttribute("sno");
								var site_nm = markers[nmarkers].getAttribute("sna");
								var agency = markers[nmarkers].getAttribute("agc");
								var lat = parseFloat(markers[nmarkers].getAttribute("lat"));
								var lng = parseFloat(markers[nmarkers].getAttribute("lng"));

								/* played around with using bootstrap tabs in popup--gets messy

								var content =  '<div class="bs-example bs-example-tabs">' + 
								'<ul id="myTab" class="nav nav-tabs"><li class="active"><a data-toggle="tab" href="#info">Info</a></li></ul>' +
								'<div id="myTabContent" class="tab-content"><div id="info" class="tab-pane fade active in">' +
								'<table class="table table-striped table-bordered table-condensed">' +
								'<tr><th>Site Number:</th><td>' + site_no + '</td></tr>' +
								'<tr><th>Site Name:</th><td>' + site_nm + '</td></tr>' +
								'<tr><th>Agency:</th><td>' + agency + '</td></tr>' +
								'<tr><th>Access data</th><td><a class="url-break" href=http://waterdata.usgs.gov/nwis/inventory?agency_code=' + agency + '&site_no=' + site_no + ' target="_blank">link</a></td></tr>' +
								'</div></div>' 
								*/
								var content =   "<table class='table table-striped table-bordered table-condensed'>"+
                                "<tr><th>Site Number:</th><td>" + site_no + "</td></tr>"+
                                "<tr><th>Site Name:</th><td>" + site_nm + "</td></tr>"+
                                "<tr><th>Agency:</th><td>" + agency + "</td></tr>"+
                                "<tr><th>Access data</th><td><a class='url-break' href=http://waterdata.usgs.gov/nwis/inventory?agency_code=" + agency + "&site_no=" + site_no + " target='_blank'>link</a></td></tr>";

								//add custom popup
								var sitePopup = new L.Rrose({ maxWidth:200, offset: new L.Point(0,-10), autoPan: false }).setLatLng([lat,lng]).setContent(content  + "</table>");;
						
								// build the marker and bind popup
								var curSite = L.marker([lat,lng], {icon: singleMarkerIcon}).bindPopup(sitePopup, { keepInView: false, autoPan: false, closeButton: false});;
	
								//add to layer
								window[curSiteTypeInfo.overlayLayerName].addLayer(curSite);
								
								//increment marker loop
								nmarkers++;
							}
						}
					}

					// at this point, all single sites have been plotted OR there are no single sites, only colocated sites.  process colocated sites
					if (colo_sites.length == 1) {
						var cl_markers = colo_sites[0].getElementsByTagName("site");
						setCoLoMarkers(curSiteTypeInfo, cl_markers);
					}
				
				}  //end zoom if
  
			}
		});
		
	}
	
	//if not a queryable zoom level, then show tile layer for this site type
	else if (map.getZoom() <= curSiteTypeInfo.tileMaxZoom) {
				
		//clear overlay layer
		window[curSiteTypeInfo.overlayLayerName].clearLayers();
				
		//add tile layer if not already on the map
		if ( ! map.hasLayer(window[curSiteTypeInfo.tileLayerName])) {
			//console.log("tile level (adding tile layer): ",curSiteTypeInfo.siteTypeStatus);
			map.addLayer(window[curSiteTypeInfo.tileLayerName]);
			window[curSiteTypeInfo.tileLayerName].bringToFront();
		}
		else {
			//console.log("tile level (no need to add tile layer): ",curSiteTypeInfo.siteTypeStatus);
		}
	}
}

function setCoLoMarkers(curSiteTypeInfo, coloMarkers) {

	//delcare custom leaflet icon
	var coloMarkerIcon = L.icon({iconUrl: curSiteTypeInfo.coloMarkerURL,iconSize: [42, 40]});

	var CurrLat, CurrLng, CurrID, CurrName, CurrCode, CurrAgency;
	var NextLat, NextLng, NextID, NextName, NextCode, NextAgency;
	
	var tablabels = [];
	var tabcontent = [];
	
	var i = 0;
	do {

		if (i >= coloMarkers.length) {
			break;
		}

		CurrID = coloMarkers[i].getAttribute("sno");
		CurrName = coloMarkers[i].getAttribute("sna");
		CurrCode = coloMarkers[i].getAttribute("cat");
		CurrAgency = coloMarkers[i].getAttribute("agc");
		CurrLat = coloMarkers[i].getAttribute("lat");
		CurrLng = coloMarkers[i].getAttribute("lng");

		// create a point 
		var curSite = L.marker([CurrLat,CurrLng], {icon: coloMarkerIcon});

		// all the sites in this web service stream have at least one colocated site
		// but the do loop will run off the markers array unless checked
		var j = 1;
		var k = 0;
		var DupFlag = 0;

		do {

			//check for end of markers array
			if ((i + j) >= coloMarkers.length) {
				NextLat = "";
				NextLng = "";
			} else {

				NextID = coloMarkers[i + j].getAttribute("sno");
				NextName = coloMarkers[i + j].getAttribute("sna");
				NextCode = coloMarkers[i + j].getAttribute("cat");
				NextAgency = coloMarkers[i + j].getAttribute("agc");
				NextLat = coloMarkers[i + j].getAttribute("lat");
				NextLng = coloMarkers[i + j].getAttribute("lng");
			}

			// if this marker as the same lat/long as the previous marker
			// then the site is a duplicate - need to accumulate the values
			// and check the next marker. If this is the first duplicate,
			// however, we need to save the previous marker information

			if ((CurrLat == NextLat) && (CurrLng == NextLng)) {
			
				// get the first colocated site data
				if (j == 1) {
					tablabels[k] = CurrID;
					tabcontent[k] = '<b>Site: </b>' + CurrID
					+ '<br /><b>Site Name: </b>' + CurrName
					+ '<br /><b>Site Type: </b>' + curSiteTypeInfo.siteTypeLookup[CurrCode]
					+ '<br /><b>Agency: </b>' + CurrAgency
					+ '<br /><a href=http://waterdata.usgs.gov/nwis/inventory?agency_code=' + CurrAgency + '&site_no=' + CurrID + ' target="_blank">Access Data</a>'
					k = k + 1;
				}

				// now get second colocated site
				tablabels[k] = NextID;
				tabcontent[k] = '<b>Site: </b>' + NextID
					+ '<br /><b>Site Name: </b>' + NextName
					+ '<br /><b>Site Type: </b>' + curSiteTypeInfo.siteTypeLookup[NextCode]
					+ '<br /><b>Agency: </b>' + NextAgency
					+ '<br /><a href=http://waterdata.usgs.gov/nwis/inventory?agency_code=' + NextAgency + '&site_no=' + NextID + ' target="_blank">Access Data</a>'

				// increment both inner loop counters
				k = k + 1;
				j = j + 1;

			} else {

				// if we fell through the if it means that the site is not a duplicate of the current group, but instead is the first site in a new group of duplicate sites. It also means that we have to now create a marker and info window for the last group

				// decrement the accumulated counter
				k = k - 1;

				// now create the popup
				var popupTemplate = "<h5>Location has " + (k + 1) + " sites</h5>";
			
				//add info for each site
				for (var nColo = 0; nColo < (k + 1); nColo++) {
					popupTemplate += tabcontent[nColo];
					popupTemplate += '<hr>';
				}
				
				//add custom popup
				var sitePopup = new L.Rrose({ offset: new L.Point(0,-10), autoPan: false })
					  .setContent(popupTemplate)
					  .setLatLng([CurrLat,CurrLng]);	  
				
				//bind the popup
				curSite.bindPopup(sitePopup, { keepInView: true, autoPan: false})
				
				//add site to map
				window[curSiteTypeInfo.overlayLayerName].addLayer(curSite);
				
				//jump over j duplicates and break out of the inner do loop
				i = (i + j);

				//set the break flag
				DupFlag = 1;
			}

		} while (DupFlag == 0)
	} while (i < coloMarkers.length)
}