'''
Metaprogramming functions.

These functions are responsible for generating JSON configuration files for the
riskzones background app.
'''

from datetime import datetime
import json
import os

# Create the queue and output directories
QUEUE_DIR = '/tmp/riskzonesweb/queue'
OUTPUT_DIR = '/tmp/riskzonesweb/out'
try:
  os.makedirs(QUEUE_DIR)
  os.makedirs(OUTPUT_DIR)
except FileExistsError:
  pass

def make_polygon(polygon: list) -> dict:
  '''
  Generate a GeoJSON structure for the polygon.
  '''
  pol_dict = {
    "type": "FeatureCollection",
    "name": "meta",
    "crs": {
      "type": "name",
      "properties": {
        "name": "urn:ogc:def:crs:EPSG::4674"
      }
    },
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPolygon",
          "coordinates": [[]]
        }
      }
    ]
  }

  # Add each point to the GeoJSON structure
  for point in polygon[:-1]:
    pol_dict['features'][0]['geometry']['coordinates'][0].append(point)

  return pol_dict

def make_config_file(polygon: list, zl: int) -> tuple:
  '''
  Generate a JSON configuration for the riskzones rool.
  '''
  timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
  base_filename = f"task_{timestamp}"

  # Calculate AoI boundaries
  left = right = polygon[0][0]
  top = bottom = polygon[0][1]

  for point in polygon[1:]:
    if point[0] < left:   left   = point[0]
    if point[0] > right:  right  = point[0]
    if point[1] < bottom: bottom = point[1]
    if point[1] < top:    top    = point[1]
  
  base_conf = {
    "left": left,
    "bottom": bottom,
    "right": right,
    "top": top,
    "zone_size": zl,
    "cache_zones": True,
    "M": 3,
    "edus": 300,
    "geojson": f"{QUEUE_DIR}/{base_filename}.geojson",
    "pois": f"{QUEUE_DIR}/{base_filename}.osm",
    "pois_types": {
      "amenity": [],
      "railway": []
    },
    "edu_alg": "restricted",
    "output": f"{OUTPUT_DIR}/{base_filename}_map.csv",
    "output_edus": f"{OUTPUT_DIR}/{base_filename}_edus.csv",
    "output_roads": f"{OUTPUT_DIR}/{base_filename}_roads.csv",
  }

  return base_filename, base_conf

def write_conf(filename: str, conf: dict, geojson: dict) -> bool:
  '''
  Write the GeoJSON and configuration JSON into the queue directory.
  '''
  fp = open(f"{QUEUE_DIR}/{filename}", 'w')
  json.dump(conf, fp)
  fp.close()

  fp = open(conf['geojson'], 'w')
  json.dump(geojson, fp)
  fp.close()
  return True
