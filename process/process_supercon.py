import pandas as pd
import numpy as np
import os
import sys
import re

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
comparable = np.vectorize(ortho)

def main():
    # Load all the expected cuprate
    df = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cuprates.csv", index_col="num :" )

    # select only data for which the lattice parameters are reported
    df = df[pd.notnull(df["lata :"])]
    df = df[pd.notnull(df["latc :"])]
    print("lattice information is recorded for {}".format(len(df.index)))

    # df["lata :"] = np.nanmean([df["lata :"].values, df["latb :"].values], axis=0)
    df["lata* :"] = df[["lata :", "latb :"]].mean(axis=1)

    # select only data for which the family information is recorded
    # TODO: we can potentially estimate families by whether the one-hot
    #       norm is within a given tolerence

    df = df[pd.notnull(df["str3 :"])]
    print("families information is recorded for {}".format(len(df.index)))

    # attempt to constrain the familiy types
    df = standardise_families(df)

    # only take families for which the total number is large
    fam_counts = df["str3 :"].value_counts()
    common = fam_counts.index[fam_counts.values > 10]
    df = df[df["str3 :"].isin(common)]
    print(df["str3 :"].value_counts().to_string())

    # exclude 247 structures as they are alternative 1212/2212 and so cannot be compared directly
    df = df[~(df["str3 :"] == "Y247")]
    df = df[~(df["str3 :"] == "RE247")]

    mask = (df["str3 :"] == "RE124") & (df["latc :"] < 27.05)
    df = df[~mask]

    mask = (df["str3 :"] == "Y123") & (df["latc :"] < 11.45)
    df = df[~mask]

    mask = (df["str3 :"] == "T") & (df["lata :"] > 4.5)
    df = df[~mask]

    mask = (df["str3 :"] == "Tl2201") & (df["lata :"] > 4.5)
    df = df[~mask]

    mask = (df["str3 :"] == "Bi2212") & (df["lata :"] < 4.5)
    df = df[~mask]

    df = df.sort_index()

    df["lata* :"] = comparable(df["lata* :"].values)
    df.to_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cleaned.csv", index=True , header=True)

    print("Number for which we have 10 or more samples {}".format(len(df.index)))


def standardise_families(df):
    """
    adopt a more standard referencing system.
    """

    # Hg majority therefore Hg1223
    df["str3 :"] = df["str3 :"].replace("Hg,Re-1223", "Hg1223")
    df["str3 :"] = df["str3 :"].replace("Nb123", "RE123")

    # Sr2CuO4 labeled as T when it is a separate sub-class
    idx = [7890, 33900 33901, 40877, 40882, 152471, 152472, 152473, 8446]
    df.at[idx, 'str3 :'] = "Sr0201"

    #
    df.at[[3680], 'str3 :'] = "Tl2234"
    df.at[[3681], 'str3 :'] = "Tl2245"
    df.at[[5414], 'str3 :'] = "Tl1223"
    df.at[[6085, 6086, 6088], "str3 :"] = "Hg1223"

    # swap lata and latc for Ga1212
    idx = (df["str3 :"] == "Ga1212") & (df["lata :"] > 10)
    df.loc[idx, ["lata :", "latc :"]] = df.loc[idx, ["latc :", "lata :"]].values

    # relabel Y123, Y124 and Y247 if no yttrium present
    idx = (df["str3 :"].eq("Y123")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE123"

    idx = (df["str3 :"].eq("Y124")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE124"

    idx = (df["str3 :"].eq("Y247")) & (~df["composition :"].str.contains("Y(?=[0-9])"))
    df.loc[idx, ["str3 :"]] = "RE247"

    return df


if __name__ == "__main__":
    main()
