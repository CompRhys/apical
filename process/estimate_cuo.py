import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


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

def main():
    df = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_cleaned.csv", index_col=0)

    # maybe discard all bar highest Tc for a given composition
    # TODO: if we do do this do we want to average the in place cu-o distances as well as latc?
    # df = df.sort_values(by=["composition :","tc :"], ascending=False) 
    # df = df[~df.duplicated("composition :")]
    # print(df.shape)

    # estimate apical distance from ICSD reference
    icsd = pd.read_csv("/home/rhys/PhD/lattice/data/processed/icsd_cleaned.csv", index_col=0)
    families = icsd["str3 :"].unique()

    df = df[df["str3 :"].isin(families)]

    df["layers :"] = df["str3 :"].map(layer_dict).values

    df["cu-o_a :"] = np.nan

    split = ["Tl1201", "Hg1201", "Tl1212", "Tl1223"]

    for fam in families:
        id_icsd = (icsd["str3 :"] == fam)
        id_df = (df["str3 :"] == fam)

        if fam in split:
            id_df = id_df.index.values[id_df.values]
            X = df.loc[id_df, ["lata :", "latc :"]].values

            id_icsd = id_icsd.index.values[id_icsd.values]
            icsd.drop_duplicates(inplace=True)
            x = icsd.loc[id_icsd, ["lata :", "latc :"]].values

            model = KMeans(n_clusters=2, random_state=0).fit(X)

            cluster_super = model.predict(X)
            cluster_icsd = model.predict(x)

            for cid in [0,1]:

                cid_icsd = id_icsd[cluster_icsd==cid]
                cid_df = id_df[cluster_super==cid]

                api_icsd = icsd.loc[cid_icsd,["cu-o_a :"]].values
                c_icsd = icsd.loc[cid_icsd,["latc :"]].values

                scale_c = StandardScaler()
                z_c = scale_c.fit_transform(c_icsd).ravel()

                scale_api = StandardScaler()
                z_api = scale_api.fit_transform(api_icsd).ravel()

                slope, intercept, r_value, p_value, std_err = stats.linregress(z_c,z_api)

                c_df = df.loc[cid_df,["latc :"]].values

                api_est = scale_api.inverse_transform(scale_c.transform(c_df) * slope)

                df.loc[cid_df, ["cu-o_a :"]] = api_est

        else:
            api_icsd = icsd.loc[id_icsd,["cu-o_a :"]].values
            c_icsd = icsd.loc[id_icsd,["latc :"]].values

            scale_c = StandardScaler()
            z_c = scale_c.fit_transform(c_icsd).ravel()

            scale_api = StandardScaler()
            z_api = scale_api.fit_transform(api_icsd).ravel()

            slope, intercept, r_value, p_value, std_err = stats.linregress(z_c,z_api)

            c_df = df.loc[id_df,["latc :"]].values

            api_est = scale_api.inverse_transform(scale_c.transform(c_df) * slope)

            if fam == "T":
                print(scale_api.inverse_transform(scale_c.transform(np.array([13.28]).reshape(-1,1)) * slope))

            df.loc[id_df, ["cu-o_a :"]] = api_est


    # estimate in plane distance from lattice parameters
    ortho = lambda x: x/np.sqrt(2) if x > 5 else x
    comparable = np.vectorize(ortho)

    df["lata :"] = comparable(df["lata :"])
    df["cu-o_p :"] = df["lata :"].values/2.

    # df["str3 :"] = df["str3 :"].map(simple_names).values

    print("Number for which we have ICSD reference {}".format(len(df.index)))

    df.to_csv("/home/rhys/PhD/lattice/data/processed/super_apical.csv", index=True , header=True)

    # # sub sample over represented families
    # df_plot = sub_sample(df, "Y123", frac=0.3)
    # df_plot = sub_sample(df, "RE123", frac=0.3)

    # df_plot = df.sort_index()

    # print(df_plot["str3 :"].value_counts())
    # print(df_plot["str3 :"].value_counts().index)

    # df_plot.to_csv("/home/rhys/PhD/lattice/data/processed/super_plot.csv", index=True , header=True)

    # add these points back in manually for the n=3 materials as they have lower Tc but are needed to see the trend.
    df_manual = df.loc[[8670,8671,6003,4526]]

    # TAKE THE TOP 20% FOR EACH FAMILY
    for fam in families:
        id_df = (df["str3 :"] == fam)
        id_df = id_df.index.values[id_df.values]
        X = df.loc[id_df, ["tc :"]].values.ravel()
        sort = np.argsort(X)
        id_df = id_df[sort]
        id_df = id_df[:-int(len(id_df)/5)]
        df = df.drop(id_df)

    df = pd.concat([df, df_manual,])

    df.to_csv("/home/rhys/PhD/lattice/data/processed/super_plot.csv", index=True , header=True)

    # TAKE THE TOP 20% ON A GRID

    # apical_bin = pd.cut(df["cu-o_a :"].values, 50)
    # planar_bin = pd.cut(df["cu-o_p :"].values, 50)

    # sep = df.groupby([apical_bin, apical_bin])


    # print(sep.to_string())


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