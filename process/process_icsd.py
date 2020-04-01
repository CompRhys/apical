import pandas as pd
import numpy as np
import os
import sys
import re

df = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cuprates.csv", index_col=0)

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
comparable = np.vectorize(ortho)

df["lata* :"] = comparable(df["lata* :"].values)

anom_index = [  # id        reason
                74094, # Hg1201 half Pb an low apical distance

                87039, #Hg2212 not reflective of SC data
                91265, 91266, 91267, # Hg2212 lata small cf supercon
                89136, 89134, 89135, # Hg2212 api smaller than expected not linear corr to latc
                83181, 83183, # Hg2212 api smaller than expected not linear corr to latc

                62947, 62948, 180517, 85371, 180519, 236446, 10252, # T low apical for given La block
                92374, 92378, # T high apical for given La block
                108997, #T api too small

                84637, 91292, 167104, 203138, 80723, #Tl1201 - doesn't match supercon density
                86427, 202898, 81165, #Tl1201 - doesn't match supercon density
                69937, 69938, #Tl1201 - doesn't match supercon density
                69906, 69909, 80656, #Tl1201 - doesn't match supercon density
                68582, # Tl2201 small lata for latc

                
                75745, 75746, 75747, 75748, 75749, 75750, 75751, # Tl1211 doesn't match supercon density
                74164, 74165, 74166, 74167, 74168, # Tl1211 doesn't match supercon density
                72584, 72585, 72586, # Tl1211 doesn't match supercon density
                74274, 74275, # Tl1211 doesn't match supercon density
                83811, 75902, 72731, 65859, 39670, 82343, 69921, # Tl1211 doesn't match supercon density   

                65323, 65324, # Tl2201 - high apical 

                91157, 91158, # Tl2212 too much Sr compared to supercon

                72230, # RE123

                80710, # Bi2212 inclusion of La not reflected in supercon
                91466, 174156, # Bi2212 Cu-O_a very low

                63428, # Y123 lattice parameters too large
 
            ]

df_anom = df[df.index.isin(anom_index)]
df_anom.to_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_removed.csv", index=True , header=True)

df = df.drop(anom_index)

# super_ = ['Y123', 'Bi2212', 'T', 'RE123', 'Y124', 'Hg1201', 'Tl1212', 'Hg1223',
#        'Hg1212', 'RE124', 'Bi2201', 'Tl1201', 'Hg2212', 'Tl1223', 'Tl2201', 'Tl2212']

df_super = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cleaned.csv", index_col=0)

fam_counts = df["str3 :"].value_counts()
common = fam_counts.index[fam_counts.values > 1]

super_ = list(set(common) & set(df_super["str3 :"].unique()))
print(set(super_).difference(set(df["str3 :"].unique())))
# super_ = [x for x in a if super_ != "RE247"]

temp = len(df)
df = df[df["str3 :"].isin(super_)]
temp -= len(df)

print(df["str3 :"].value_counts())

print("Dropping {} manually identified points".format(len(anom_index)))
print("Dropping {} points due to small samples".format(temp))
print("{} points dropped in total".format(len(anom_index)+temp))
print("{} points remain".format(len(df)))

df.to_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv", index=True , header=True)