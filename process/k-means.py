import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans

super_ = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_cleaned.csv")
icsd = pd.read_csv("/home/rhys/PhD/lattice/data/processed/icsd_cleaned.csv")

families = ["Tl1201", "Hg1201", "Tl1212", "Tl1223"]

fig, ax = plt.subplots(2,2, figsize=(10,10))
plt.rcParams.update({'font.size': 16})

for i, fam in enumerate(families):
    j, k = divmod(i,2)                   
    idx = (super_["str3 :"]==fam)
    X = super_.loc[idx, ["lata :", "latc :"]].values
    y_pred = KMeans(n_clusters=2, random_state=0).fit_predict(X)
    
    ax[j,k].scatter(X[:, 0], X[:, 1], c=y_pred)
    ax[j,k].set_title(fam)
    
ax[0,0].set_ylabel("c / Å")
ax[1,0].set_ylabel("c / Å")
ax[1,0].set_xlabel("a / Å")
ax[1,1].set_xlabel("a / Å")


fig.tight_layout()
plt.savefig("k-means.pdf", bbox_inches='tight')
plt.show()