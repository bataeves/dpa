from numpy import zeros, array
from scipy.sparse import eye, coo_matrix
from scipy.sparse.linalg import spsolve, factorized


class CNScheme(object):
  """docstring for CNScheme"""
  S_nodes = None #vector<vector<double>>
  S_steps = None #vector<vector<double>>
  grid_t = None #vector<double>
  change_grid = None #vector<int>
  eps = 1e-9

  #rate and volatility functions
  rate = None
  vol = None

  def __init__(self, g_grid_S, g_S_steps, g_grid_t, g_change_grid):
    super(CNScheme, self).__init__()
    self.S_nodes = array(g_grid_S)
    self.S_steps = array(g_S_steps)
    self.grid_t = array(g_grid_t)
    self.change_grid = array(g_change_grid)

  def Time_Step(self, it, P):
    i = n = 0
    dt = t = S = h_p = h_n = r = 0.0
    a = b = c = d = e = 0.0
    n = len(self.S_steps[it])

    t = self.grid_t[it]
    dt = t - self.grid_t[it - 1]

    A = self.build_matrix(self.S_steps[it], self.S_nodes[it], t, dt) #computes the matrix B =(M+dt/2* S)

    if self.change_grid[it]:
      self.build_rhs(P[it], P[it - 1], self.S_steps[it - 1], self.S_nodes[it - 1], self.S_steps[it], self.S_nodes[it],
                     t - dt, dt)
    else:
      self.build_rhs_same_grid(P[it], P[it - 1], self.S_steps[it - 1], self.S_nodes[it - 1], self.S_steps[it],
                               self.S_nodes[it], t - dt, dt)

    P[it] = spsolve(A.tocsr(), P[it])

  def build_matrix(self, steps, nodes, t, dt):
    A_row = []
    A_col = []
    A_data = []
    n = len(steps)
    i = 0
    S = h_p = h_n = 0.
    a = b = c = d = 0. # auxiliary variables

    r = self.rate(t)
    e = 0.25 * dt
    h_n = steps[0]

    A_row += [0, 0]
    A_col += [0, 1]
    A_data += [e * r * h_n + h_n / 3, h_n / 6]
    for i in xrange(1, n):
      h_p = h_n
      S = nodes[i]
      h_n = steps[i]
      a = pow(S * self.vol(t, S), 2)
      b = a / h_p
      c = a / h_n
      d = r * S

      A_row += [i, i]
      A_col += [i, i - 1]
      A_data += [e * (b + c + r * (h_p + h_n)) + (h_p + h_n) / 3, e * (-b + d) + h_p / 6]
      if i < n - 1:
        A_row += [i]
        A_col += [i + 1]
        A_data += [e * (-c - d) + h_n / 6]
    return coo_matrix((A_data, (A_row, A_col)), shape=(n, n))

  def build_rhs_same_grid(self, u, u_p, steps_p, nodes_p, steps, nodes, t, dt):
    c = d = v_l = v_r = u_l = u_r = x_l = x_r = 0.
    r = self.rate(t)
    e = 0.5 * dt

    u[:] = 0.
    x_l = 0.
    u_l = u_p[0]
    v_l = self.vol(t, x_l)
    v_l *= x_l
    v_l *= 0.5 * v_l
    for i in xrange(0, len(steps_p) - 1):
      x_r = nodes_p[i + 1]
      v_r = self.vol(t, x_r)
      v_r *= x_r
      v_r *= 0.5 * v_r
      u_r = u_p[i + 1]
      c = u_r - u_l
      d = c / steps_p[i]
      u[i] += steps_p[i] / 6. * (2 * u_l + u_r) + e * (
      d * v_l + (c * (2 * x_l + x_r) - (2 * u_l + u_r) * steps_p[i]) * r / 6)
      u[i + 1] += steps_p[i] / 6. * (u_l + 2 * u_r) + e * (
      -d * v_r + (c * (2 * x_r + x_l) - (2 * u_r + u_l) * steps_p[i]) * r / 6)
      x_l = x_r
      u_l = u_r
      v_l = v_r
    i = len(steps_p) - 1
    c = -u_l
    d = c / steps_p[i]
    u[i] += steps[i] / 3. * (u_p[i]) + e * (d * v_l + (c * (2 * x_l + x_r) - 2 * u_l * steps_p[i]) * r / 6)
