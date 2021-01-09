import os
import re
import pickle

import numpy as np

from lcdb import observations


def generate_major_list():

    emph_path = '/home/xubu/NEFE/Ephms/'
    major_list = []
    for file in os.listdir(emph_path):
        if os.stat(emph_path+file).st_size > 100000:
            if file[:-6] not in major_list:
                major_list.append(file[:-6])

    return major_list


def generate_sv_database():

    # Read state vector files to dictionary structure and major body list
    emph_path = '/home/xubu/NEFE/Ephms/'
    object_dict = {}
    for file in os.listdir(emph_path):
        if os.stat(emph_path+file).st_size > 100000:
            object_lable = file[:-6]
        else:
            object_lable = file[:-4]
        sv_list = read_svs_from_file('/home/xubu/NEFE/Ephms/{}'.format(file))
        if sv_list != 'skip':
            for row in sv_list:
                date = row[0][:-8]
                sv_p = [float(x) for x in row[2:5]]
                sv_v = [float(x) for x in row[5:]]
                if object_lable in object_dict:
                    object_dict[object_lable][date] = (sv_p, sv_v)
                else:
                    object_dict[object_lable] = {date: (sv_p, sv_v)}
    pk = open("/home/xubu/NEFE/objects.pkl", "wb")
    pickle.dump(object_dict, pk)
    pk.close()

    return object_dict


def read_svs_from_file(filename):

    with open(filename) as targetfile:

        if 'No matches found.' in targetfile.read():
            ephm_lines = 'skip'

        targetfile.seek(0)
        config = False
        ephm_lines = []
        for line in targetfile.readlines():
            if line.strip() == '$$SOE':
                config = True
                continue
            if line.strip() == '$$EOE':
                config = False
                continue
            if config:
                line_list = line[:-2].split(',')
                line_list = [x.strip() for x in line_list]
                ephm_lines.append(line_list)

        return ephm_lines


def make_lable(objcounter, number, name, designation, ptrn):

    invalid_str = ""
    if objcounter < 0:
        filename = "".join(["_", str(objcounter).replace("-", "min")])
    elif number > 0:
        filename = "".join(["_", str(number)])
    elif isinstance(designation, str) and designation != invalid_str:
        filename = "".join(["_", re.sub(ptrn, '', designation)])
    elif isinstance(name, str) and name != invalid_str:
        filename = "".join(["_", re.sub(ptrn, '', name)])
    else:
        filename = 'skip'

    return filename


def get_ext_field(minor_svp, major_svp_list, major_mass_list):

    G = 6.674*10.0**(-11.0)
    minor_svp = np.asarray(minor_svp) * 149597870700.0
    major_svp_list = [np.asarray(x) * 149597870700.0 for x in major_svp_list]
    differences = [major_svp - minor_svp for major_svp in major_svp_list]
    distances = [np.linalg.norm(difference) for difference in differences]
    uvs = []
    for idx, difference in enumerate(differences):
        uvs.append(difference/distances[idx])
    accelerations = []
    # For now there are no observations of Pluto's rotation period in the LCDB.
    # Should this change and you want to use this include an exception here.
    # Because Pluto's mass is being used as a major body as well.
    for idx, M in enumerate(major_mass_list):
        accelerations.append(uvs[idx]*G*M/(distances[idx]**2))
    net_accel_vect = np.add.reduce(accelerations)
    net_acceleration = np.linalg.norm(net_accel_vect)

    return net_acceleration


if __name__ == "__main__":

    # Load State Vector Database
    if os.path.exists("/home/xubu/NEFE/objects.pkl"):
        with open("objects.pkl", "rb") as pk:
            object_dict = pickle.load(pk)
    else:
        object_dict = generate_sv_database()
    # Load list of major bodies + Ceres, Pallas & Vesta
    major_list = generate_major_list()
    # Load masses of bodies in major_list
    mass_dict = {"_min10":  1.989100*10.0**(30.0),
                 "_min199": 3.301140*10.0**(23.0),
                 "_min299": 4.867470*10.0**(24.0),
                 "_min301": 7.347320*10.0**(22.0),
                 "_min399": 5.972370*10.0**(24.0),
                 "_min499": 6.417120*10.0**(23.0),
                 "_min501": 8.932559*10.0**(22.0),
                 "_min502": 4.798761*10.0**(22.0),
                 "_min503": 1.481832*10.0**(23.0),
                 "_min504": 1.075724*10.0**(23.0),
                 "_min599": 1.898187*10.0**(27.0),
                 "_min606": 1.345560*10.0**(23.0),
                 "_min699": 5.683174*10.0**(26.0),
                 "_min799": 8.681270*10.0**(25.0),
                 "_min801": 2.138076*10.0**(22.0),
                 "_min899": 1.024126*10.0**(26.0),
                 "_min999": 1.303000*10.0**(22.0),
                 "_1":      9.384381*10.0**(20.0),
                 "_2":      2.590760*10.0**(20.0),
                 "_4":      2.040000*10.0**(20.0)}

    # Generate Unitary Asteroid Database
    unitary_asteroids = []
    # For each observation calculate the external field
    trim_pattern = re.compile(r'\W')
    for observation in observations:
        object_counter, MPCnum, name, desig, date = observation[:5]
        lable = make_lable(object_counter, MPCnum, name, desig, trim_pattern)
        try:
            object_position = object_dict[lable][date][0]
        except KeyError:
            continue
        major_body_positions = []
        major_body_masses = []
        for major_body in major_list:
            if major_body != lable:
                major_body_positions.append(object_dict[major_body][date][0])
                major_body_masses.append(mass_dict[major_body])
        major_body_positions.append([0.0, 0.0, 0.0])  # sun
        major_body_masses.append(mass_dict['_min10'])  # sun
        ext_field = get_ext_field(object_position,
                                  major_body_positions, major_body_masses)
        unitary_asteroids.append(observation+[object_position, ext_field])

    # Save ext, field as variable with other obs variables to pickle
    ua_db = open("/home/xubu/NEFE/unitary_asteroids_db.pkl", "wb")
    pickle.dump(unitary_asteroids, ua_db)
    pk.close()
