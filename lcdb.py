import datetime
import math


def get_julian_datetime(date):
    """
    Convert a datetime object into julian float.
    Args:
        date: datetime-object of date in question

    Returns: float - Julian calculated datetime.
    Raises:
        TypeError : Incorrect parameter type
        ValueError: Date out of range of equation
    """

    # Ensure correct format
    if not isinstance(date, datetime.datetime):
        raise TypeError('Invalid type for parameter "date" - need datetime')
    if date.year < 1801 or date.year > 2099:
        raise ValueError('Datetime must be between year 1801 and 2099')

    # Perform the calculation
    julian_datetime = (367 * date.year
                       - int((7*(date.year+int((date.month+9)/12.0)))/4.0)
                       + int((275*date.month)/9.0)
                       + date.day
                       + 1721013.5
                       + (date.hour
                          + date.minute/60.0
                          + date.second/math.pow(60, 2))/24.0
                       - 0.5*math.copysign(1, (100*date.year
                                               + date.month-190002.5))
                       + 0.5)

    return julian_datetime


# GATHER OBSERVATIONS
lcdb_fdir = "/home/xubu/NEFE/LCDB/LC_DAT_PUB.TXT"
observations = []
dates = []
with open(lcdb_fdir, "r") as lcdb_file:
    lines = lcdb_file.readlines()[5:]
    counter = 0
    numslst = []
    object_counter = 0
    quality_dict = {"": -1.0, "0": 0.0,
                    "1-": 1.0, "1": 2.0, "1+": 3.0,
                    "2-": 4.0, "2": 5.0, "2+": 6.0,
                    "3-": 7.0, "3": 8.0}
    for lnidx, line in enumerate(lines):
        if len(line.strip()) == 0:
            continue
        varstrs = []
        split_pos = [7, 9, 40, 61, 70, 72, 78, 80, 82, 91, 93, 100, 102, 105,
                     107, 114, 116, 130, 146, 148, 153, 158, 161, 167, 171,
                     175, 179, 185, 189]
        for idx, pos in enumerate(split_pos):
            if idx == 0:
                previous_pos = 0
            else:
                previous_pos = split_pos[idx-1]
            varstrs.append(line[previous_pos:pos])
        for idx, item in enumerate(varstrs):
            varstrs[idx] = item.strip()

        MPCnum, entryflag, namestr, col_3, family, csource, clss = varstrs[0:7]
        dsource, dflag, diam, hsource, h, hband, asource = varstrs[7:14]
        albedoflag, alb, pflag, period, pdescrip, ampflag = varstrs[14:20]
        ampmin, ampmax, u, notes, binary, private, pole = varstrs[20:27]
        survey, extnotes = varstrs[27:]
        if hband == "":
            hband = "V"
        try:
            MPCnum = int(MPCnum)
        except ValueError:
            if MPCnum != "":
                print(lnidx)
                print("MPCnum: ", MPCnum)
            MPCnum = None
        qual_obs = quality_dict[u]
        float_list = [diam, h, alb, period, ampmin, ampmax]
        for idx, item in enumerate(float_list):
            try:
                float_list[idx] = float(item)
            except ValueError:
                if item != "":
                    print(lnidx)
                    print(idx, "float item: ", item)
                float_list[idx] = None
        diam, h, alb, period, ampmin, ampmax = float_list
        if MPCnum is not None:
            object_counter = object_counter + 1
            mpc_number = MPCnum
            name = namestr
            desig = col_3
            diameter = diam
            obj_class = clss
            fam = family
            abs_mag = h
            albedo = alb
            qual_gen = qual_obs
            minamp = ampmin
            maxamp = ampmax
            bin_flag = binary
            pole_availability = pole
            srvy_nm = survey
        try:
            date = datetime.datetime.strptime(col_3, '%Y-%m-%d')
        except ValueError:
            date = None
        if (isinstance(date, datetime.datetime) and isinstance(period, float)
            and isinstance(diameter, float)):
            date = str(get_julian_datetime(date))
            observations.append([object_counter, mpc_number, name, desig,
                                 date, period, diameter, abs_mag,
                                 obj_class, fam, albedo, qual_obs, qual_gen,
                                 minamp, maxamp,
                                 bin_flag, pole_availability, srvy_nm])
            dates.append(date)
            counter = counter + 1
