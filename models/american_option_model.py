import numpy as np

from option_model import OptionModel
from schemes.american_euler_scheme import AmericanEulerScheme


class AmericanOptionModel(OptionModel):
  """docstring for AmericanOptionModel"""

  def __init__(self, **kwargs):
    super(AmericanOptionModel, self).__init__(**kwargs)

  def payoff(self, S):
    pass

  def generate(self, grid):
    Nt = len(grid.series["t"])
    NS = len(grid.series["S"])
    P = np.zeros((Nt, NS - 1), dtype=float)

    #construct grid
    for i in xrange(0, Nt):
      for j in xrange(0, NS - 1):
        grid.values[i][j] = grid.series["S"][j + 1] - grid.series["S"][j]

    scheme = AmericanEulerScheme(option=self, grid=grid)
    #construct cauchy data
    iS = 0
    for iS in xrange(0, NS - 1):
      P[0][iS] = self.payoff(grid.series["S"][iS])
      if P[0][iS] <= 0.:
        break
    #free boundary vector
    fb = [self.K]
    free_bdry = iS
    for i in xrange(1, Nt):
      #find free boundary point in time
      ts_result = scheme.step(i, P, free_bdry)
      fb.append(grid.series["S"][ts_result])
    return fb, P