import pandas as pd
import numpy as np
import os
import sys
import re

selected = ["num :", "element :", "name :", "str3 :", 
            "tc :", "lata :", "latb :", "latc :", "refno :",
            "ma1 :", "ma2 :", "mb1 :", "mb2 :", "mc1 :",
            "mc2 :", "md1 :", "md2 :", "me1 :", "me2 :", 
            "mf1 :", "mf2 :", "mg1 :", "mg2 :", "mh1 :", 
            "mh2 :", "mi1 :", "mi2 :", "mo1 :", "mo2 :", "oz :"]

elements = ["ma1 :", "mb1 :", "mc1 :", "md1 :",
            "me1 :", "mf1 :", "mg1 :", "mh1 :",
            "mi1 :", "mo1 :"]

composition = ["ma1 :", "ma2 :", "mb1 :", "mb2 :", "mc1 :", "mc2 :",
               "md1 :", "md2 :", "me1 :", "me2 :", "mf1 :", "mf2 :",
               "mg1 :", "mg2 :", "mh1 :", "mh2 :", "mi1 :", "mi2 :",
               "mo1 :", "mo2 :"]

clean = ["composition :", "str3 :", "tc :", "lata :", "latb :", "latc :", "refno :"]

def main():
    df = pd.read_csv("/home/reag2/PhD/datasets/superconductivity/supercon/full.csv", index_col=0)

    # take a subset of the columns
    df = df[selected]
    df = df.set_index("num :")
    print("Starting with {} datapoints".format(len(df.index)))

    # only take data where Tc has been reported
    df = df[pd.notnull(df["tc :"])]
    print("Tc reported for {} materials".format(len(df.index)))

    df = df[df["tc :"]>10]
    print("Tc > 10 for {} materials".format(len(df.index)))


    # Remove elements that don"t contain Copper and Oxygen
    df = df[df[elements].apply(lambda r: r.str.contains("Cu").any(), axis=1)]
    print("Of these {} are contain copper".format(len(df.index)))

    # df = df[df[elements].apply(lambda r: r.str.contains("O").any(), axis=1)]
    # print("Of these {} are also contain oxygen".format(len(df.index)))

    # Combine the various oxygen entries into composition string
    df = merge_oz(df)
    df["composition :"] = composition_str(df).values

    # Remove borate and delafossite systems as well as other erronously entered cuprates
    df = df[df["mo2 :"] > 3]
    print("Of these {} are believed to be cuprates".format(len(df.index)))

    # remove points manually identified as being errors
    df = manual_removals(df)

    df = df[clean]

    df.to_csv("/home/reag2/PhD/lattice/data/processed/super_cuprates.csv", index=True , header=True)

    # df["lata :"] = np.nanmean([df["lata :"].values, df["latb :"].values], axis=0)
    df["lata "] = df[["lata :", "latb :"]].mean(axis=1)

    df = df[pd.notnull(df["lata :"])]
    df = df[pd.notnull(df["latc :"])]

    print("lattice information is recorded for {}".format(len(df.index)))

    df = df[pd.notnull(df["str3 :"])]
    print("families information is recorded for {}".format(len(df.index)))

    # attempt to constrain the familiy types
    df = standardise_families(df)

    fam_counts = df["str3 :"].value_counts()
    print(fam_counts.to_string())
    common = fam_counts.index[fam_counts.values > 10]
    df = df[df["str3 :"].isin(common)]

    df = df[~(df["str3 :"]=="Y247")]
    df = df[~(df["str3 :"]=="RE247")]

    df = df.sort_index()    

    df.to_csv("/home/reag2/PhD/lattice/data/processed/super_cleaned.csv", index=True , header=True)

    print("Number for which we have 10 or more samples {}".format(len(df.index)))


def manual_removals(df, very_clean=True):
    """
    clean rows that have manually been identified as erroneous
    """        

    lat_err = [ 140,          # tc reported as 275.0 which isn't feasible for a Re123 structure
                #  2570, 2571, 2572, 2573, # element recorded as LI rather than Li (manually corrected)
                #  3135, 3136, 3137, # element recorded as LI rather than Li (manually corrected)
                # 3525, 3524, 12179,   # oxygen entered as Z+0.2x where Z=8 but not given
                8835, 8868,     # compounds given with zero weighted elements            
                8319,           # 1013.0 oxygens rather than 10.13
                8472,           # 6050.0 oxygens rather than 6.05
                30959,          # Sm1Ba-1Cu3O6.94, cannot have negative  
                5031,           # appears anomolously small lata 5.13 but as reported in paper. 
                9676,           # latc given as 27271.0 not 27.271
                30915,          # latc given as 11684.0 not 11.684
                8277,           # lata given as 30921.0 not 30.921
                9752,           # latc given as 38586.0 not 38.586
                8099,           # reported at Hg1223 when actually Hg1212
                32339, 32338,   # removed due to lata = latc
                9946,           # latc ~ 15 cf ~13 normally for T
                5777,           # lata reported as latc
                6924,           # superconducting copper oxychromate not cuprate
                5221,           # latc is twice usual latc for Hg1212
                5768,           # latc is twice usual latc for Y123
                5461, 5462,     # reported as Hg1201 but (Hg,Tran)1Sr4C1Cu2O9
                3707,           # reported as Tl2223 when it is likely Tl1223
                5141,           # lata recorded as 6.858 but paper gives 3.858
                6057,           # lata recorded as 3.67325 but paper only reports 
                                # lata>3.8 but online copy unclear.
                20162,20163,    # latc larger than expected (journal not accessible)
                20106,          # appears to be mis-entered lata 3.395 vs 3.895 (journal not accessible)
                5709,           # appears to be mis-entered latc 37.193 vs 27.193 (nb inconsistent with journal)
                10105,          # Iodine intercalated structure has larger latc than typical IBi2212 not Bi2212
                7666, 7667, 7668, 7669,  # Orthorhombic structure where lata!=latb which skews the average
                6723, 6724, 6725, 6727, 6728,  # data misentered latc should be 11.381, 11.389, 11.457, 11.560, 11.594   
                7085, 7086, 7087, # reported with bi0.16 as opposed to 1.6, also appear to be duplicated entries.
                7054,           # lata mis-entered as 5.043 as opposed to 5.403
                34575, 34576, 34577, 34578, # lata correctly entered as publication -> BPSCCO 
                                             # needs to be treated as a separate family,
                34372,          # BPSCCO as above therefore not comparable to Ba2223 as entered
                1534,           # BPSCCO as above therefore not comparable to Ba2223 as entered
                11317,          # lata misentered as 3.684 when paper gives 3.864
                2928,           # lata misentered as 3.736 when paper gives 3.808
                151031, 151032, 151033, 151034, 151035, 151036, # Cu0.5Tl0.5-1223 not Tl1223 with Ni subbing a copper
                40423, 40424,   # Cu0.5Tl0.5-1223 not Tl1223
                152359,         # Cu0.5Tl0.5-1223 not Tl1223
                152360, 152361, 152362,  # Cu0.5Tl0.5-1223 not Tl1223 with Cd subbing a copper
                20290,          # Cuprocarbonate not Hg1201
                40364,          # latc reported as 11.1201 rather than 12.1201 as given in paper
                5503,           # recorded as Hg1212 but actually gives data for a Hg1223 sample
                5770,           # reported with latc twice typical value
                12318,          # latc misreported as 11.063 rather than 11.6635
                9696, 9680,     # latc misreported at 27.981 rather than 26.981 as in original paper, 
                                # note both correspond to same sample in different papers
                7863, 7864, 7865, 7866, # this are flourinated compounds whose lattice values are correct 
                                         # but the composition strings are inaccurate (F_x,O_1-x)4 -> FO4
                1370, 3973,     # lata is give as a multiple (3x) of expected value
                4664,           # lata given as 3.371 rather than 3.71 as in paper
                426,            # lata reported as 3.382 rather than 3.82
                4205,           # superlattice structure not pure structure. 
                7231, 7232,     # recorded as Nd0.7Sr1.3Cu1.0FO4.0-z rather than Nd0.7Sr1.3Cu1.0(F,O)zO4-z. 
                                # Discount the points rather than florine
                8579,           # multiphase and the lattice parameters are not properly given for 1201 in paper only 2201.
                2607,           # Sample contains no Tl but labelled at Tl1212
                34003, 34004, 34005, # repoorted as 3-x rather than 2-x Y123
                34006, 34007, 34008, # repoorted as 3-x rather than 2-x Y123
                34009, 34010, 34012, # repoorted as 3-x rather than 2-x Y123
                34012, 34013, 34014, # repoorted as 3-x rather than 2-x Y123
                34015, 34016, # repoorted as 3-x rather than 2-x Y123
                ]

    hunch_err = [
                10057,10064,    # these are as reported in the original paper with c = 14.2 but I believe 
                                # them to be anomolous due to 21 counter examples for 10057
                                # probably due to a phase change in the system
                10000,          # the values for the a and b lattice parameters reported here are somewhat 
                                # anomolous as it's a single datapoint outlier we exclude it
                2119,8278,8423,8425,
                4178,12666,13008,150402,
                8936,9741,8522,5342,4663,
                2974,150170,9683,9685,33476,
                36,             # lata and latc are swapped
                5838,           # Contains Ei not allowed by current featurisations
    ]

    err_index = lat_err

    if very_clean:
        err_index = err_index + hunch_err

    print("\tTotal number of anomalous points removed: {}".format(len(err_index)))

    df = df.drop(err_index)

    return df


def standardise_families(df):
    """
    adopt a more standard referencing system.
    """

    # Hg majority therefore Hg1223
    df["str3 :"] =  df["str3 :"].replace("Hg,Re-1223", "Hg1223" )
    df["str3 :"] =  df["str3 :"].replace("Nb123", "RE123" )

    # Sr2CuO4 labeled as T when it is a separate sub-class
    idx = [7890,33900,33901,40877,40882,152471,152472,152473, 8446]
    df.at[idx, 'str3 :'] = "Sr0201"

    # 
    df.at[[3680], 'str3 :'] = "Tl2234"
    df.at[[3681], 'str3 :'] = "Tl2245"
    df.at[[5414], 'str3 :'] = "Tl1223"
    df.at[[6085,6086,6088], "str3 :"] = "Hg1223"     

    # swap lata and latc for Ga1212
    idx = (df["str3 :"] == "Ga1212") & (df["lata :"] > 10)
    df.loc[idx,["lata :", "latc :"]] = df.loc[idx,["latc :", "lata :"]].values

    # relabel Y123, Y124 and Y247 if no yttrium present
    idx = (df["str3 :"].eq("Y123")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE123"

    idx = (df["str3 :"].eq("Y124")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE124"

    idx = (df["str3 :"].eq("Y247")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE247"

    return df


def merge_oz(df, excess_oxy=True):
    """
    Where oz replace mo2 by oz
    if mo2 contains letters and numbers truncate to number

    further steps might include:
    if mo2 only contains letters then check family for oxygen count
    if mo2 still contains letter then return num for manual correction

    however currently this would only enable us to use 1-2% more of the 
    original dataset and so 
    """
    if excess_oxy == True:
        df["mo2 :"].loc[df["oz :"].notnull()] = df["oz :"].loc[
            df["oz :"].notnull()]

    # axis 1 -> columns
    df["mo2 :"] = df["mo2 :"].apply(lambda x: split_mo2(x))

    # discard
    df = df.loc[df["mo2 :"].notnull()]

    return df


def split_mo2(oxy):
    """
    extract the stochiometric oxygen for a string with unknown excess oxygen
    """
    regex1 = r"([O])"
    regex2 = r"([\+\-])"

    oxy = re.split(regex1, str(oxy))[-1]
    oxy = re.split(regex2, oxy)[0]

    try:
        return float(oxy)
    except ValueError:
        return np.nan


def composition_str(df):
    """
    take the element and weight rows and combine them into a 
    composition string removing any nan"s that are present.
    """
    def remove_nan(string):
        """ remove nan from a string """
        return re.sub(r"(nan)", "", string)
        
    df = df[composition].apply(lambda x: "".join(x.map(str)), axis=1)
    df = df.apply(lambda x: remove_nan(x))
    return df


if __name__ == "__main__":
    main()