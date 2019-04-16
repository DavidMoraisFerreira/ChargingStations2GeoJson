import unittest
import os
import sys
import logging
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ChargingStations2GeoJson


class TestConversion(unittest.TestCase):
    def buildPath(self, filename):
        base_path = os.path.dirname(sys.argv[0])
        return os.path.join(base_path, "data", filename)

    def setUp(self):
        ChargingStations2GeoJson.logger.setLevel(logging.DEBUG)
        ChargingStations2GeoJson.strict_mode = True
        print(os.path.dirname(sys.argv[0]))

    @unittest.skip("Not implemented yet")
    def test_simple_station(self):
        test_case_prefix = "valid_station_with_one_charging_point"
        ChargingStations2GeoJson.extract_data_from_kml(
            "data/%s.kml" % test_case_prefix, "data/%s.geojson" % test_case_prefix)
        # TODO: Assert properties
        self.assertEqual(False, False)

    def test_mismatched_connector_count(self):
        test_case_prefix = "broken_mismatched_connector_count"
        self.assertRaises(ValueError, ChargingStations2GeoJson.extract_data_from_kml,
                          self.buildPath("%s.kml" % test_case_prefix), self.buildPath("%s.geojson" % test_case_prefix))

    def test_mismatched_connector_count_in_charging_point(self):
        test_case_prefix = "broken_mismatched_connector_count_charging_point"
        self.assertRaises(ValueError, ChargingStations2GeoJson.extract_data_from_kml,
                          self.buildPath("%s.kml" % test_case_prefix), self.buildPath("%s.geojson" % test_case_prefix))

    def test_different_wattage_in_description(self):
        test_case_prefix = "broken_wattage_count_description"
        self.assertRaises(ValueError, ChargingStations2GeoJson.extract_data_from_kml,
                          self.buildPath("%s.kml" % test_case_prefix), self.buildPath("%s.geojson" % test_case_prefix))

    def test_different_wattage_in_charging_point(self):
        test_case_prefix = "broken_wattage_count_charging_point"
        self.assertRaises(ValueError, ChargingStations2GeoJson.extract_data_from_kml,
                          self.buildPath("%s.kml" % test_case_prefix), self.buildPath("%s.geojson" % test_case_prefix))

    def test_socket_type_wattage(self):
        test_case_prefix = "broken_socket_type_count"
        self.assertRaises(ValueError, ChargingStations2GeoJson.extract_data_from_kml,
                          self.buildPath("%s.kml" % test_case_prefix), self.buildPath("%s.geojson" % test_case_prefix))


if __name__ == '__main__':
    unittest.main()
