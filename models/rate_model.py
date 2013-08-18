from base_model import BaseModel
from scipy.sparse import coo_matrix
import pyprocess as pp


class RateModel(BaseModel):
  """docstring for RateModel"""

  def __init__(self, **kwargs):
    super(RateModel, self).__init__()
    self._volatility = kwargs.get("volatility")
    self._rate = kwargs.get("rate")

    self.C_0 = kwargs.get("C_0")
    self.R_0 = kwargs.get("R_0")

  def volatility(self, **kwargs):
    if callable(self._volatility):
      return self._volatility(**kwargs)
    return self._volatility

  def rate(self, **kwargs):
    if callable(self._rate):
      return self._rate(**kwargs)
    return self._rate

  def construct_matrix(self, grid, it):
    n = len(grid.values[it]) - 1
    A_row = []
    A_col = []
    A_data = []
    t = grid.series["t"][it]
    dt = t - grid.series["t"][it - 1]
    r = self.rate(t=t)
    e = 0.5 * dt
    h_n = grid.values[it][0]

    A_row += [0, 0]
    A_col += [0, 1]
    A_data += [e * r * h_n + h_n / 3, h_n / 6]

    for i in xrange(1, n - 1):
      h_p = h_n
      S = grid.series["S"][i]
      h_n = grid.values[it][i]
      a = pow(S * self.volatility(t=t, S=S), 2)
      b = a / h_p
      c = a / h_n
      d = r * S

      A_row += [i, i, i]
      A_col += [i, i - 1, i + 1]
      A_data += [
        e * (b + c + r * (h_p + h_n)) + (h_p + h_n) / 3.,
        e * (-b + d) + h_p / 6.,
        e * (-c - d) + h_n / 6.
      ]

    i += 1
    h_p = h_n
    S = grid.series["S"][i]
    h_n = grid.values[it][i]
    a = pow(S * self.volatility(t=t, S=S), 2)
    b = a / h_p
    c = a / h_n
    d = r * S

    A_row += [i, i]
    A_col += [i, i - 1]
    A_data += [e * (b + c + r * (h_p + h_n)) + (h_p + h_n) / 3., e * (-b + d) + h_p / 6.]

    return coo_matrix((A_data, (A_row, A_col)), shape=(n, n)).todok()

  def generate(self, serie, N=0.001):
    # customInitial = {"startTime": 0, "startPosition": 0}
    #get the mean and poisiton at t=10.
    #As this diffusion is untractable, we use MC methods. You can specify the accuracy in the library.
    return pp.Custom_diffusion({"a": self.drift, "b": self.diffusion}, startTime=serie[0],
                               startPosition=self.C_0).sample_path(serie[1:], N=N)

  # Lets create a custom diffusion. We specify the drift and diffusion functions in the SDE:
  # The functions must have time and space parameters, though they don't need to depend on them.
  def drift(self, x, t):
    return 0

    #the diffusion function must be non-negative in it's domain.
  def diffusion(self, x, t):
    return (-x**2 / self.C_0) * self.volatility(S=x, t=t)
