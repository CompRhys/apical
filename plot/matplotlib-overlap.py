import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df_super = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_apical.csv", index_col=0)

lata_super = df_super["lata :"].values.T
latc_super = df_super["latc :"].values.T
family_super = df_super["str3 :"].values

df_icsd = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv", index_col=0)

latc_icsd = df_icsd["latc :"].values
lata_icsd = df_icsd["lata :"].values
family_icsd = df_icsd["str3 :"].values

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
compare = np.vectorize(lambda x: x/sqrt2 if x > 5 else x)
lata_super = compare(lata_super)
lata_icsd = compare(lata_icsd)

families = df_super["str3 :"].unique()
families.sort()

num = len(families)
rows = 4
cols = int((num+rows-1)/rows)

fig_2d, ax_2d = plt.subplots(cols, rows, squeeze=False, figsize=(cols*3,rows*3))
plt.rcParams.update({'font.size': 12})

for i, ftype in enumerate(families):
    j, k = divmod(i, rows)
    
    mask_super = np.where(family_super==ftype)
    a_super = lata_super[mask_super] 
    c_super = latc_super[mask_super] 
    
    mask_icsd = np.where(family_icsd==ftype)
    a_icsd = lata_icsd[mask_icsd]
    c_icsd = latc_icsd[mask_icsd]
    
    ax_2d[j,k].plot(a_super, c_super, 'o', markersize=5)
    ax_2d[j,k].plot(a_icsd, c_icsd, 'x')
    ax_2d[j,k].set_title(ftype)

ax_2d[0,0].set_ylabel("c / Å")
ax_2d[1,0].set_ylabel("c / Å")
ax_2d[2,0].set_ylabel("c / Å")
ax_2d[3,0].set_xlabel("a / Å")
ax_2d[3,0].set_ylabel("c / Å")
ax_2d[3,1].set_xlabel("a / Å")
ax_2d[3,2].set_xlabel("a / Å")
ax_2d[3,3].set_xlabel("a / Å")


fig_2d.tight_layout()
plt.show()