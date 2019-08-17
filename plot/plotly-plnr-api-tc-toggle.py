import numpy as np
import pandas as pd

from plotly.offline import plot
import plotly.graph_objs as go
import colorlover as cl


df_super = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_plot.csv", index_col=0)

api_super = df_super["cu-o_a :"].values.T
plnr_super = df_super["cu-o_p :"].values.T
tc_super = df_super["tc :"].values.T
family_super = df_super["str3 :"].values.tolist()
comp_super = df_super["composition :"].values.tolist()
ref_super = df_super.index.tolist()

hover_super = []

for c_, a_, tc_, type_, ref_, comp_ in zip(api_super,plnr_super,tc_super,
                                        family_super,ref_super,comp_super):
    iter_string = ('SuperCon: {}<br>'
                    'Composition: {}<br>'
                    'Family: {}<br>'
                    'Apical: {:1.3f}<br>'
                    'In-Plane: {:1.3f} <br>'
                    'Tc: {:1.3f}'.format(ref_, comp_, type_, c_, a_, tc_))
    hover_super.append(iter_string)

hover_super = np.array(hover_super)

trace_list = []

# families = df_super["str3 :"].unique()
# families.sort()
families = df_super["layers :"].unique()

print(families)

bupu = cl.scales["8"]["div"]["RdYlGn"]
re_list = cl.interp( bupu, len(families))
colours = iter([re_list[0],re_list[2],re_list[1]])

# tab_20 = iter(['rgb(255,187,120)',
# 'rgb(255,127,14)',
# 'rgb(174,199,232)',
# 'rgb(44,160,44)',
# 'rgb(31,119,180)',
# 'rgb(255,152,150)',
# 'rgb(214,39,40)',
# 'rgb(197,176,213)',
# 'rgb(152,223,138)',
# 'rgb(148,103,189)',
# 'rgb(247,182,210)',
# 'rgb(227,119,194)',
# 'rgb(196,156,148)',
# 'rgb(140,86,75)',
# 'rgb(127,127,127)',
# 'rgb(219,219,141)',
# 'rgb(199,199,199)',
# 'rgb(188,189,34)',
# 'rgb(158,218,229)',
# 'rgb(23,190,207)',])

for fam in families:
    # mask = np.asarray(df_super["str3 :"]==fam).nonzero()
    mask = np.asarray(df_super["layers :"]==fam).nonzero()
    trace = go.Scatter3d(x=plnr_super[mask], y=api_super[mask], z=tc_super[mask],
    # trace = go.Scatter(x=plnr_super[mask], y=tc_super[mask],
                        mode = 'markers',
                        text=hover_super[mask].tolist(),
                        hoverinfo='text',
                        marker = dict(
                            # color = next(colours),
                            # color = next(tab_20),
                            opacity=0.8,
                            ),
                        name=fam,
        )

    trace_list.append(trace)
    # break

# trace = go.Scatter3d(x=[2.0], y=[1.88], z=[73],
# # trace = go.Scatter(x=plnr_super[mask], y=tc_super[mask],
#                     mode = 'markers',
#                     hoverinfo='text',
#                     name="Ba2CuO4",
#     )

# trace_list.append(trace)
    

layout_3d = go.Layout(
                    title=go.layout.Title(
                            text='Tc as a function of in-plane and apical Cu-O distances for Cuprate Families',
                            xref='paper',
                            x=0),
                    scene = dict(
                        xaxis = dict(
                            title='In-Plane Distance / Å'),
                        yaxis = dict(
                            title='Apical Distance / Å'),
                        zaxis = dict(
                            title='Tc / K'),
                        ),
    )



fig_super = go.Figure(data=trace_list, layout=layout_3d)
plot(fig_super, filename='pln-api-tc-toggle.html', include_plotlyjs='cdn',)

