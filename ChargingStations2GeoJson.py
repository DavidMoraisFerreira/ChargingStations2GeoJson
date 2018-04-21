import argparse
import time
import json
import re
import logging
import os
import sys
import xml.etree.cElementTree as ET
from utils.GeoJsonBuilder import GeoJsonBuilder
from collections import OrderedDict

ns = {}
ch = logging.StreamHandler(sys.stdout)
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    return arg


def get_namespace(element):
    match = re.match(r"\{(.*?)\}", element.tag)
    if match:
        return match.group(1)
    raise ValueError("Fatal: Couldn't identify the namespace!")


def process_charging_device(charging_point, station_name, output_wattage_value):
    json_device = json.loads(charging_point.text)
    sum_connectors = json_device["numberOfConnectors"]
    charging_point_id = json_device["id"]
    charging_point_name = json_device["name"].strip()

    if re.search(r"\s", charging_point_name):
        logger.warning("Charging point name '%s' probably contains some text, make sure to verify this before importing. (Belongs to charging station: '%s')" % (
            charging_point_name, station_name))
    if not charging_point_name.startswith("CP"):
        logger.warning("Charging point name '%s' does not have a chargy Id (CPabcd), make sure to verify this before importing. (Belong to charging station: '%s')" %
                       (charging_point_name, station_name))

    # Check contents of the charging points
    charging_points_status = 0
    for chargingPoint in json_device["connectors"]:
        charging_point_description = chargingPoint["description"].strip()

        if charging_point_description.upper() != "OFFLINE":
            charging_points_status += 1

        # Check power output
        if chargingPoint["maxchspeed"] != output_wattage_value:
            logger.error("Power Output mismatch for '%s', was expecting '%s' and got '%s'." % (
                charging_point_name, output_wattage_value, chargingPoint["maxchspeed"]))
            raise ValueError("Power Output Error!")

    count_connectors_not_offline = charging_points_status
    return sum_connectors, charging_point_id, charging_point_name, count_connectors_not_offline


def process_charging_station(station):
    properties = {}
    station_name = ' '.join(station.find("ns:name", ns).text.split())
    # print(station_name)
    # if station_name.startswith("Chargy Ok"):
    # This is a charging station operated by another company, but compatible with Chargy
    # Ideal naming scheme is <Chargy Ok> - <Operator> - <Location>, sometimes the separator between <Operator> and <Location> is missing.
    #    split_name_by_minus = re.search(
    #        r"(.*?)\s\-\s(.*?)\s\-\s(.*)", station_name, flags=re.IGNORECASE)
    #    if split_name_by_minus:
    #        properties["operator"] = split_name_by_minus.group(2)
    #    else:
    #        logger.warning(
    #            "Couldn't find operator for '%s'. Leaving operator empty." % station_name)
    # else:
    #    properties["operator"] = "Chargy"
    properties["operator"] = "Chargy"

    visibility = int(station.find("ns:visibility", ns).text)
    if visibility != 1:
        logger.warning("Node '%s', visibility flag != 1." % station_name)
        properties["operational_status"] = "closed"

    properties["amenity"] = "charging_station"
    properties['name'] = station_name
    properties["brand"] = "Chargy"
    properties["operator"] = "Chargy"
    properties["opening_hours"] = "24/7"
    properties["car"] = "yes"
    properties["phone"] = "+352 80062020"
    properties["authentication:membership_card"] = "yes"

    # Each charging station can have multiple charging points
    charging_devices = station.findall(
        "ns:ExtendedData/ns:Data[@name='chargingdevice']/ns:value", ns)

    properties["devices"] = len(charging_devices)
    if(len(charging_devices) > 1):
        logger.info("Charging Station '%s' contains '%s' charging points, tagging as 1 charging station." % (
            station_name, len(charging_devices)))

    # Get Output in Watts from Description
    raw_station_description = station.find("ns:description", ns).text
    output_wattage_search = re.search(
        r"(\d+)kW", raw_station_description, flags=re.IGNORECASE)
    if not output_wattage_search:
        logger.error("Charging station '%s' description does not contain informations about the wattage in kW. Description is: '%s'" % (
            station_name, raw_station_description))
        raise ValueError("Power Output Error!")
    else:
        output_wattage_value = int(output_wattage_search.group(1))

    # Process all the charging points
    sum_connectors = 0
    refs = []
    count_connectors_not_offline = 0
    for device in charging_devices:
        r_sum_connectors, r_charging_point_id, charging_point_name, r_cnt_connectors_offline = process_charging_device(
            device, station_name, output_wattage_value)
        sum_connectors += r_sum_connectors
        count_connectors_not_offline += r_cnt_connectors_offline
        refs.append(str(r_charging_point_id))

    properties["ref:chargy"] = ";".join(refs)
    if count_connectors_not_offline == 0:
        logger.warning(
            "Charging station '%s' is OFFLINE (All sockets are OFFLINE)" % station_name)
        #properties["operational_status"] = "closed"

    properties["socket:type2:output"] = ("%skW" % output_wattage_value)

    countChargingPoints = int(station.find(
        "ns:ExtendedData/ns:Data[@name='CPnum']/ns:value", ns).text)

    if countChargingPoints != sum_connectors:
        logger.error("Charging point count mismatch for '%s'. Total reported count is %s, summed description count is %s." % (
            charging_point_name, countChargingPoints, sum_connectors))
        raise ValueError("Charging Point Count mismatch!")

    if not re.search(r"Type 2 connector", raw_station_description, flags=re.IGNORECASE):
        logger.error("Type 2 was not found for station '%s'. Description is: '%s'" % (
            station_name, raw_station_description))
        raise ValueError("Connector Type Error! Was expecting Type 2.")

    properties["socket:type2"] = countChargingPoints
    properties["capacity"] = countChargingPoints

    lon, lat = station.find("ns:Point/ns:coordinates", ns).text.split(",")

    return GeoJsonBuilder.create_feature(properties, float(lon), float(lat))


def extract_data_from_kml(path, output_file):
    logger.debug("Reading File: %s" % path)
    doc = ET.parse(path)
    root = doc.getroot()

    ns["ns"] = "%s" % get_namespace(root)
    stations = root.findall(".//ns:Placemark", ns)
    logger.debug("Found %s stations" % len(stations))

    features = []
    for station in stations:
        computed_feature = process_charging_station(station)
        if computed_feature is not None:
            features.append(computed_feature)

    export_artifact = GeoJsonBuilder.create_geojson(features)

    with open(output_file, "w") as outfile:
        logger.debug("Writing to: %s" % output_file)
        json.dump(export_artifact, outfile)

    logger.debug("Success! Output file contains %s points." % len(features))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Convert the Chargy KML Dataset into GeoJSON Points')
    parser.add_argument('infile', metavar='INFILE',
                        help='KML File from Chargy',
                        type=lambda x: is_valid_file(parser, x))

    parser.add_argument('outfile', metavar='OUTFILE', nargs='?',
                        default="charging_stations_out_%s.geojson" % time.strftime(
                            '%Y%m%d_%H%M%S'),
                        help='Overrides the default filename for the exported GeoJSON file')

    parser.add_argument("-v", "--verbose", action="store_const", dest="loglevel",
                        help="Override default loglevel", const=logging.DEBUG)

    args = parser.parse_args()

    if args.loglevel is not None:
        logger.setLevel(args.loglevel)

    extract_data_from_kml(args.infile, args.outfile)
