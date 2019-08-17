
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 16})

df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_apical.csv", index_col=0)

api_super = df_super["cu-o_a :"].values.T
plnr_super = df_super["cu-o_p :"].values.T
tc_super = df_super["tc :"].values.T

families = ["One", "Two", "Three"]


fig, ax = plt.subplots(figsize = (10,7))

for fam in families:
    mask = np.asarray(df_super["layers :"]==fam).nonzero()
    ax.plot(api_super[mask], tc_super[mask], 
            label=fam,
            marker="x", 
            linestyle="None",
            )

ax.set_ylabel('Tc / K')
ax.set_xlabel('Apical / Å')
fig.tight_layout()
# plt.show()
fig.savefig("api-tc.pdf", bbox_inches='tight')


# plot c against tc
df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_apical.csv", index_col=0)

c_super = df_super["latc :"].values.T
tc_super = df_super["tc :"].values.T

selection = "layers :"

# families = df_super[selection].unique()
families = ["One", "Two", "Three"]


fig, ax = plt.subplots(figsize = (10,7))
plt.set_cmap('tab10')

for fam in families:
    mask = np.asarray(df_super[selection]==fam).nonzero()
    ax.plot(c_super[mask], tc_super[mask], 
            label=fam,
            marker="x", 
            linestyle="None",
            )

ax.set_ylabel('Tc / K')
ax.set_xlabel('c / Å')
fig.tight_layout()
# plt.show()
fig.savefig("c-tc.pdf", bbox_inches='tight')



## plot a against tc
df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_apical.csv", index_col=0)

a_super = df_super["lata :"].values.T
tc_super = df_super["tc :"].values.T

selection = "layers :"

# families = df_super[selection].unique()
families = ["One", "Two", "Three"]

fig, ax = plt.subplots( figsize = (10,7))
plt.set_cmap('tab10')

for fam in families:
    mask = np.asarray(df_super[selection]==fam).nonzero()
    ax.plot(a_super[mask], tc_super[mask], 
            label=fam,
            marker="x", 
            linestyle="None",
            )



ax.set_ylabel('Tc / K')
ax.set_xlabel('a* / Å')

fig.tight_layout()
# plt.show()
fig.savefig("a-tc.pdf", bbox_inches='tight')




#%%
