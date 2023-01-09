'''
Metaprogramming functions.

These functions are responsible for generating JSON configuration files for the
riskzones background app.
'''

from datetime import datetime
import os

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
                    "coordinates": [[[]]]
                }
            }
        ]
    }

    # Add each point to the GeoJSON structure
    for point in polygon:
        pol_dict['features'][0]['geometry']['coordinates'][0][0].append(point)
    
    # The first point must be repeated at the end to close the polygon
    pol_dict['features'][0]['geometry']['coordinates'][0][0].append(polygon[0])

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
        if point[1] > top:    top    = point[1]
    
    base_conf = {
        "base_filename": base_filename,
        "left": left,
        "bottom": bottom,
        "right": right,
        "top": top,
        "zone_size": zl,
        "cache_zones": True,
        "M": int(os.getenv('RZ_M')),
        "edus": int(os.getenv('RZ_EDUS')),
        "geojson": f"{base_filename}.geojson",
        "pois": f"{base_filename}.osm",
        "pois_types": {
            "amenity": [],
            "railway": []
        },
        "edu_alg": "none",
        "output": f"{base_filename}_map.csv",
        "output_edus": f"{base_filename}_edus.csv",
        "output_roads": f"{base_filename}_roads.csv",
    }

    return base_filename, base_conf
