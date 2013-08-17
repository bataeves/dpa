__author__ = 'bataev'
from grids.uniform_grid import UniformGrid
from models.american_option_model import AmericanOptionModel
from models.asset_model import AssetModel
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


grid = UniformGrid(series=[
    ("t", 0.0, 2.0, 200),
    ("S", 0.0, 200.0, 200),
  ])
asset = AssetModel(S_0=88, volatility=0.2, rate=0.09)
option = AmericanOptionModel(asset=asset, K=100, T=2.0)
fb, P = option.generate(grid)

fig = plt.figure()

# option market price
ax3d = fig.add_subplot(121, projection="3d")
axfb = fig.add_subplot(122)

ax3d.set_xlabel('Asset price <S(t)>')
ax3d.set_ylabel('Time to maturity <t>')
ax3d.set_zlabel('Option Price <P(S, t)>')

xs = np.tile(grid.series["S"][:-1], P.shape[0])
ys = np.repeat(grid.series["t"], P.shape[1])
ax3d.scatter(xs, ys, P.reshape(P.shape[0] * P.shape[1]))

# free boundary
axfb.plot(grid.series["t"], fb)