#!/usr/bin/env python
'''
Makes shapefiles given animal name and link
'''
import geopandas as gpd
import json
import random
import fiona
import matplotlib.pyplot as plt
from shapely.ops import transform
import time
import click
from download_utils import *
import csv


def get_simplify_factor(a_range):
    # area = (abs(a_range.bounds.minx.values[0] - a_range.bounds.maxx.values[0]) * 
            # abs(a_range.bounds.miny.values[0] - a_range.bounds.maxy.values[0]))
    # print(area)
    return SIMPLIFY_CONST


def to_geojson(animal_name, animal_link=None, science_name=None):
    if not animal_link and not animal_name in ANIMAL_TO_URL:
        print("Unrecognized animal")
        return
    # does downloading, unzipping, etc and gives back nice .shp        
    path_to_shp = get_shp_path_from_animal_name(animal_name, animal_link=animal_link)
    animal_range = gpd.read_file(path_to_shp)
    animal_range = animal_range.to_crs("EPSG:4326") # convert to normal coords
    simplifyFactor = get_simplify_factor(animal_range)

    simp = animal_range.simplify(simplifyFactor, preserve_topology=False) # simplified geodataframe
    # simp.plot(figsize=(5,5), edgecolor="purple", facecolor="None") # TODO needed?
    outfilename = "../usable_data/final_geojson/" + animal_name + "_simplify_auto.geojson"
    simp.to_file(outfilename, driver='GeoJSON')

    # Dump min/max for animal in case we use it for shifting populations
    with open("../usable_data/final_metadata_animals/" + animal_name + "_meta.json", 'w') as meta_file:
        json.dump({
            "minx": animal_range.bounds.minx.values[0],
            "miny": animal_range.bounds.miny.values[0],
            "maxx": animal_range.bounds.maxx.values[0],
            "maxy": animal_range.bounds.maxy.values[0],
            "real_name": ' '.join(animal_name.split('_')),
            "science_name": science_name
        }, meta_file)

def bulk_shape_from_csv(filename):
    with open(filename) as csvfile:
        csvReader = csv.reader(csvfile, delimiter=',')
        header = next(csvReader)
        underscore_name = ""
        while underscore_name != "Southeastern_Myotis":
            row = next(csvReader)
            row_dict = {header[i]: row[i] for i in range(len(header))}
            underscore_name = '_'.join(row_dict["Common Name"].split(" "))

        for row in csvReader:
            row_dict = {header[i]: row[i] for i in range(len(header))}
            underscore_name = '_'.join(row_dict["Common Name"].split(" "))
            to_geojson(underscore_name, row_dict["Range Data"], row_dict["Scientific Name"])
            time.sleep(random.random()*5)


@click.command()
@click.option('-a', help='Animal name that maps to url to start')
@click.option('-f', help='File name with json animal:link dict to add')
@click.option('-c', help='CSV name with links to add')
@click.option('-m', help='geojson')
# TODO go from csv add taxa to all metadata
def makeGeoJSONForAnimal(a, f, m, c):
    if not m == "geojson":
        print("Bad mode, not running!")
    if a:
        to_geojson(a)
    elif f:
        for animal, animal_link in d_from_file(f).items():
            time.sleep(random.random()*3)
            to_geojson(animal, animal_link=animal_link)
    elif c:
        bulk_shape_from_csv(c)
    else:
        "Pick animal or file or get the heck out"
    print("=====Done!=====")


if __name__ == "__main__":
    makeGeoJSONForAnimal()