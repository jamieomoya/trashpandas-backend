import requests
from sgp4.api import Satrec, SatrecArray
from sgp4 import omm
import numpy as np
from lxml import etree


def get_celestrak_omm_data(group, file_format, file):
    celestrak_endpoint = 'https://celestrak.com/NORAD/elements/gp.php'
    payload = {'GROUP': group, 'FORMAT': file_format}

    # Make request to Celestrak
    r = requests.get(celestrak_endpoint, params=payload)
    r.raise_for_status()

    with open(file, 'w') as f:
        f.write(r.text)

    return


def parse_omm_data(file, file_format):

    if file_format == 'xml':
        doc = etree.parse(file)
        sat_count = int(doc.xpath("count(//omm)"))
        parse_func = omm.parse_xml
    elif file_format == 'csv':
        parse_func = omm.parse_csv
    else:
        raise ValueError

    sats = np.empty(sat_count, dtype=Satrec)

    with open(file, 'r') as f:
        i = 0
        parser = parse_func(f)
        while True:
            try:
                fields = next(parser)
            # except xml.etree.ElementTree.ParseError:
            #     continue
            except StopIteration:
                break

            sats[i] = Satrec()
            omm.initialize(sats[i], fields)

            i += 1

    return SatrecArray(sats)


if __name__ == '__main__':
    get_celestrak_omm_data('active', 'xml', 'celestrak_response.xml')
    sat_array = parse_omm_data('celestrak_response.xml', 'xml')

    print(sat_array)
