import json
import io

source = "https://data.public.lu/fr/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/"
query = [('amenity', 'charging_station')]
bbox = True
no_dataset_id = True
master_tags = ['name','capacity','devices','socket:type2']
remove_duplicates = False


def dataset(fileobj):
    js = json.loads(fileobj.read().decode('utf-8'))
    data = []
    for feature in js["features"]:
        tags = feature["properties"]
        title = tags["ref:chargy"]
        geometry = feature["geometry"]
        lon = geometry["coordinates"][0]
        lat = geometry["coordinates"][1]
        data.append(SourcePoint(title, lat, lon, tags))

    return data
