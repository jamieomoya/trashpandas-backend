# TODO: Generate orbits with sgp4
# TODO: Make data ready for front-end use

from load_omm_data import *
from propagateorbits import *

from os.path import exists, getmtime
from sgp4.api import SGP4_ERRORS, Satrec
from datetime import datetime, timedelta
import asyncio
import numpy as np
np.set_printoptions(precision=2)
import pandas as pd
import json


async def main(start_time: datetime, time_step: timedelta):
    # Where the OMM (Orbital Mean elements Message) data is stored
    omm_file = 'source_data/celestrak_response.xml'

    # Don't spam the CelesTrak API with requests, it doesn't update that often either way
    if exists(omm_file):
        data_update_time = datetime.fromtimestamp(getmtime(omm_file))
        data_age = datetime.now() - data_update_time
        if data_age > timedelta(hours=1):
            print("Updating data...")
            get_celestrak_omm_data('active', 'xml', omm_file)
    elif not exists(omm_file):
        print("Downloading data...")
        get_celestrak_omm_data('iridium-33-debris', 'xml', omm_file)

    # Parse the data
    sats = parse_omm_data(omm_file, 'xml')

    sim_time = start_time

    # Update orbit position every XX second
    while True:
        e, r, v = await update_sat_pos(sats, sim_time)
        [print(SGP4_ERRORS[int(error)]) for error in e if error != 0]
        print(f'{sim_time}\t{r[0, :, :].squeeze()}')
        # test = json.JSONEncoder.encode(r)
        df = pd.DataFrame(
            {
                "X": r[:, :, 0].squeeze(),
                "Y": r[:, :, 1].squeeze(),
                "Z": r[:, :, 2].squeeze(),
            },
            index=range(len(r))
        )
        with open("test.json", 'w') as f:
            f.write(df.to_json())

        sim_time += time_step
        await asyncio.sleep(10)


def alt_main(start_time: datetime, time_step: timedelta, n_steps: int):
    # Where the OMM (Orbital Mean elements Message) data is stored
    omm_file = 'celestrak_response.xml'

    # Don't spam the CelesTrak API with requests, it doesn't update that often either way
    if exists(omm_file):
        data_update_time = datetime.fromtimestamp(getmtime(omm_file))
        data_age = datetime.now() - data_update_time
        if data_age > timedelta(hours=1):
            print("Updating data...")
            get_celestrak_omm_data('active', 'xml', omm_file)
    elif not exists(omm_file):
        print("Downloading data...")
        get_celestrak_omm_data('iridium-33-debris', 'xml', omm_file)

    # Parse the data
    sats = parse_omm_data(omm_file, 'xml')

    e, r, v = long_propagation(sats, start_time, time_step, n_steps)

    to_web = {}

    for idx in range(len(sats)):
        to_web[idx] = {"X": list(r[idx, :, 0]),
                       "Y": list(r[idx, :, 1]),
                       "Z": list(r[idx, :, 2]),
                       }

    return to_web


if __name__ == '__main__':
    # asyncio.run(main(
    #     start_time=datetime.utcnow(),
    #     time_step=timedelta(seconds=10)
    # ))

    to_web = alt_main(
        start_time=datetime.utcnow(),
        time_step=timedelta(seconds=10),
        n_steps=1000
    )

    with open("test.json", "w") as f:
        f.write(json.dumps(to_web))


