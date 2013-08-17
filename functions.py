#!/usr/bin/python
# -*- coding: utf-8 -*-

from numpy import *
from main_options import american_calculation


class Parameter(object):
  def __init__(self, name, def_val, label=None, values=None):
    self.name = name
    self.label = label or self.name
    self.val = def_val
    self.values = values

  @classmethod
  def to_dict(cls, par_array):
    return {par.name: par.val for par in par_array}


# def opt_pricing(parameters, callback_func):
#   pars = Parameter.to_dict(parameters)
#   Nt = pars.get("Nt")
#   NS = pars.get("NS")
#   K = pars.get("K")
#   S_max = pars.get("Smax")
#   T = pars.get("T")
#   vol = pars.get("V")
#   rate = pars.get("r")
#   otype = pars.get("otype")
#   r_grid_S = []
#   r_grid_t = []
#   r_P = []
#   r_fb = []
#   for i, grid_S, grid_t, P, fb in american_calculation(Nt, NS, K, S_max, T, vol, rate, otype):
#     if callback_func:
#       callback_func({"i": i, "grid_S": grid_S, "grid_t": grid_t, "P": P, "fb": fb, "parameters": pars})
#     r_grid_S.append(grid_S)
#     r_grid_t.append(grid_t)
#     r_P.append(P)
#     r_fb.append(fb)
#   return r_grid_S, r_grid_t, r_P, r_fb

def opt_pricing(parameters, callback_func):
  pars = Parameter.to_dict(parameters)
  Nt = pars.get("Nt")
  NS = pars.get("NS")
  K = pars.get("K")
  S_max = pars.get("Smax")
  T = pars.get("T")
  vol = pars.get("V")
  rate = pars.get("r")
  otype = pars.get("otype")
  r_grid_S = []
  r_grid_t = []
  r_P = []
  r_fb = []
  for i, grid_S, grid_t, P, fb in american_calculation(Nt, NS, K, S_max, T, vol, rate, otype):
    if callback_func:
      callback_func({"i": i, "grid_S": grid_S, "grid_t": grid_t, "P": P, "fb": fb, "parameters": pars})
    r_grid_S.append(grid_S)
    r_grid_t.append(grid_t)
    r_P.append(P)
    r_fb.append(fb)
  return r_grid_S, r_grid_t, r_P, r_fb


def find_num_solution(grid_S, P, S_0):
  if not S_0:
    return None
  close_val = grid_S[grid_S >= S_0].min() or grid_S[grid_S <= S_0].max()
  ind = where(grid_S == close_val)[0][0]
  return close_val, P[ind]