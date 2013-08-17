__author__ = 'bataev'
from grids.uniform_grid import UniformGrid
from models.american_option_model import AmericanOptionModel
from models.asset_model import AssetModel
import matplotlib.pyplot as plt

if __name__ == "__main__":
  grid = UniformGrid(series=[
    ("t", 0.0, 2.0, 50),
    ("S", 0.0, 200.0, 50),
  ])
  asset = AssetModel(S_0=88, volatility=0.2, rate=0.09)
  option = AmericanOptionModel(asset=asset, K=100, T=10)
  fb, P = option.generate(grid)
  plt.plot(fb)
  plt.plot(P)
