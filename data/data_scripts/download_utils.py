from constants import *
import requests
import zipfile
import os
from os import listdir
import json

# https://www.sciencebase.gov/catalog/file/get/59f5ebe4e4b063d5d307e245
# for animal, url in ANIMAL_TO_URL.items():

def already_there(animal_name):
    return os.path.isdir(DOWNLOAD_PATH + animal_name + '/')

def find_existing_shp(animal_name):
    inner_zip_folder_path = DOWNLOAD_PATH + animal_name + '/'
    return (inner_zip_folder_path + next(filename for filename in listdir(inner_zip_folder_path) if filename.endswith(".shp")))

def write_outer_zip(animal_name, url):
    r = requests.get(url) # TODO separate out get in try/catch, if already there don't bother zipping just find .shp
    zip_location = DOWNLOAD_PATH + animal_name + '.zip'
    open(zip_location, 'wb').write(r.content)
    return zip_location

def unzip_outer_zip(outer_zip_path, animal_name):
    extract_zip_path = DOWNLOAD_PATH + animal_name + '/'
    os.mkdir(extract_zip_path)
    with zipfile.ZipFile(outer_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_zip_path) # directory_to_extract_to is arg for extractall
    return extract_zip_path

def unzip_inner_zip(inner_zip_folder_path, inner_zip_file_path):
    with zipfile.ZipFile(inner_zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(inner_zip_folder_path) # directory_to_extract_to is arg for extractall

def get_shp_path_from_animal_name(animal_name, animal_link=None):
    if not animal_link:
        animal_link = ANIMAL_TO_URL[animal_name]
    if already_there(animal_name):
        print(animal_name, "no download")
        return find_existing_shp(animal_name)
    print(animal_name, "download")
    outer_zip_path = write_outer_zip(animal_name, animal_link)
    inner_zip_folder_path = unzip_outer_zip(outer_zip_path, animal_name)
    inner_zip_file_name = inner_zip_folder_path + next(filename for filename in listdir(inner_zip_folder_path) if ".zip" in filename)
    unzip_inner_zip(inner_zip_folder_path, inner_zip_file_name)
    return (inner_zip_folder_path + next(filename for filename in listdir(inner_zip_folder_path) if filename.endswith(".shp")))

def d_from_file(filename):
    d = None
    with open(filename) as f:
        d = json.load(f)
    f.close()
    return d