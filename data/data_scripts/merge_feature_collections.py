#!/usr/bin/env python

from shapely.geometry import MultiPolygon, Polygon
from shapely import geometry
from shapely.ops import unary_union
import json
from os import listdir


FEATURE_COLLECTION_DIR = "../usable_data/final_geojson/"
METADATA_DIR = "../usable_data/final_metadata_animals/"
FINAL_DEST = "../usable_data/animals_for_mongo/{}_document.json"
JUST_GEO_DEST = "../usable_data/animals_for_mongo_just_geo/{}_multipoly.geojson"

def to_shapely_object(feature):
    if not feature.get("geometry") or not feature["geometry"].get("type"):
        print("weird shape: ", str(feature))
        return None
    if feature["geometry"]["type"] == "Polygon":
        return geometry.MultiPolygon([geometry.Polygon(poly) for poly in feature["geometry"]["coordinates"]])
    elif feature["geometry"]["type"] == "MultiPolygon":
        return geometry.MultiPolygon([geometry.Polygon(poly) 
                                      for multipoly in feature["geometry"]["coordinates"]
                                      for poly in multipoly])
    else:
        print("weird shape: ", str(feature))


def get_animal_from_filename(filename):
    if not "_simplify_auto.geojson" in filename:
        print(f"the heck is this filename: {filename}")
        assert False
    return filename.split("/")[-1].split("_simplify_auto.geojson")[0]


def write_just_geo(animal, uni_simple):
    with open(JUST_GEO_DEST.format(animal.lower()), 'w') as f:
        json.dump(uni_simple, f)


def write_full(animal, all_data):
    with open(FINAL_DEST.format(animal.lower()), 'w') as f:
        json.dump(all_data, f)


def make_multipoly_for_file(filename):
    f = open(filename, 'r')
    shapes = list(map(to_shapely_object, json.load(f)["features"]))
    shapes = list(filter(lambda x: x != None, shapes))
    uni = unary_union(shapes)
    return uni.bounds, geometry.mapping(uni)    


def get_area(metadata):
    return abs(metadata["minx"] - metadata["maxx"]) * abs(metadata["miny"] - metadata["maxy"])


def convert_file(filename, metadata_dir):
    animal = get_animal_from_filename(filename)
    print(f"processing {animal}...")
    bounds, multipoly = make_multipoly_for_file(filename)
    if not bounds:
        # RIP berry cave salamander and pigeon mountain salamander
        print(f"No bounds for my friend the {animal} :'(")
        return False

    write_just_geo(animal, multipoly)
    meta_file = metadata_dir + animal + "_meta.json"
    with open(meta_file, 'r') as f:
        metadata = json.load(f)

    minx, miny, maxx, maxy = bounds
    metadata["minx"] = minx
    metadata["miny"] = miny
    metadata["maxx"] = maxx
    metadata["maxy"] = maxy
    metadata["rough_area"] = get_area(metadata)
    metadata["habitat_range"] = multipoly
    write_full(animal, metadata)
    return True


def convert_from_dir(feature_collect_dir=FEATURE_COLLECTION_DIR, metadata_dir=METADATA_DIR):
    feature_files = {feature_collect_dir+filename for filename in listdir(feature_collect_dir)}
    count = 0
    for feature_file in feature_files:
        count += int(convert_file(feature_file, metadata_dir))
    print(f"Did {count} of these guys..")
convert_from_dir()
