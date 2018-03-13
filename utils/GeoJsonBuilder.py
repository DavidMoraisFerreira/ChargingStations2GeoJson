from collections import OrderedDict


class GeoJsonBuilder:

    @staticmethod
    def create_geojson(features, feature_type="FeatureCollection"):
        export_artifact = OrderedDict()
        export_artifact["type"] = feature_type
        export_artifact["features"] = features

        return export_artifact
