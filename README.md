 ChargingStations2osm
==================

Converts the Dataset of public EV charging stations in Luxembourg into a format (GeoJSON) that is more suited for importing in [OpenStreetMap](https://www.openstreetmap.org). This Dataset is provided by [Chargy.lu](https://chargy.lu/) and published under the Creative Commons Zero License on the [Luxembourgish Data Platform](https://data.public.lu/en/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/).


## Tagging Scheme

TODO: Describe how the *.kml information is tagged in OSM.


## How to use

```
> python3 ChargingStations2osm.py input_file.kml

> python3 ChargingStations2osm.py input_file.kml output_file.geojson

> python3 ChargingStations2osm.py --help

usage: ChargingStations2osm.py [-h] INFILE [OUTFILE]

Convert the Chargy KML Dataset into OSM Nodes

positional arguments:
  INFILE      KML File from Chargy
  OUTFILE     Overrides the default filename for the exported GeoJSON file

optional arguments:
  -h, --help  show this help message and exit
```
