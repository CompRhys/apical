# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import HuberRegressor, LinearRegression
from sklearn.metrics import r2_score

super_ = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_cleaned.csv")
icsd = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv")

families = icsd["str3 :"].unique()

r2_vals = []

huber = HuberRegressor()

for fam in families:
    
    idx = (icsd["str3 :"] == fam)

    api_icsd = icsd[idx][["cu-o_a :"]].values
    c_icsd = icsd[idx][["latc :",]].values
    idx = icsd.loc[idx]["col_id :"].values
    
    if len(api_icsd) < 5:
        print("{} not enough data".format(fam))
        continue
    
    huber.fit(c_icsd,api_icsd.ravel())

    slope = huber.coef_
    intercept = huber.intercept_
    
    api_est = huber.predict(c_icsd)

    r2 = r2_score(api_est, api_icsd)
    r2_vals.append(r2)

    sort = c_icsd.argsort().ravel()
    
    lin = np.array((min(c_icsd),max(c_icsd)))*slope + intercept
    
    # print("familiy {}, slope {}, intercept {}, r2 {}".format(fam, slope, intercept, r_value**2))
    
    plt.scatter(c_icsd,api_icsd, marker='x')
    # print(idx)
    for i, txt in enumerate(idx):
        plt.annotate(txt, (c_icsd[i], api_icsd[i]))
    plt.plot((c[0],c[-1]),lin, 'r--')
    plt.xlabel('latc standard score')
    plt.ylabel('apical standard score')
    # plt.legend(title="Familiy {}\nSlope {:2f}\nIntercept {:2f}\nR2 {:2f}".format(fam, slope, intercept, r2))
    plt.show()

print(dict(zip(families,r2_vals)))
print(np.mean(r2_vals), np.median(r2_vals), np.std(r2_vals))



# %%
