from collections import OrderedDict


class GeoJsonBuilder:

    @staticmethod
    def create_geojson(features, feature_type="FeatureCollection"):
        export_artifact = OrderedDict()
        export_artifact["type"] = feature_type
        export_artifact["features"] = features

        return export_artifact

    @staticmethod
    def create_feature(properties, lon, lat):
        geometry = OrderedDict()
        geometry["type"] = "Point"
        geometry["coordinates"] = float(lon), float(lat)

        feature = OrderedDict()
        feature["type"] = "Feature"
        feature["properties"] = properties
        feature["geometry"] = geometry

        return feature
