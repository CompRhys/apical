import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error as mse

from plotly.offline import plot
import plotly.graph_objs as go

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RationalQuadratic as RQ, RBF, DotProduct as Dot, ConstantKernel as C

import pickle

df = pd.read_csv("/home/rhys/PhD/lattice/data/processed/super_plot.csv", index_col=0)

mask =(df["layers :"]=="One")
df = df.loc[mask]

X = df[["cu-o_p :", "cu-o_a :"]].values
y = df["tc :"].values
comp = df["composition :"].values.tolist()
ref = df.index.tolist()

# # train on all structures with a one-hot label
# X = df[["cu-o_p :", "cu-o_a :",]].values
# struc = pd.get_dummies(df["layers :"]).values
# X = np.hstack((X,struc))
# y = df["tc :"].values

hover = []

for idx, elem, tc in zip(ref, comp, y):
    iter_string = ('SuperCon: {}<br>'
                    'Composition: {}<br>'
                    'Tc: {:1.3f}'.format(idx, elem, tc))
    hover.append(iter_string)

hover = np.array(hover)

y = np.vstack((y, hover)).T

print(X.shape, y.shape)
# Split data into training and test sets (50 is good)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

train_hover = y_train[:,1].astype(str) 
test_hover = y_test[:,1].astype(str)

y_train = y_train[:,0].astype(float) 
y_test = y_test[:,0].astype(float)

# Scale the input features to improve
scaler = StandardScaler().fit(X_train)
X_train = scaler.transform(X_train) 
X_test = scaler.transform(X_test) 

model_file = 'fitted-gp-one.pickle'

if os.path.isfile(model_file):
    f = open(model_file, 'rb')
    model = pickle.load(f) 
else:
    # # Instantiate a Gaussian Process model
    # kernel = C() * Dot() * (RBF(length_scale_bounds=(1e-1, 1e2)) + RQ(alpha_bounds=(1e-2,1), length_scale_bounds=(1e-5, 1e3)))
    # kernel = ( C() * Dot () * Dot () * Dot () + C() * Dot () * Dot () + C() * Dot () + C() )
    # kernel = RQ(alpha_bounds=(1e-2,1), length_scale_bounds=(1e-5, 1e3)) + RBF()
    # kernel = RBF() + RBF() 
    kernel = RBF() + RQ() 
    # kernel = RQ() + RQ()
    model = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=100)

    # Fit to data using Maximum Likelihood Estimation of the parameters
    model.fit(X_train, y_train)
    print(model.kernel_)

    f = open(model_file, 'wb')
    pickle.dump(model, f)


# Make the prediction on the meshed x-axis (ask for MSE as well)
y_pred, std_pred = model.predict(X_test, return_std=True)



num = 50
# x_grid = np.linspace(1.75, 2, num)
x_grid = np.linspace(1.85, 2, num)
y_grid = np.linspace(2.2, 3.0, num)

xx, yy = np.meshgrid(x_grid,y_grid)
points = np.vstack([xx.reshape(-1), yy.reshape(-1)]).T

# labels = np.zeros((points.shape[0], 3))
# labels[:,0] = 1
# points = np.hstack((points, labels ))

points = scaler.transform(points) 


trace_list = []

# predict for test set
X_test = scaler.inverse_transform(X_test)

r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mse(y_test, y_pred))
print("The R2 Score is {}".format(r2))
print("The RMSE is {} K".format(rmse))

trace = go.Scatter3d(x=X_test[:, 0], y=X_test[:, 1], z=y_test.ravel(),
                    mode = 'markers',
                    text=test_hover.tolist(),
                    hoverinfo='text',
                    marker = dict(
                        size = 5,
                        ),
                    name="Test",
        )

trace_list.append(trace)

# plot training set
X_train = scaler.inverse_transform(X_train)

trace = go.Scatter3d(x=X_train[:, 0], y=X_train[:, 1], z=y_train.ravel(),
                    mode = 'markers',
                    text=train_hover.tolist(),
                    hoverinfo='text',
                    marker = dict(
                        size = 5,
                        ),
                    name="Train",
        )

trace_list.append(trace)


# # predict for judiths point
# x = np.array([1.88, 2.43, 1, 0, 0]).reshape(1,-1)
x = np.array([1.88, 2.43]).reshape(1,-1)
x = scaler.transform(x) 
y_pred, sigma = model.predict(x, return_std=True)
x = scaler.inverse_transform(x)

print("Predicted Tc for VAN point {} +/- {}".format(y_pred[0], sigma[0]))

trace = go.Scatter3d(x=x[:, 0], y=x[:, 1], z=y_pred.ravel(),
                    mode = 'markers',
                    marker = dict(
                        size = 5,
                        opacity=0.8
                        ),
                    name="VAN - LCO",
        )


trace_list.append(trace)


# plot gp surface
surf_pred, sigma = model.predict(points, return_std=True)
surf_pred = np.reshape(surf_pred,(num, num))
sigma = np.reshape(sigma,(num, num))

trace = go.Surface(x=xx, y=yy, z=surf_pred, 
                    # showscale=False,
                    colorbar = dict(
                        xanchor = "right"
                    ),   
                    opacity=0.5,
                    surfacecolor = sigma
                    )

trace_list.append(trace)

layout_3d = go.Layout(
                    title=go.layout.Title(
                            text='Gaussian Process model for one layer Cuprates',
                            xref='paper',
                            x=0),
                    scene = dict(
                        xaxis = dict(
                            title='In-Plane Distance / Å'),
                            showgrid=False,
                            zeroline=False,
                            showline=False,
                        yaxis = dict(
                            title='Apical Distance / Å'),
                        zaxis = dict(
                            title='Tc / K',
                            range = [20,120],
                            ),
                            
                        ),
    )


fig_super = go.Figure(data=trace_list, layout=layout_3d)
plot(fig_super, filename='one-layer-gp.html', include_plotlyjs='cdn',)

plt.show()
