 ChargingStations2osm
==================

Converts the Dataset of public EV charging stations in Luxembourg into a format (GeoJSON) that is more suited for importing in [OpenStreetMap](https://www.openstreetmap.org). This Dataset is provided by [Chargy.lu](https://chargy.lu/) and published under the Creative Commons Zero License on the [Luxembourgish Data Platform](https://data.public.lu/en/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/).


## Tagging Scheme

### Input:
```xml
<!-- Left out some data to keep it short -->
<Placemark>
    <name>PLACEHOLDER_NAME</name>
    <visibility>1</visibility>
    <address>PLACEHOLDER_ADDRESS</address>
    <description>&lt;span&gt;&lt;b&gt;2&lt;/b&gt; connectors with 22kW and Type 2 connector&lt;span&gt;&lt;br/&gt;&lt;span&gt;&lt;b&gt;2&lt;/b&gt; available connectors&lt;span&gt;&lt;br/&gt;&lt;span&gt;&lt;b&gt;0&lt;/b&gt; occupied connectors&lt;span&gt;&lt;br/&gt;</description>
    <styleUrl>#AVAILABLE</styleUrl>
    <ExtendedData>
        <Data name="CPnum">
            <displayName>Number of chargingpoints</displayName>
            <value>2</value>
        </Data>
        <Data name="chargingdevice">
            <displayName>Charging device</displayName>
            <value>{"name":"PLACEHOLDER_ID","numberOfConnectors":2,"chargingPointList":[{"id":51566,"maxchspeed":22.0,"connector":1,"description":"AVAILABLE"},{"id":51603,"maxchspeed":22.0,"connector":2,"description":"AVAILABLE"}]}</value>
        </Data>
    </ExtendedData>
    <Point>
        <altitudeMode>clampToGround</altitudeMode>
        <coordinates>123,456</coordinates>
    </Point>
</Placemark>
<!-- Left out some data to keep it short -->
```

### Output:
```json
{
   "type":"FeatureCollection",
   "features":[
      {
         "type":"Feature",
         "properties":{
            "operator":"Chargy",
            "amenity":"charging_station",
            "name":"PLACEHOLDER_NAME",
            "brand":"Chargy",
            "opening_hours":"24/7",
            "car":"yes",
            "phone":"PLACEHOLDER_PHONE",
            "authentication:membership_card":"yes",
            "devices":1,
            "ref:chargy":"1763",
            "socket:type2:output":"22kW",
            "socket:type2":2,
            "capacity":2
         },
         "geometry":{
            "type":"Point",
            "coordinates":[
               123,
               456
            ]
         }
      }
   ]
}
```
## How to use

```
> python3 ChargingStations2osm.py input_file.kml

> python3 ChargingStations2osm.py input_file.kml output_file.geojson

> python3 ChargingStations2osm.py --help

usage: ChargingStations2osm.py [-h] INFILE [OUTFILE]

Convert the Chargy KML Dataset into GeoJSON Points

positional arguments:
  INFILE      KML File from Chargy
  OUTFILE     Overrides the default filename for the exported GeoJSON file

optional arguments:
  -h, --help  show this help message and exit
```
