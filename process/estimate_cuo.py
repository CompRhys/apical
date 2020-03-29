import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

from sklearn.linear_model import HuberRegressor, LinearRegression

layer_dict = {  'Bi2201' : "One", 
                'Bi2212' : "Two",
                'Hg1201' : "One",
                'Hg1212' : "Two",
                'Hg1223' : "Three",
                'Hg2212' : "Two",
                'RE123'  : "Two",
                'RE124'  : "Two",
                'T'      : "One",   
                'Tl1201' : "One",
                'Tl1212' : "Two",
                'Tl1223' : "Three",
                'Tl2201' : "One",
                'Tl2212' : "Two",
                'Y123'   : "Two",
                'Y124'   : "Two",
                }

type_dict = {  'Bi2201' : "Bi", 
                'Bi2212' : "Bi",
                'Hg1201' : "Hg",
                'Hg1212' : "Hg",
                'Hg1223' : "Hg",
                'Hg2212' : "Hg",
                'RE123'  : "RE",
                'RE124'  : "RE",
                'T'      : "RE",   
                'Tl1201' : "Tl",
                'Tl1212' : "Tl",
                'Tl1223' : "Tl",
                'Tl2201' : "Tl",
                'Tl2212' : "Tl",
                'Y123'   : "RE",
                'Y124'   : "RE",
                }

def main():

    sqrt2 = np.sqrt(2)
    ortho = lambda x: x/sqrt2 if x > 5 else x
    comparable = np.vectorize(ortho)

    df = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cleaned.csv", index_col=0)

    # estimate apical distance from ICSD reference
    icsd = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv", index_col=0)
    families = icsd["str3 :"].unique()

    df = df[df["str3 :"].isin(families)]

    df["layers :"] = df["str3 :"].map(layer_dict).values
    df["types :"] = df["str3 :"].map(type_dict).values

    df["cu-o_a :"] = np.nan

    df["cid :"] = np.nan

    # estimate in plane distance from lattice parameters
    ortho = lambda x: x/np.sqrt(2) if x > 5 else x
    comparable = np.vectorize(ortho)

    df["lata* :"] = comparable(df["lata :"])
    df["cu-o_p :"] = df["lata* :"].values/2.
    icsd["lata* :"] = comparable(icsd["lata :"])

    huber = HuberRegressor()

    for fam in families:
        id_df = (df["str3 :"] == fam)
        id_icsd = (icsd["str3 :"] == fam)

        api_icsd = icsd[id_icsd][["cu-o_a :"]].values
        c_icsd = icsd[id_icsd][["latc :","lata* :"]].values

        huber.fit(c_icsd,api_icsd.ravel())

        c_df = df[id_df][["latc :", "lata* :"]].values

        api_est = huber.predict(c_df)

        if fam == "T":
            print(huber.predict(((13.28, 3.76),)))
            print(huber.predict(((13.22, 3.78),)))
            print(huber.predict(((13.20, 3.79),)))

        df.loc[id_df,["cu-o_a :"]] = api_est

    print("Number for which we have ICSD reference {}".format(len(df.index)))

    df.to_csv("/home/reag2/PhD/first-year/apical/processed-data/super_apical.csv", index=True , header=True)

    # TAKE THE TOP 20% FOR EACH FAMILY

    for fam in families:
        id_df = (df["str3 :"] == fam)
        X = df[id_df][["lata :", "latc :"]].values
        model = KMeans(n_clusters=2, random_state=0).fit(X)
        cluster_super = model.predict(X)
        df.at[id_df, "cid :"] = cluster_super

        split_id = []
        for cid in [0,1]:
            cid_df = (df[id_df]["cid :"] == cid)
            cid_df = cid_df.index.values[cid_df.values]
            X = df.loc[cid_df][["tc :"]].values.ravel()
            sort = np.argsort(X)
            cid_df = cid_df[sort]
            # print(fam, max(1,int(len(cid_df)/5)))
            split_id += list(cid_df[:-max(2,int(len(cid_df)/5))])

        df = df.drop(split_id)

    print(min(icsd["str3 :"].value_counts()))

    print(df["str3 :"].value_counts()/icsd["str3 :"].value_counts())
    print(pd.unique(df["str3 :"]))

    print("Number left reference {}".format(len(df.index)))

    df.to_csv("/home/reag2/PhD/first-year/apical/processed-data/super_top.csv", index=True , header=True)

def sub_sample(df, family, frac = 0.3, alpha=2.0):
    mask = np.asarray(df["str3 :"] == family).nonzero()
    n = int(len(mask[0])*frac)
    print("\t{} of family {} found, taking {} as a sample".format(len(mask[0]), family, n))
    sample = df.iloc[mask].sample(n=n, weights=np.power(df.iloc[mask]["tc :"].values, alpha), random_state=0)
    df = df.drop(df.index[mask])
    df = df.append(sample)
    return df


if __name__ == "__main__":
    main()