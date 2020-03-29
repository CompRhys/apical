import os
import sys
import re

import pymatgen as mg
import pandas as pd
import numpy as np

from tqdm import tqdm

import matplotlib.pyplot as plt
from sklearn.linear_model import HuberRegressor, LinearRegression


def get_Cu_O_dist(species, distances):
    """
    get all the copper oxygen distances in a material
    """
    cu_ind = [i for i, s in enumerate(species) if 'Cu' in s.formula]

    # need to resolve further edge-case to avoid osmium and oxygen sitting on the same site.
    o_ind = [i for i, s in enumerate(species) if 'O' in s.formula]
    os_ind = [i for i, s in enumerate(species) if 'Os' in s.formula]
    o_ind = list(set(o_ind).difference(set(os_ind)))

    dist_cu_o = distances[np.array(o_ind, dtype=int), np.array(cu_ind, dtype=int)[:, None]]
    
    # round the values as we cannot measure to the calculated accuracy
    # dist_cu_o = np.floor(1e4*dist_cu_o)/1e4
    dist_cu_o = np.unique(np.floor(1e4*dist_cu_o)/1e4)

    in_plane = [x for x in dist_cu_o.ravel() if (1.8 <= x < 2.0)]
    apical = [x for x in dist_cu_o.ravel() if (2.0 <= x < 2.9)]

    # Only take structures where we have a single apical distance
    if (len(apical) != 1) or (len(in_plane) == 0):
        return None, None
    else:
        in_plane = np.median(in_plane)
        apical = np.mean(apical)
        return in_plane, apical
        

def get_La_La_dist(species, distances):
    """
    """
    la_ind = [i for i, s in enumerate(species) if 'La' in s.formula]
    dist_la_la = distances[np.array(la_ind, dtype=int), np.array(la_ind, dtype=int)[:, None]]
    
    # round the values as we cannot measure to the calculated accuracy
    dist_la_la = np.unique(np.floor(1e4*dist_la_la)/1e4)

    return dist_la_la[1]    

def main(folder):

    df = pd.DataFrame()

    fail_dict = {}

    subfolders = [ f.name for f in os.scandir(folder) if f.is_dir() ]
    # print(subfolders)
    # exit()

    for subdir in subfolders:
        failed = 0
        for file in os.listdir(folder+subdir):
            try:
                col_id = int(re.findall('\d+', file.split("_")[-1])[0])
                # if col_id not in [63209, 69884]:
                #     continue
                struct = mg.Structure.from_file(folder+subdir+'/'+file)
                comp = ''.join(struct.formula.split())
                distances = struct.distance_matrix
                species = struct.species_and_occu
                lat_a, lat_b, lat_c = struct.lattice.abc
                in_plane, apical  = get_Cu_O_dist(species, distances)
                
                if apical is not None:
                    if col_id == 68947:
                        df = df.append(pd.Series((col_id, subdir, comp, 
                                        lat_c, lat_b, lat_a, apical, in_plane, None)), ignore_index=True)
                    elif subdir == 'T':
                        la_block = get_La_La_dist(species, distances)
                        df = df.append(pd.Series((col_id, subdir, comp, 
                                        lat_a, lat_b, lat_c, apical, in_plane, la_block)), ignore_index=True)
                    else:
                        df = df.append(pd.Series((col_id, subdir, comp, 
                                        lat_a, lat_b, lat_c, apical, in_plane, None)), ignore_index=True)
                else:
                    failed +=1

            except ValueError as e:
                if str(e) != "Invalid cif file with no structures!":
                    raise e
                else:
                    failed += 1
                    continue
        fail_dict[subdir] = failed
                
    print(fail_dict)

    df.columns = ["col_id :", "str3 :", "composition :",
                                "lata :", "latb :", "latc :", 
                                "cu-o_a :", "cu-o_p* :", "d_la :"]
    sqrt2 = np.sqrt(2)
    ortho = lambda x: x/sqrt2 if x > 5 else x
    comparable = np.vectorize(ortho)

    df["cu-o_p :"] = comparable(df["lata :"].values)/2.
    df["col_id :"] = df["col_id :"].astype(int) 
    df.to_csv("processed-data/icsd_scrape.csv", index=False)
    pass


if __name__ == "__main__":
    folder = sys.argv[1]

    main(folder)
    pass

