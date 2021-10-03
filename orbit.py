from spacetrack import SpaceTrackClient
from sgp4 import omm
from sgp4.api import Satrec, SatrecArray
from skyfield.api import load, EarthSatellite

username = 's164024@student.dtu.dk'
password = '0r3HIhzNKGLJpjquYMpFHw27kpKUOiii'
st = SpaceTrackClient(username, password)

valid_predicates = st.get_predicates('gp', controller='basicspacedata')
# pprint(valid_predicates)

def download_latest_debris_data(filepath):
    debris_data = st.gp(
        iter_lines=True,
        object_type='DEBRIS, ROCKET BODY',
        decay_date=None,
        orderby='gp_id asc',
        format='xml'
    )

    with open(filepath, 'w') as fp:
        for line in debris_data:
            fp.write(line)


def import_orbital_data_from_xml(filepath):
    with open(filepath, 'r') as fp:
        sat_parser = omm.parse_xml(fp)
        sat_list = SatrecArray([Satrec(sat) for sat in sat_parser])

    return sat_list

if __name__ == '__main__':
    filepath = 'debris.xml'

    # st = SpaceTrackClient(username, password)
    # download_latest_debris_data(filepath)

    sat_list = import_orbital_data_from_xml(filepath)

    ts = load.timescale()




