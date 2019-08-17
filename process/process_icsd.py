import pandas as pd
import numpy as np
import os
import sys
import re

df = pd.read_csv("/home/rhys/PhD/datasets/superconductivity/ICSD.csv", index_col=1)

anom_index = [  # id        reason
                78252, # latc too high, probably due to phase change
                68894, # latc too low, due to large doping of Ni for Cu
                63209, # appears highly anomalous, original paper in german doesn't give parameters directly
                91466, # Cu-O_a very low
                68188, # Cu-O_a very low 
                74166, # Cu-O_a very low
                79254, # Cu-O_a very low
                155341, # Cu-O_a appears anomolous Tl2201
                74259, 74261, 74262, # Cu-O_a appears anomolous Y124, RE124 same source, systematic error?

                75155,74276,80710, # Bi2212 inclusion of La not reflected in supercon
                79774, 72584, 75746, 75747, 75750, 82343, # Tl1212 inclusion of Pr and Nd not reflected in supercon
                69906, 69909, 69937, 80656, 81165, 202898,  # Tl1201 too much Sr compared to supercon
                89161, 91157, 91158, # Tl2212 too much Sr compared to supercon
                50264, # Hg1201
                78679, # Hg2212 extra Cu included
                74426, 75713, # Both Y124 with no doping but destroy the trend we see.
                63322, # Y123 no doping but signifcantly higher than expected apical distance. inconsistent with DFT and other experiments
                56509, # Y123 containing 0.4 Gd for Y 
                64658, # Y123 containing 0.5 Pd for Cu
                83181, 83183, 89135, # Hg2212 
                72212, # Bi2212 however we have (Bi0.5Pb0.5)2212 
                63210, # Bi2212 high Sr content and low Cu-Oa
                68672, # Bi2212 high Sr content and low Cu-Oa
                71825, # Bi2212 Cu-O_a very low 2.2 cf 2.5
                190110, 161679, # Tl2212 Ca ~0.38 instead of Tl and low Cu-O_a
                91162, # Tl2212 very hetrogenous structure no obvious trend as to why low Cu-O_a
                64645, # Tl2212 excess copper gives rise to very large Cu-O_a
                73654, # Bi2201 BiPbBaLaCu system not reflected in supercon
                66300, # excessively large lata when compared to similar systems, poission/jahn-teller effect?
                67334, # Tl2201 large apical for low c 
                41962, # Tl2201 large apical for low c high oxygen doping
                66795, # RE247 
            ]



df = df.drop(anom_index)

# super_ = ['Y123', 'Bi2212', 'T', 'RE123', 'Y124', 'Hg1201', 'Tl1212', 'Hg1223',
#        'Hg1212', 'RE124', 'Bi2201', 'Tl1201', 'Hg2212', 'Tl1223', 'Tl2201', 'Tl2212']

df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_cleaned.csv", index_col=0)

fam_counts = df["str3 :"].value_counts()
common = fam_counts.index[fam_counts.values > 5]

super_ = list(set(common) & set(df_super["str3 :"].unique()))
# super_ = [x for x in a if super_ != "RE247"]

temp = len(df)
df = df[df["str3 :"].isin(super_)]
temp -= len(df)

print(df["str3 :"].value_counts())

print("Dropping {} manually identified points".format(len(anom_index)))
print("Dropping {} points due to small samples".format(temp))
print("{} points dropped in total".format(len(anom_index)+temp))
print("{} points remain".format(len(df)))

# df["str3 :"] =  df["str3 :"].replace("RE123", "Y123" )
# df["str3 :"] =  df["str3 :"].replace("RE124", "Y124" )

# df["str3 :"] =  df["str3 :"].replace("Tl1201", "1201" )
# df["str3 :"] =  df["str3 :"].replace("Hg1201", "1201" )

# df["str3 :"] =  df["str3 :"].replace("Tl1212", "1212" )
# df["str3 :"] =  df["str3 :"].replace("Hg1212", "1212" )

# df["str3 :"] =  df["str3 :"].replace("Hg1223", "1223" )
# df["str3 :"] =  df["str3 :"].replace("Tl1223", "1223" )

# # df["str3 :"] =  df["str3 :"].replace("Bi2201", "2201" )
# df["str3 :"] =  df["str3 :"].replace("Tl2201", "2201" )

# # df["str3 :"] =  df["str3 :"].replace("Bi2212", "2212" )
# df["str3 :"] =  df["str3 :"].replace("Tl2212", "2212" )
# df["str3 :"] =  df["str3 :"].replace("Hg2212", "2212" )


df.to_csv("/home/rhys/PhD/lattice/data/processed/icsd_cleaned.csv", index=True , header=True)