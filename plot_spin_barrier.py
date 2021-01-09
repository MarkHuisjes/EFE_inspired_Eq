import pickle

import numpy as np
# from minepy import MINE
import matplotlib.pyplot as plt

# mine = MINE(alpha=0.6, c=15, est="mic_approx")
# mine.compute_score(g_crits, g_hosts)
# print(mine.mic())
# mine.compute_score(g_obsvs, g_hosts)
# print(mine.mic())


def gather(unitary_asteroids, quality=5):

    names = []
    periods = []
    diameters = []
    qualities = []
    external_fields = []
    fams = []
    for observation in unitary_asteroids:
        name = observation[2]
        period = observation[5]
        diam = observation[6]
        ext_field = observation[-1]
        qual_obs = observation[11]
        fam = observation[9]
        if qual_obs > quality:
            names.append(name)
            periods.append(period*3600)
            diameters.append(diam*1000)
            qualities.append(qual_obs)
            external_fields.append(ext_field)
            fams.append(fam)
    names = np.array(names)
    diameters = np.array(diameters)
    periods = np.array(periods)
    external_fields = np.array(external_fields)
    qualities = np.array(qualities)
    fams = np.array(fams)
    return diameters, periods, external_fields, qualities, fams, names


if __name__ == "__main__":

    folder = "D:/Gravity/3. MOND/0. Total Field Effect/NEFE/"
    with open(folder+"unitary_asteroids_db.pkl", "rb") as ua_db:
        unitary_asteroids = pickle.load(ua_db)

    # Get main variables
    diameters, periods, g_hosts, quals, fams, names = gather(unitary_asteroids)
    rhos = np.empty_like(diameters)
    rhos.fill(2500.0)
    rhos[fams == 'TR-J'] = 500.0
    rhos[fams == 'TNO'] = 500.0
    G = 6.674*10.0**(-11.0)
    g_surfs = G*rhos*(4/3)*3.14159*0.5*diameters
    g_angulars = (4*(3.14159**2)*0.5*diameters)/(periods**2)
    extint_ratio = np.log(g_hosts/g_surfs)
    # print(names[np.where(diameters == np.amax(diameters))])

    # Create plot dataset
    plt.figure(dpi=1000)
    # plt.tight_layout()
    plt.scatter(g_surfs, g_hosts+g_angulars, s=5, c='black')
    cm = plt.cm.get_cmap('hsv')
    sc = plt.scatter(g_surfs, g_angulars, s=5,
                     c=extint_ratio, cmap=cm)  # , vmin=0, vmax=10)
    # Plot selected families
    # f = 'TNO'
    # plt.scatter(g_surfs[fams == f], g_angulars[fams == f], s=5, c='black')
    # f = 'TR-J'
    # plt.scatter(g_surfs[fams == f], g_angulars[fams == f], s=5, c='black')

    # Execute Plot
    spin_barrier = plt.plot([0.000001, 5], [0.000001, 5], c='black')
    plt.xscale('log')
    plt.xlabel('surface gravity, $g_{int}$ (in $m/s^2$)')
    plt.yscale('log')
    plt.ylabel('observed angular acceleration, $\\alpha$ (in $m/s^2$)\n'
               + 'expected $\\alpha$ with EFE inspired eq. (black)')
    plt.colorbar(sc, label='log($g_{ext}$/$g_{int}$)')
    plt.title('Null observations from asteroids\n'
              + 'for the "EFE inspired" equation (Lelli et al. 2017)\n'
              + 'using JPL HORIZONS & MPC LCDB')
    plt.legend([spin_barrier[0]], ['Newtonian cohesionless spin barrier'])
    # plt.show()
    plt.savefig('Spin barrier.png', bbox_inches='tight')
