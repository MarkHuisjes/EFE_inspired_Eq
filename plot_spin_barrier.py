import pickle

import numpy as np
# from minepy import MINE
import matplotlib.pyplot as plt

# mine = MINE(alpha=0.6, c=15, est="mic_approx")
# mine.compute_score(g_crits, g_hosts)
# print(mine.mic())
# mine.compute_score(g_obsvs, g_hosts)
# print(mine.mic())


def gather(unitary_asteroids):

    periods = []
    diameters = []
    qualities = []
    external_fields = []
    fams = []
    for observation in unitary_asteroids:
        period = observation[5]
        diam = observation[6]
        ext_field = observation[-1]
        qual_obs = observation[11]
        fam = observation[9]
        if qual_obs > 5:
            periods.append(period*3600)
            diameters.append(diam*1000)
            qualities.append(qual_obs)
            external_fields.append(ext_field)
            fams.append(fam)
    diameters = np.array(diameters)
    periods = np.array(periods)
    external_fields = np.array(external_fields)
    qualities = np.array(qualities)
    fams = np.array(fams)
    return diameters, periods, external_fields, qualities, fams


if __name__ == "__main__":

    folder = "D:/Gravity/3. MOND/0. Total Field Effect/NEFE/"
    with open(folder+"unitary_asteroids_db.pkl", "rb") as ua_db:
        unitary_asteroids = pickle.load(ua_db)

    # Get main variables
    rho = 2500.0
    G = 6.674*10.0**(-11.0)
    diameters, periods, g_hosts, quals, fams = gather(unitary_asteroids)
    g_surfs = G*rho*(4/3)*3.14159*0.5*diameters
    g_angulars = (4*(3.14159**2)*0.5*diameters)/(periods**2)
    extint_ratio = np.log(g_hosts/g_surfs)

    # Plot dataset
    plt.scatter(g_surfs, g_hosts+g_angulars, s=5, c='black')
    cm = plt.cm.get_cmap('hsv')
    sc = plt.scatter(g_surfs, g_angulars, s=5,
                     c=extint_ratio, cmap=cm)  # , vmin=0, vmax=10)
    # Plot selected families

    # fam = 'MB-O'
    # plt.scatter(test_1[fams==fam], test_2[fams==fam], s=5, c='yellow')
    # fam = 'TR-J'
    # plt.scatter(test_1[fams==fam], test_2[fams==fam], s=5, c='black')
    # Execute Plot
    plt.plot([0.000001, 10], [0.000001, 10], c='black')
    plt.xscale('log')
    plt.yscale('log')
    plt.colorbar(sc)
    plt.show()
