import numpy as np
import pandas as pd

from plotly.offline import plot
import plotly.graph_objs as go
import colorlover as cl


df_super = pd.read_csv("/home/reag2/PhD/first-year/apical/processed-data/super_apical.csv", index_col=0)

api_super = df_super["cu-o_a :"].values.T
plnr_super = df_super["lata :"].values.T
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
                    'c: {:1.3f}<br>'
                    'a: {:1.3f} <br>'
                    'Tc: {:1.3f}'.format(ref_, comp_, type_, c_, a_, tc_))
    hover_super.append(iter_string)

hover_super = np.array(hover_super)

trace_list = []

# families = df_super["str3 :"].unique()
# families = df_super["layers :"].unique()
families = ["One", "Two", "Three"]
# families.sort()
print(families)

sqrt2 = np.sqrt(2)
ortho = lambda x: x/sqrt2 if x > 5 else x
comparable = np.vectorize(ortho)

plnr_super = comparable(plnr_super)

bupu = cl.scales["8"]["div"]["RdYlGn"]
re_list = cl.interp( bupu, len(families))
colours = iter([re_list[0],re_list[2],re_list[1]])

print(colours)

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
    # trace = go.Scatter(x=api_super[mask], y=tc_super[mask],
                        mode = 'markers',
                        text=hover_super[mask].tolist(),
                        hoverinfo='text',
                        marker = dict(
                            # color = next(colours),
                            ),
                        name=fam,
        )

    trace_list.append(trace)
    # break

layout = go.Layout(
                    title=go.layout.Title(
                            text='Tc as a function a* for Cuprate Families',
                            xref='paper',
                            x=0
                        ),
                    scene = dict(
                        xaxis = dict(
                            title='a*',
                            ),
                        yaxis = dict(
                            title='c',
                            ),
                        zaxis = dict(
                            title='Tc',
                            ),
                        ),
                    hovermode = 'closest',
    )



fig_super = go.Figure(data=trace_list, layout=layout)
plot(fig_super, filename='a-tc-toggle.html', include_plotlyjs='cdn',)




