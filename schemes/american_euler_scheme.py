import logging
from numpy import zeros
from american_free_bondary import free_boundary


class AmericanEulerScheme(object):
  """docstring for AmericanEulerScheme"""

  eps = 1e-9

  def __init__(self, option, grid):
    super(AmericanEulerScheme, self).__init__()
    self.option = option
    self.grid = grid
    self.asset = self.option.asset
    self.iK = 0
    while self.option.payoff(self.grid.series["S"][self.iK]) > 0:
      self.iK += 1

  def step(self, it, P, free_bdry_guess_p):
    n = len(self.grid.values[it]) - 1

    y = zeros(n, dtype=float)
    rhs = zeros(n, dtype=float)
    ob = zeros(n, dtype=float)

    #construct A
    A = self.asset.construct_matrix(self.grid, it)

    logging.info("build_rhs at it=%d" % it)
    logging.info("size of rhs =%d , size of previous vector =%d" % (len(P[it]), len(P[it - 1])))
    self.build_rhs(rhs, P[it - 1], self.grid.values[it], self.grid.series["S"], self.grid.values[it - 1],
                   self.grid.series["S"])

    for k in xrange(0, self.iK):
      ob[k] = self.option.payoff(self.grid.series["S"][k])

    free_bdry_guess = 0
    while self.grid.series["S"][free_bdry_guess] < self.grid.series["S"][free_bdry_guess_p]:
      free_bdry_guess += 1
    return free_boundary(A, P[it], y, rhs, ob, free_bdry_guess, dtype=float)

  def build_rhs(self, u, u_p, steps, nodes, steps_p=None, nodes_p=None):
    """
    KN<double> &u, const KN<double> &u_p,
    const  vector<double> & steps_p, const  vector<double> & nodes_p,
    const  vector<double> & steps, const  vector<double> & nodes
    """
    lsteps = len(steps) - 1
    if steps_p is None and nodes_p is None:
      i = 0
      for i in xrange(0, lsteps - 1):
        u[i] += steps[i] / 6. * (2 * u_p[i] + u_p[i + 1])
        u[i + 1] += steps[i] / 6. * (u_p[i] + 2 * u_p[i + 1])
      u[i + 1] += steps[i] / 3. * u_p[i]
    else:
      lsteps_p = len(steps_p) - 1
      x_l = 0.0
      i = j = 0
      u_pl = u_p[0]
      while i < lsteps:
        logging.info("i=%d j=%d" % (i, j))
        if nodes_p[j + 1] <= nodes[i + 1] + self.eps:
          phi_l = 0.0
          psi_l = 1.0
          while nodes_p[j + 1] <= nodes[i + 1] + self.eps:
            u_pr = u_p[j + 1] if j < lsteps_p - 1 else 0.0
            x_r = nodes_p[j + 1]
            h = x_r - x_l
            phi_r = (nodes_p[j + 1] - nodes[i]) / steps[i]
            psi_r = 1. - phi_r
            if i < lsteps - 1:
              u[i + 1] += h * (2. * (phi_l * u_pl + phi_r * u_pr) + (phi_l * u_pr + phi_r * u_pl)) / 6.
            u[i] += h * (2. * (psi_l * u_pl + psi_r * u_pr) + (psi_l * u_pr + psi_r * u_pl)) / 6.

            x_l, u_pl, phi_l, psi_l = x_r, u_pr, phi_r, psi_r

            j += 1
            if j == lsteps_p:
              break

          if nodes[i + 1] > nodes_p[j] + self.eps:
            x_r = nodes[i + 1]
            h = x_r - x_l
            if j < lsteps_p - 1:
              u_pr = u_p[j] + (nodes[i + 1] - nodes_p[j]) / steps_p[j] * (u_p[j + 1] - u_p[j])
            else:
              u_pr = (1. - (nodes[i + 1] - nodes_p[j]) / steps_p[j]) * u_p[j]

            phi_r = 1.0
            psi_r = 0.0
            if i < lsteps - 1:
              u[i + 1] += h * (2. * (phi_l * u_pl + phi_r * u_pr) + (phi_l * u_pr + phi_r * u_pl) ) / 6.
            u[i] += h * (2. * (psi_l * u_pl + psi_r * u_pr) + (psi_l * u_pr + psi_r * u_pl) ) / 6.
            u_pl, x_l = u_pr, x_r
          i += 1
        else:
          while nodes[i + 1] <= nodes_p[j + 1] + self.eps:
            x_r = nodes[i + 1]
            h = x_r - x_l
            if j < lsteps_p - 1:
              u_pr = u_p[j] + (nodes[i + 1] - nodes_p[j]) / steps_p[j] * (u_p[j + 1] - u_p[j])
            else:
              u_pr = u_p[j] * (1. - (nodes[i + 1] - nodes_p[j]) / steps_p[j])
            if i < lsteps - 1:
              u[i + 1] += h * (2. * u_pr + u_pl) / 6.
            u[i] += h * (2. * u_pl + u_pr) / 6.
            x_l, u_pl = x_r, u_pr
            i += 1
            if i == lsteps:
              break
          if nodes[i] > nodes_p[j + 1] - self.eps:
            j += 1
