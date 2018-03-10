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
    #print(station_name)
    #if station_name.startswith("Chargy Ok"):
        # This is a charging station operated by another company, but compatible with Chargy
        # Ideal naming scheme is <Chargy Ok> - <Operator> - <Location>, sometimes the separator between <Operator> and <Location> is missing.
    #    split_name_by_minus = re.search(
    #        r"(.*?)\s\-\s(.*?)\s\-\s(.*)", station_name, flags=re.IGNORECASE)
    #    if split_name_by_minus:
    #        properties["operator"] = split_name_by_minus.group(2)
    #    else:
    #        logger.warning(
    #            "Couldn't find operator for '%s'. Leaving operator empty." % station_name)
    #else:
    #    properties["operator"] = "Chargy"
    properties["operator"] = "Chargy"
    
    visibility = int(station.find("ns:visibility", ns).text)
    if visibility != 1:
        logger.warning("Node '%s', visibility flag != 1." % station_name)
        properties["operational_status"] = "closed"
    
    properties["amenity"] = "charging_station"
    properties['name'] = station_name
    properties["brand"] = "Chargy"
    
    properties["opening_hours"] = "24/7"
    properties["car"] = "yes"
    properties["phone"] = "+352 80062020"
    properties["authentication:membership_card"] = "yes"

    charging_devices = station.findall(
        "ns:ExtendedData/ns:Data[@name='chargingdevice']/ns:value", ns)

    if(len(charging_devices) > 1):
        logger.info("Charging Station '%s' contains '%s' charging points, tagging as 1 charging station." % (
            station_name, len(charging_devices)))

    sum_connectors = 0
    refs = []
    for single_device in charging_devices:
        json_device = json.loads(single_device.text)
        sum_connectors += json_device["numberOfConnectors"]
        refs.append(json_device["name"])
    # TODO: Check if all charging points are offline ?
    properties["ref"] = ";".join(refs)

    raw_station_description = station.find("ns:description", ns).text
    output_wattage_search = re.search(
        r"(\d+)kW", raw_station_description, flags=re.IGNORECASE)
    if not output_wattage_search:
        logger.error("Charging station '%s' description does not contain informations about the wattage in kW. Skipping this entry! Description is: '%s'" % (
            station_name, raw_station_description))
        return None
    else:
        output_wattage_value = int(output_wattage_search.group(1))

    for chargingPoint in json_device["chargingPointList"]:
        if chargingPoint["maxchspeed"] != output_wattage_value:
            logger.error("Power Output mismatch for '%s', was expecting '%s' and got '%s'. Skipping this entry!" % (
                json_device["name"], output_wattage_value, chargingPoint["maxchspeed"]))
            return None

    properties["socket:type2:output"] = ("%skW" % output_wattage_value)

    countChargingPoints = int(station.find(
        "ns:ExtendedData/ns:Data[@name='CPnum']/ns:value", ns).text)

    if countChargingPoints != sum_connectors:
        logger.error("Charging point count mismatch for '%s'. Total reported count is %s, summed description count is %s. Skipping this entry!" % (
            json_device["name"], countChargingPoints, sum_connectors))
        return None

    if not re.search(r"Type 2 connector", raw_station_description, flags=re.IGNORECASE):
        logger.error("Type 2 was not found for station '%s'. Skipping this entry. Description is: '%s'" % (
            station_name, raw_station_description))
        return None

    properties["socket:type2"] = countChargingPoints

    # TODO: Check raw_station_description for count of connectors
    properties["capacity"] = countChargingPoints

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

    logger.debug("Success! Output file contains %s points." % len(features))


if __name__ == "__main__":
    ns = {}

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(
        description='Convert the Chargy KML Dataset into GeoJSON Points')
    parser.add_argument('infile', metavar='INFILE',
                        help='KML File from Chargy',
                        type=lambda x: is_valid_file(parser, x))

    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        default="charging_stations_out_%s.geojson" % time.strftime(
                            '%Y%m%d_%H%M%S'),
                        help='Overrides the default filename for the exported GeoJSON file')

    args = parser.parse_args()

    extract_data_from_kml(args.infile, args.outfile)
