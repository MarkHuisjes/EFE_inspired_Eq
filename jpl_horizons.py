import os
import subprocess
import re

import numpy as np

from observations import observations, dates


def get_state_vectors(observations, dates):

    queries = make_queries(observations, dates)
    executed_queries = len(os.listdir("/home/xubu/NEFE/Ephms/"))
    for query in queries:
        outp, err = launch_query(query)
        executed_queries = executed_queries + 1
        print(executed_queries)
        if len(os.listdir("/home/xubu/NEFE/Ephms/")) != executed_queries:
            print(query, outp, err)
            break
        # if executed_queries > 15:
        #     break

def launch_query(query_string):
    """
    Shell out to wget and retrieve state vectors from HORIZONS
    """

    proc = subprocess.Popen(
        [query_string],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        shell=True)
    # Required check to know if subprocess is finished
    output, error = proc.communicate()

    return output, error


def make_queries(observations, dates):

    trim_pattern = re.compile(r'\W')
    queries = []
    objects, names = create_objects(observations, dates)
    for obj in objects:
        if len(objects[obj]) > 1000:
            date_chunks = np.array_split(objects[obj], 10)
            for idx, date_chunk in enumerate(date_chunks):
                dates_string = ','.join(list(date_chunk))
                command = make_command(obj, names[obj])
                if command == 'skip':
                    continue
                file_name = make_filename(obj, names[obj], trim_pattern)
                file_name = file_name[:-4] + "_{}.txt".format(str(idx))
                fnm_path = "/home/xubu/NEFE/Ephms/{}".format(file_name)
                if not os.path.isfile(fnm_path):
                    query = fill_query(command, dates_string, file_name)
                    queries.append(query)
        else:
            dates_string = ','.join(objects[obj])
            command = make_command(obj, names[obj])
            if command == 'skip':
                continue
            file_name = make_filename(obj, names[obj], trim_pattern)
            fnm_path = "/home/xubu/NEFE/Ephms/{}".format(file_name)
            if not os.path.isfile(fnm_path):
                query = fill_query(command, dates_string, file_name)
                queries.append(query)

    return queries


def create_objects(observations, dates):

    bodies = {}
    lables = {}
    major_bodies_list = [-199, -299, -301, -399, -499, -501, -502, -503, -504,
                         -599, -606, -699, -799, -801, -899, -999]

    # Create asteroids in bodies with lists of observation dates
    for observation in observations:
        object_counter, MPCnum, name, desig, date = observation[:5]
        if object_counter in bodies:
            bodies[object_counter].append(date)
        else:
            bodies[object_counter] = [date]
            lables[object_counter] = [MPCnum, name, desig]

    # Create major bodies in bodies with list of all dates
    for body in major_bodies_list:
        bodies[body] = dates
        lables[body] = [None, None, None]

    # Overwrite Ceres, Pallas and Vesta data regardless of observations
    # This is needed because we are use them as major bodies (gravitationally)
    bodies[1], bodies[2], bodies[4] = dates, dates, dates
    lables[2], lables[4] = [2, "Pallas", None], [4, "Vesta", None]

    # Make bodies lists of dates unique and sort them
    for body in bodies:
        bodies[body] = sorted(list(set(bodies[body])))

    return bodies, lables


def make_command(objcounter, identifiers):

    invalid_str = ""
    number, name, designation = identifiers
    if objcounter < 0:
        command = str(abs(objcounter))
    elif number > 0:
        command = '{}%3B'.format(number)
    elif isinstance(designation, str) and designation != invalid_str:
        command = '\'DES={}\''.format(designation)
    elif isinstance(name, str) and name.strip() != invalid_str:
        command = '\'DES={}\''.format(name)
    else:
        write_error(objcounter, number, name, designation)
        command = 'skip'

    return command

def make_filename(objcounter, identifiers, ptrn):

    invalid_str = ""
    number, name, designation = identifiers
    if objcounter < 0:
        filename = "".join(["_", str(objcounter).replace("-", "min"), ".txt"])
    elif number > 0:
        filename = "".join(["_", str(number), ".txt"])
    elif isinstance(designation, str) and designation != invalid_str:
        filename = "".join(["_", re.sub(ptrn, '', designation), ".txt"])
    elif isinstance(name, str) and name != invalid_str:
        filename = "".join(["_", re.sub(ptrn, '', name), ".txt"])
    else:
        filename = 'skip'

    return filename

def fill_query(cmd_str, dates_str, f_nm_str):

    query = ''.join(['wget --secure-protocol=auto --no-check-certificate ',
                     '"https://ssd.jpl.nasa.gov/horizons_batch.cgi?batch=1',
                     '&COMMAND={}'.format(cmd_str),
                     '&MAKE_EPHEM=\'YES\'&TABLE_TYPE=\'VECTOR\'',
                     '&OUT_UNITS=AU-D',
                     '&TLIST=\'{}\''.format(dates_str),
                     '&CENTER=\'@sun\'&REF_PLANE=\'frame\'',
                     '&CSV_FORMAT=\'YES\'&VEC_TABLE=\'2\'" ',
                     '-O "/home/xubu/NEFE/Ephms/{}"'.format(f_nm_str)])
    return query

def write_error(a, b, c, d):
    
    variables = ", ".join([a, b, c, d])
    types = ", ".join([type(a), type(b), type(c), type(d)])
    with open("/home/xubu/NEFE/log.TXT", 'a') as log:
        log.write(variables)
        log.write(types)

if __name__ == "__main__":
    get_state_vectors(observations, dates)
