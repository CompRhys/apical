# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

super_ = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cleaned.csv")
icsd = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv")

families = icsd["str3 :"].unique()

r2_vals = []

for fam in families:
    
    idx = (icsd["str3 :"] == fam)

    api = icsd.loc[idx,["cu-o_a :"]].values.ravel()
    c = icsd.loc[idx,["latc :"]].values.ravel()
    idx = icsd.loc[idx, ["id :"]].values.ravel()
    
    if len(api) < 5:
        print("{} not enough data".format(fam))
        continue
    
    # api = stats.zscore(api)
    # c = stats.zscore(c)

    api = api/np.mean(api) - 1
    c = c/np.mean(c) - 1
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(c,api)
    
    sort = c.argsort().ravel()
    
    api = api[sort]
    c = c[sort]
    idx = idx[sort]
    
    lin = np.array((c[0],c[-1]))*slope + intercept
    
    # print("familiy {}, slope {}, intercept {}, r2 {}".format(fam, slope, intercept, r_value**2))
    
    plt.scatter(c,api, marker='x')
    # print(idx)
    for i, txt in enumerate(idx):
        plt.annotate(txt, (c[i], api[i]))
    plt.plot((c[0],c[-1]),lin, 'r--')
    plt.xlabel('latc standard score')
    plt.ylabel('apical standard score')
    plt.legend(title="Familiy {}\nSlope {:2f}\nIntercept {:2f}\nR2 {:2f}".format(fam, slope, intercept, r_value**2))
    plt.show()

    r2_vals.append(r_value**2)

print(np.mean(r2_vals), np.median(r2_vals), np.std(r2_vals))

