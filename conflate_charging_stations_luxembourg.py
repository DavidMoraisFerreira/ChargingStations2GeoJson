import conflate
import json
import io

#Documentation: https://wiki.openstreetmap.org/wiki/OSM_Conflator

source = "https://data.public.lu/fr/datasets/bornes-de-chargement-publiques-pour-voitures-electriques/"
wiki = "https://wiki.openstreetmap.org/wiki/Import/Catalogue/Chargy_Import_Luxembourg"
query = [('amenity', 'charging_station'), ('ref:chargy',)]
bbox = True
no_dataset_id = True
max_distance = 200
master_tags = ['name', 'capacity', 'devices', 'socket:type2', 'socket:type2:output', 'ref:chargy']
remove_duplicates = False
delete_unmatched = True

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
