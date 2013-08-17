import argparse
import numpy as np
from american_euler_scheme import AmericanEulerScheme
from cn_scheme import CNScheme

#Matrice

__vol = None
__rate = None


def rate(t):
  return eval(__rate)


def vol(S, t):
  # vType == 1:
  #   return 0.1 + 0.1 * ( 1 if 100*pow(t-0.5,2) + pow(S-25,2)/100 < 2.0 else 0)
  return eval(__vol)


def european_calculation(Nt, NS, K, S_max, T, func_vol, func_rate, otype="put"):
  global __vol
  global __rate
  __vol = compile(func_vol, "<string>", "eval")
  __rate = compile(func_rate, "<string>", "eval")

  #initialize grids
  grid_t = np.zeros(Nt, dtype=float)
  change_grid = np.zeros(Nt, dtype=int)
  grid_S = np.zeros((Nt, NS), dtype=float)
  S_steps = np.zeros((Nt, NS - 1), dtype=float)
  P = np.zeros((Nt, NS - 1), dtype=float)
  non_unif_grid_t = np.zeros(Nt, dtype=float)
  non_unif_grid_S = np.zeros((Nt, NS), dtype=float)
  non_unif_S_steps = np.zeros((Nt, NS - 1), dtype=float)

  #construction of a simple uniform grid in time and S
  #construct grid
  for i in xrange(0, Nt):
    grid_t[i] = (T * i) / (Nt - 1)
    for j in xrange(0, NS):
      grid_S[i][j] = (S_max * j) / (NS - 1)
    for j in xrange(0, NS - 1):
      S_steps[i][j] = grid_S[i][j + 1] - grid_S[i][j]

  #the time grid is refined near t=0 
  power = 4.
  for i in xrange(1, Nt - 1):
    non_unif_grid_t[i] = T * pow(grid_t[i + 1] / T, power)
    #the S grid is refined near t=0
  power_S = 2.
  for i in xrange(0, Nt):
    for j in xrange(0, len(grid_S[i]) / 2):
      non_unif_grid_S[i][j] = K - K * pow(K - grid_S[i][j], power_S) / pow(K, power_S)
    for j in xrange(len(grid_S[i]) / 2, NS):
      non_unif_grid_S[i][j] = K + K * pow(grid_S[i][j] - K, power_S) / pow(K, power_S)
    for j in xrange(0, NS - 1):
      non_unif_S_steps[i][j] = non_unif_grid_S[i][j + 1] - non_unif_grid_S[i][j]

  # the numerical solutions of the Black-Scholes equation with two different boundary condition at S=S_max
  iS = 0
  #the Cauchy data
  # Put
  if otype == "put":
    while non_unif_grid_S[0][iS] < K:
      P[0][iS] = K - non_unif_grid_S[0][iS]
      iS += 1
    # Call
  if otype == "call":
    while non_unif_grid_S[0][iS] > K:
      P[0][iS] = non_unif_grid_S[0][iS] - K
      iS += 1

  #construction of a Crank-Nicolson scheme
  non_unif_scheme = CNScheme(non_unif_grid_S, non_unif_S_steps, non_unif_grid_t, change_grid)
  non_unif_scheme.rate = rate
  non_unif_scheme.vol = vol
  for i in xrange(1, Nt):
    non_unif_scheme.Time_Step(i, P)
    yield i, grid_S[i], grid_t[i], P[i], 0
  return


def american_calculation(Nt, NS, K, S_max, T, func_vol, func_rate, otype="put"):
  global __vol
  global __rate
  __vol = compile(func_vol, "<string>", "eval")
  __rate = compile(func_rate, "<string>", "eval")

  #initialize grids
  grid_t = np.zeros(Nt, dtype=float)
  change_grid = np.zeros(Nt, dtype=int)
  grid_S = np.zeros((Nt, NS), dtype=float)
  S_steps = np.zeros((Nt, NS - 1), dtype=float)
  P = np.zeros((Nt, NS - 1), dtype=float)

  #construct grid
  for i in xrange(0, Nt):
    grid_t[i] = (T * i) / (Nt - 1)
    for j in xrange(0, NS):
      grid_S[i][j] = (S_max * j) / (NS - 1)
    for j in xrange(0, NS - 1):
      S_steps[i][j] = grid_S[i][j + 1] - grid_S[i][j]

  scheme = AmericanEulerScheme(grid_S, S_steps, grid_t, change_grid)
  scheme.rate = rate
  scheme.vol = vol
  #construct cauchy data
  iS = 0
  # Put
  if otype == "put":
    while grid_S[0][iS] < K:
      P[0][iS] = K - grid_S[0][iS]
      iS += 1
    # Call
  if otype == "call":
    while grid_S[0][iS] > K:
      P[0][iS] = grid_S[0][iS] - K
      iS += 1

  #free boundary vector
  fb = [K]
  free_bdry = iS
  for i in xrange(1, Nt):
    #find free boundary point in time
    ts_result = scheme.time_step(i, P, K, free_bdry)
    fb.append(grid_S[i][ts_result])
    yield i, grid_S[i], grid_t[i], P[i], fb[i]
  return


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Numerical solution to American option pricing problem.')

  parser.add_argument('-Nt', metavar="Nt", action='store', type=int, default=101,
                      help="t-grid interval count")
  parser.add_argument('-NS', metavar="NS", action='store', type=int, default=51,
                      help="S-grid interval count")
  parser.add_argument('-K', metavar="K", action='store', type=float, default=100.0,
                      help="K")
  parser.add_argument('-S0', metavar="S_0", action='store', type=float, default=88,
                      help="S initial")
  parser.add_argument('-Smax', metavar="Smax", action='store', type=float, default=-1,
                      help="S up bounding")
  parser.add_argument('-T', metavar="T", action='store', type=float, default=2.,
                      help="Time to maturity")

  parser.add_argument('-r', metavar="r", action='store', default="0.09",
                      help="risk-free rate function")
  parser.add_argument('-V', metavar="V", action='store', default="0.2",
                      help="volatility function")
  parser.add_argument('-otype', metavar="option type", action='store', default="put",
                      help="type of option to calculate")

  parser.add_argument('-sol', metavar="sol", action='store', default="output/solution",
                      help="filepath to main solution")
  parser.add_argument('-fb', metavar="fb", action='store', default="output/fb",
                      help="filepath to free boundary solution")
  parser.add_argument('-vol', metavar="vol", action='store', default="output/vol",
                      help="filepath to volatility function")
  parser.add_argument('-rate', metavar="rate", action='store', default="output/rate",
                      help="filepath to rate function")
  args = parser.parse_args()

  #fill args
  sol_fn = args.sol
  fb_fn = args.fb
  vol_fn = args.vol
  rate_fn = args.rate
  Nt = args.Nt
  NS = args.NS
  K = args.K
  S_max = args.Smax if args.Smax > 0 else K * 1.3
  T = args.T
  otype = args.otype

  with open(sol_fn, "w") as outf:
    with open(fb_fn, "w") as outfb:
      with open(vol_fn, "w") as outv:
        with open(rate_fn, "w") as outr:
          for i, grid_S, grid_t, P, fb in american_calculation(Nt, NS, K, S_max, T, args.V, args.r, otype):
            #print "%d iteration" % i
            #output results
            if i in [1, Nt - 1]:
              print i
              print "S \t\t\t time \t\t Price"
            for j in xrange(1, NS - 1):
              outf.write("%f\t%f\t%f\n" % (grid_S[j], grid_t, P[j]))
              if i in [0, Nt - 1]:
                print "%f\t%f\t%f" % (grid_S[j], grid_t, P[j])
            outf.write("\n")
            outfb.write("%f\t%f\n" % (fb, grid_t))

            _t = T * Nt / i
            for j in xrange(1, NS - 1):
              _s = S_max / NS * j
              outv.write("%f\t%f\t%f\n" % (_s, _t, vol(_s, _t)))
            outv.write("\n")

            _t = T * Nt / i
            outr.write("%f\t%f\n" % (_t, rate(_t)))
