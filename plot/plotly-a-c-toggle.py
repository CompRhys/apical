import numpy as np
import pandas as pd

from plotly.offline import plot
import plotly.graph_objs as go
import colorlover as cl


df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_cleaned.csv", index_col=0)

api_super = df_super["latc :"].values.T
plnr_super = df_super["lata :"].values.T
tc_super = df_super["tc :"].values.T
family_super = df_super["str3 :"].values.tolist()
comp_super = df_super["composition :"].values.tolist()
ref_super = df_super.index.tolist()

df_icsd = pd.read_csv("/home/rhys/PhD/lattice/data/processed/icsd_cleaned.csv", index_col=0)

api_icsd = df_icsd["latc :"].values
plnr_icsd = df_icsd["lata :"].values
family_icsd = df_icsd["str3 :"].values
comp_icsd = df_icsd["composition :"].values.tolist()
ref_icsd = df_icsd.index.tolist()

hover_super = []
hover_icsd = []


for c_, a_, tc_, type_, ref_, comp_ in zip(api_super,plnr_super,tc_super,
                                        family_super,ref_super,comp_super):
    iter_string = ('SuperCon: {}<br>'
                    'Composition: {}<br>'
                    'Family: {}<br>'
                    'Apical: {:1.3f}<br>'
                    'In-Plane: {:1.3f} <br>'
                    'Tc: {:1.3f}'.format(ref_, comp_, type_, c_, a_, tc_))
    hover_super.append(iter_string)

for c_, a_, comp_, type_, ref_ in zip(api_icsd,plnr_icsd,comp_icsd,
                                        family_icsd,ref_icsd):
    iter_string = ('ICSD: {}<br>'
                    'Composition: {}<br>'
                    'Family: {}<br>'
                    'c: {:1.3f}<br>'
                    'a: {:1.3f} <br>'.format(ref_, comp_, type_, c_, a_))
    hover_icsd.append(iter_string)

hover_super = np.array(hover_super)
hover_icsd = np.array(hover_icsd)

trace_list = []

families = df_super["str3 :"].unique()
families.sort()
print(families)

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
comparable = np.vectorize(ortho)

plnr_super = comparable(plnr_super)
plnr_icsd = comparable(plnr_icsd)

for fam in families:
    mask = np.asarray(df_super["str3 :"]==fam).nonzero()
    trace_super = go.Scatter(x=plnr_super[mask], y=api_super[mask],
                        mode = 'markers',
                        text=hover_super[mask].tolist(),
                        hoverinfo='text',
                        name="{} SuperCon".format(fam),
        )

    trace_list.append(trace_super)

    mask = np.asarray(df_icsd["str3 :"]==fam).nonzero()
    trace_icsd = go.Scatter(x=plnr_icsd[mask], y=api_icsd[mask],
                        mode = 'markers',
                        text=hover_icsd[mask].tolist(),
                        hoverinfo='text',
                        name="{} ICSD".format(fam),
        )

    trace_list.append(trace_icsd)
    # break

layout = go.Layout(
                    title=go.layout.Title(
                            text='a* vs c for Cuprate Families',
                            xref='paper',
                            x=0),
                    scene = dict(
                        xaxis = dict(
                            title='a'),
                        yaxis = dict(
                            title='c*'),
                        ),
                    hovermode='closest'
    )



fig_super = go.Figure(data=trace_list, layout=layout)
plot(fig_super, filename='a-c-toggle.html', include_plotlyjs='cdn',)


