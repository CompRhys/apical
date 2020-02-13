import numpy as np
import pandas as pd

from plotly.offline import plot
import plotly.graph_objs as go
from plotly import tools
import colorlover as cl

df_super = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_plot.csv", index_col=0)

latc_super = df_super["cu-o_a :"].values.T
lata_super = df_super["cu-o_p :"].values.T
tc_super = df_super["tc :"].values.T
family_super = df_super["str3 :"].values.tolist()
comp_super = df_super["composition :"].values.tolist()
ref_super = df_super.index.tolist()

df_icsd = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/icsd_cleaned.csv", index_col=0)

latc_icsd = df_icsd["cu-o_a :"].values
lata_icsd = df_icsd["cu-o_p :"].values
family_icsd = df_icsd["str3 :"].values
comp_icsd = df_icsd["composition :"].values.tolist()
ref_icsd = df_icsd.index.tolist()

hover_super = []
hover_icsd = []

for c_, a_, tc_, type_, ref_, comp_ in zip(latc_super,lata_super,tc_super,
                                        family_super,ref_super,comp_super):
    iter_string = ('SuperCon: {}<br>'
                    'Composition: {}<br>'
                    'Family: {}<br>'
                    'c: {:1.3f}<br>'
                    'a: {:1.3f} <br>'
                    'Tc: {:1.3f}'.format(ref_, comp_, type_, c_, a_, tc_))
    hover_super.append(iter_string)

# note we do not have Tc from ICSD not did we collect the compositions
for c_, a_, comp_, type_, ref_ in zip(latc_icsd,lata_icsd,comp_icsd,
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

bupu = cl.scales["11"]["qual"]["Paired"]
colours = iter(cl.interp( bupu, len(families)))

for fam in families:
    col = next(colours)

    mask = np.asarray(df_super["str3 :"]==fam).nonzero()
    trace_super = go.Scatter(x=lata_super[mask], y=latc_super[mask],
                        mode = 'markers',
                        text=hover_super[mask].tolist(),
                        hoverinfo='text',
                        marker = dict(
                            color = col,
                            symbol="circle-open",
                            ),
                        name="SuperCon "+fam,
        )

    mask = np.asarray(df_icsd["str3 :"]==fam).nonzero()
    trace_icsd = go.Scatter(x=lata_icsd[mask], y=latc_icsd[mask],
                        mode = 'markers',
                        text=hover_icsd[mask].tolist(),
                        hoverinfo='text',
                        marker = dict(
                            color = col,
                            symbol="x",
                            ),
                        name="ICSD "+fam,
        )

    trace_list.append(trace_super)
    trace_list.append(trace_icsd)
    # break


layout = go.Layout( title=go.layout.Title(
                            text='In-Plane vs Apical Cu-O distance for Cuprate Families',
                            xref='paper',
                            x=0
                        ),
                        xaxis = dict(
                                    title='In-Plane',
                                    # range=[3.7,3.95],
                                    ),
                        yaxis = dict(
                                    title='Apical',
                                    # range=[8,43],
                                    ),
                        hovermode='closest',
                    )

fig_super = go.Figure(data=trace_list, layout=layout)
plot(fig_super, filename='plot/figures/pln-api.html', include_plotlyjs='cdn',)

