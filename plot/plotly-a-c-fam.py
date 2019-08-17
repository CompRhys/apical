import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.plotly as py
from plotly import tools
from plotly.offline import plot

df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_cleaned.csv", index_col=0)

latc_super = df_super["latc :"].values.T
lata_super = df_super["lata :"].values.T
tc_super = df_super["tc :"].values.T
family_super = df_super["str3 :"].values
comp_super = df_super["composition :"].values.tolist()
ref_super = df_super.index.tolist()

df_icsd = pd.read_csv("/home/rhys/PhD/lattice/data/processed/icsd_cleaned.csv", index_col=0)

latc_icsd = df_icsd["latc :"].values
lata_icsd = df_icsd["lata :"].values
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

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
compare = np.vectorize(lambda x: x/sqrt2 if x > 5 else x)
lata_super = compare(lata_super)
lata_icsd = compare(lata_icsd)

families = sorted(df_super["str3 :"].unique())


num = len(families)
rows = 3
cols = int((num+rows-1)/rows)

fig = tools.make_subplots(rows=rows, cols=cols, subplot_titles=families,
                            horizontal_spacing = 0.03, vertical_spacing=0.07)

for i, ftype in enumerate(families):
    j, k = divmod(i, cols)
    
    mask_super = np.where(family_super==ftype)
    a_super = lata_super[mask_super] 
    c_super = latc_super[mask_super]
    hover_sc = hover_super[mask_super] 
    
    mask_icsd = np.where(family_icsd==ftype)
    a_icsd = lata_icsd[mask_icsd]
    c_icsd = latc_icsd[mask_icsd]
    hover_ic = hover_icsd[mask_icsd]

    trace_super = go.Scatter(x=a_super, y=c_super, 
                            mode = 'markers',
                            text=hover_sc,
                            hoverinfo='text',
                            marker=dict(
                                        color="#1F77B4",
                                        symbol="x",
                                        ),
    )   

    trace_icsd = go.Scatter(x=a_icsd, y=c_icsd, 
                            mode = 'markers',
                            text=hover_ic,
                            hoverinfo='text',
                            marker=dict(
                                        color="#FF7F0E",
                                        symbol="x",
                                        ),
    )   

    fig.append_trace(trace_super, j+1, k+1)   
    fig.append_trace(trace_icsd, j+1, k+1)   


fig['layout'].update(showlegend=False, title='Plots of a* against c for Cuprate Families', hovermode = 'closest')

plot(fig, filename='a-c-fam.html', include_plotlyjs='cdn',)
