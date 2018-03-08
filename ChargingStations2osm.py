import argparse
import time
import json
import re
import logging
import os
import xml.etree.cElementTree as ET
from collections import OrderedDict


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    return arg


def get_namespace(element):
    match = re.match(r"\{(.*?)\}", element.tag)
    if match:
        return match.group(1)
    raise ValueError("Fatal: Couldn't identify the namespace!")


def build_single_feature(station):
    single_feature = OrderedDict()
    single_feature["type"] = "Feature"
    properties = {}
    station_name = station.find("ns:name", ns).text
    visibility = int(station.find("ns:visibility", ns).text)
    if visibility != 1:
        logger.warning("Node '%s', visibility flag is not 1" % station_name)
        properties["operational_status"] = "closed"

    properties["amenity"] = "charging_station"
    properties['name'] = station_name
    properties["amperage"] = 32  # TODO: Is this correct?
    properties["operator"] = "Chargy"
    properties["car"] = "yes"
    properties["phone"] = "+352 80062020"
    properties["authentication:membership_card"] = "yes"
    properties["authentication:membership_card"] = "mKaart"

    charging_devices = station.findall(
        "ns:ExtendedData/ns:Data[@name='chargingdevice']/ns:value", ns)

    if(len(charging_devices) > 1):
        logger.info("Station %s is actually %s stations marked as 1, tagging accordingly." % (
            station_name, len(charging_devices)))

    sum_connectors = 0
    refs = []
    for single_device in charging_devices:
        json_device = json.loads(single_device.text)
        sum_connectors += json_device["numberOfConnectors"]
        refs.append(json_device["name"])

    properties["ref"] = ";".join(refs)

    countChargingPoints = int(station.find(
        "ns:ExtendedData/ns:Data[@name='CPnum']/ns:value", ns).text)

    if countChargingPoints != sum_connectors:
        logger.error("Charging point count mismatch for %s! Total reported count is %s, summed description count is %s. Skipping this entry!" % (
            json_device["name"], countChargingPoints, sum_connectors))
        return None

    properties["socket:type2"] = countChargingPoints
    properties["capacity"] = countChargingPoints

    expected_output = 22  # TODO: Extract this from the html description
    for chargingPoint in json_device["chargingPointList"]:
        if chargingPoint["maxchspeed"] != expected_output:
            logger.error("'propertiesectric' Power Output mismatch for %s, was expecting %s and got %s. Skipping this entry!" % (
                json_device["name"], expected_output, chargingPoint["maxchspeed"]))
            return None

    properties["socket:type2:output"] = ("%skW" % expected_output)

    geometry = OrderedDict()
    geometry["type"] = "Point"
    lon, lat = station.find("ns:Point/ns:coordinates", ns).text.split(",")
    geometry["coordinates"] = float(lon), float(lat)
    single_feature["properties"] = properties
    single_feature["geometry"] = geometry
    return single_feature


def extract_data_from_kml(path, output_file):
    logger.debug("Reading File: %s" % path)
    doc = ET.parse(path)
    root = doc.getroot()

    ns["ns"] = "%s" % get_namespace(root)
    stations = root.findall(".//ns:Placemark", ns)
    logger.debug("Found %s stations" % len(stations))

    features = []
    for station in stations:
        computed_feature = build_single_feature(station)
        if computed_feature is not None:
            features.append(computed_feature)

    export_artifact = OrderedDict()
    export_artifact["type"] = "FeatureCollection"
    export_artifact["features"] = features

    with open(output_file, "w") as outfile:
        logger.debug("Writing to: %s" % output_file)
        json.dump(export_artifact, outfile)

    logger.debug("Success! Output file contains %s nodes." % len(features))


if __name__ == "__main__":
    ns = {}

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description='Convert the Chargy KML Dataset into OSM Nodes')
    parser.add_argument('infile', metavar='INFILE',
                        help='KML File from Chargy',
                        type=lambda x: is_valid_file(parser, x))

    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        default="charging_stations_out_%s.geojson" % time.strftime(
                            '%Y%m%d_%H%M%S'),
                        help='Overrides the default filename for the exported GeoJSON file')

    args = parser.parse_args()

    extract_data_from_kml(args.infile, args.outfile)
