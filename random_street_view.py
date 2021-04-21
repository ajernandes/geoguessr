import argparse
import os
import random
import sys
import requests
import json
import base64
import shapefile  # pip install pyshp

import getcolor

# Optional, http://stackoverflow.com/a/1557906/724176
try:
    import timing

    assert timing  # avoid flake8 warning
except ImportError:
    pass

# Google Street View Image API
# 25,000 image requests per 24 hours
# See https://developers.google.com/maps/documentation/streetview/
API_KEY = "AIzaSyA9PAn87ZMK3SB5SNJlC9ATOAediOgg6IU"
GOOGLE_URL = (
    "https://maps.googleapis.com/maps/api/streetview/metadata?key=" + API_KEY
)

IMG_PREFIX = "img_"
IMG_SUFFIX = ".jpg"

parser = argparse.ArgumentParser(
    description="Get random Street View images from a given country",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "-n", "--images-wanted", type=int, default=10, help="Number of images wanted"
)
parser.add_argument("country", help="ISO 3166-1 Alpha-3 Country Code")
parser.add_argument(
    "-hdg",
    "--heading",
    help="Heading in degrees: 0 and 360 north, 90 east, 180 south, 270 west",
)
parser.add_argument(
    "-p",
    "--pitch",
    help="Pitch in degrees: 0 is default, 90 straight up, -90 straight down",
)
args = parser.parse_args()
countries = ["ARG","AUS", "BEL", "BEN", "BES", "BFA", "BGD", "BGR", "BHR", "BHS", "BIH", "BLM", "BLR", "BLZ", "BMU", "BOL", "BRA", "BRB", "BRN", "BTN", "BVT", "BWA", "CAF", "CAN", "CCK", "CHE", "CHL", "CHN", "CIV", "CMR", "COD", "COG", "COK", "COL", "COM", "CPV", "CRI", "CUB", "CUW", "CXR", "CYM", "CYP", "CZE", "DEU", "DJI", "DMA", "DNK", "DOM", "DZA", "ECU", "EGY", "ERI", "ESH", "ESP", "EST", "ETH", "FIN", "FJI", "FLK", "FRA", "FRO", "FSM", "GAB", "GBR", "GEO", "GGY", "GHA", "GIB", "GIN", "GLP", "GMB", "GNB", "GNQ", "GRC", "GRD", "GRL", "GTM", "GUF", "GUM", "GUY", "HKG", "HMD", "HND", "HRV", "HTI", "HUN", "IDN", "IMN", "IND", "IOT", "IRL", "IRN", "IRQ", "ISL", "ISR", "ITA", "JAM", "JEY", "JOR", "JPN", "KAZ", "KEN", "KGZ", "KHM", "KIR", "KNA", "KOR", "KWT", "LAO", "LBN", "LBR", "LBY", "LCA", "LIE", "LKA", "LSO", "LTU", "LUX", "LVA", "MAC", "MAF", "MAR", "MCO", "MDA", "MDG", "MDV", "MEX", "MHL", "MKD", "MLI", "MLT", "MMR", "MNE", "MNG", "MNP", "MOZ", "MRT", "MSR", "MTQ", "MUS", "MWI", "MYS", "MYT", "NAM", "NCL", "NER", "NFK", "NGA", "NIC", "NIU", "NLD", "NOR", "NPL", "NRU", "NZL", "OMN", "PAK", "PAN", "PCN", "PER", "PHL", "PLW", "PNG", "POL", "PRI", "PRK", "PRT", "PRY", "PSE", "PYF", "QAT", "REU", "ROU", "RUS", "RWA", "SAU", "SDN", "SEN", "SGP", "SGS", "SHN", "SJM", "SLB", "SLE", "SLV", "SMR", "SOM", "SPM", "SRB", "SSD", "STP", "SUR", "SVK", "SVN", "SWE", "SWZ", "SXM", "SYC", "SYR", "TCA", "TCD", "TGO", "THA", "TJK", "TKL", "TKM", "TLS", "TON", "TTO", "TUN", "TUR", "TUV", "TWN", "TZA", "UGA", "UKR", "UMI", "URY", "USA", "UZB", "VAT", "VCT", "VEN", "VGB", "VIR", "VNM", "VUT", "WLF", "WSM", "YEM", "ZAF", "ZMB", "ZWE",]

# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# http://www.ariel.com.au/a/python-point-int-poly.html
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside



print("Loading borders")
shape_file = "TM_WORLD_BORDERS-0.3.shp"
if not os.path.exists(shape_file):
    print(
        "Cannot find " + shape_file + ". Please download it from "
        "http://thematicmapping.org/downloads/world_borders.php and try again."
    )
    sys.exit()

sf = shapefile.Reader(shape_file, encoding="latin1")
shapes = sf.shapes()

print("Finding country")
if(args.country == "all" or args.country == "ALL"):
    args.country = random.choice(countries)
for i, record in enumerate(sf.records()):
    if record[2] == args.country.upper():
        print(record[2], record[4])
        print(shapes[i].bbox)
        min_lon = shapes[i].bbox[0]
        min_lat = shapes[i].bbox[1]
        max_lon = shapes[i].bbox[2]
        max_lat = shapes[i].bbox[3]
        borders = shapes[i].points
        break
    


print("processing (will not continually print to make the program faster)")
attempts, country_hits, imagery_hits, imagery_misses = 0, 0, 0, 0
MAX_URLS = 25000

try:
    while True:
        attempts += 1
        rand_lat = random.uniform(min_lat, max_lat)
        rand_lon = random.uniform(min_lon, max_lon)
        # print attempts, rand_lat, rand_lon
        # Is (lat,lon) inside borders?
        if point_inside_polygon(rand_lon, rand_lat, borders):
            country_hits += 1
            lat_lon = str(rand_lat) + "," + str(rand_lon)
            url = GOOGLE_URL + "&location=" + lat_lon
            returnData = ""
            try:
                returnData = requests.get(url).content
            except KeyboardInterrupt:
                sys.exit("exit")
            returnData = json.loads(returnData)
            if returnData['status'] == "OK":
                print("    ========== Got one! ==========")
                message = str(returnData["location"]["lat"]) + "," + str(returnData["location"]["lng"])
                message_bytes = message.encode('ascii').hex()
                print(message_bytes)
                break
            else:
                imagery_misses += 1

except KeyboardInterrupt:
    print("Keyboard interrupt")

print("Attempts:\t", attempts)

# End of file
countries = ["ABW", "AFG", "AGO", "AIA", "ALA", "ALB", "AND", "ARE", "ARG", "ARM", "ASM", "ATA", "ATF", "ATG", "AUS", "AUT", "AZE", "BDI", "BEL", "BEN", "BES", "BFA", "BGD", "BGR", "BHR", "BHS", "BIH", "BLM", "BLR", "BLZ", "BMU", "BOL", "BRA", "BRB", "BRN", "BTN", "BVT", "BWA", "CAF", "CAN", "CCK", "CHE", "CHL", "CHN", "CIV", "CMR", "COD", "COG", "COK", "COL", "COM", "CPV", "CRI", "CUB", "CUW", "CXR", "CYM", "CYP", "CZE", "DEU", "DJI", "DMA", "DNK", "DOM", "DZA", "ECU", "EGY", "ERI", "ESP", "EST", "ETH", "FIN", "FJI", "FLK", "FRA", "FRO", "FSM", "GAB", "GBR", "GEO", "GGY", "GHA", "GIB", "GIN", "GLP", "GMB", "GNB", "GNQ", "GRC", "GRD", "GRL", "GTM", "GUF", "GUM", "GUY", "HKG", "HMD", "HND", "HRV", "HTI", "HUN", "IDN", "IMN", "IND", "IOT", "IRL", "IRN", "IRQ", "ISL", "ISR", "ITA", "JAM", "JEY", "JOR", "JPN", "KAZ", "KEN", "KGZ", "KHM", "KIR", "KNA", "KOR", "KWT", "LAO", "LBN", "LBR", "LBY", "LCA", "LIE", "LKA", "LSO", "LTU", "LUX", "LVA", "MAC", "MAF", "MAR", "MCO", "MDA", "MDG", "MDV", "MEX", "MHL", "MKD", "MLI", "MLT", "MMR", "MNE", "MNG", "MNP", "MOZ", "MRT", "MSR", "MTQ", "MUS", "MWI", "MYS", "MYT", "NAM", "NCL", "NER", "NFK", "NGA", "NIC", "NIU", "NLD", "NOR", "NPL", "NRU", "NZL", "OMN", "PAK", "PAN", "PCN", "PER", "PHL", "PLW", "PNG", "POL", "PRI", "PRK", "PRT", "PRY", "PSE", "PYF", "QAT", "REU", "ROU", "RUS", "RWA", "SAU", "SDN", "SEN", "SGP", "SGS", "SHN", "SJM", "SLB", "SLE", "SLV", "SMR", "SOM", "SPM", "SRB", "SSD", "STP", "SUR", "SVK", "SVN", "SWE", "SWZ", "SXM", "SYC", "SYR", "TCA", "TCD", "TGO", "THA", "TJK", "TKL", "TKM", "TLS", "TON", "TTO", "TUN", "TUR", "TUV", "TWN", "TZA", "UGA", "UKR", "UMI", "URY", "USA", "UZB", "VAT", "VCT", "VEN", "VGB", "VIR", "VNM", "VUT", "WLF", "WSM", "YEM", "ZAF", "ZMB", "ZWE",]