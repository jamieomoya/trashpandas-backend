import numpy as np
from sgp4.api import jday, SatrecArray
from datetime import datetime, timedelta
from sgp4.conveniences import jday_datetime

async def update_sat_pos(sat_arr: SatrecArray, t):
    # t = datetime.utcnow()
    jd, fr = map(np.atleast_1d, jday(t.year, t.month, t.day, t.hour, t.minute, t.second + t.microsecond / 1e6))
    e, r, v = sat_arr.sgp4(jd, fr)
    return e, r, v


def long_propagation(sat_arr: SatrecArray, start_time: datetime, time_step: timedelta, n_steps: int):
    times = np.arange(n_steps) * time_step + start_time
    x = np.asarray([jday_datetime(t) for t in times])

    # Numpy complained about these arrays not being C-contiguous, so this fixes that
    jd = np.ascontiguousarray(x[:, 0])
    fr = np.ascontiguousarray(x[:, 1])

    e, r, v = sat_arr.sgp4(jd, fr)
    return e, r, v