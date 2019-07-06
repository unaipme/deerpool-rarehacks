from urllib import request
from urllib.error import HTTPError
import xml.etree.cElementTree as ET
import sys


def query(lat, lng, offset=.01):
    hits = []
    worked = False
    while not worked and offset > 0:
        try:
            url = "https://api.openstreetmap.org/api/0.6/map?bbox={},{},{},{}" \
                      .format(round(float(lat) - offset, 4), round(float(lng) - offset, 4),
                              round(float(lat) + offset, 4), round(float(lng) + offset, 4))
            req = request.Request(url)
            response = request.urlopen(req)
            it = ET.fromstring(response.read())
            for node in it.iter("node"):
                for tag in node.iter("tag"):
                    if tag.attrib["k"] == "amenity" and tag.attrib["v"] in ["hospital", "clinic"]:
                        hits.append(node)
            worked = True
        except HTTPError as err:
            if err.code == 400:
                offset -= .001
    return hits, offset


def find(lat, lng):
    result, offset = query(lat, lng)
    or_offset = offset
    if len(result) != 0:
        return result
    while len(result) == 0:
        for i_lng in [lng + i * or_offset for i in range(int(-offset/or_offset), int(offset/or_offset))]:
            rang = [lat - offset, lat + offset]
            if i_lng in [lng - offset, lng + offset]:
                rang = [lat + i * or_offset for i in range(int(-offset / or_offset), int(offset / or_offset))]
            for i_lat in rang:
                local_result, _ = query(i_lat, i_lng, or_offset)
                result += local_result
        offset += or_offset
    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)
    lng = float(sys.argv[1])
    lat = float(sys.argv[2])
    for a in find(lat, lng):
        print(a.attrib)
