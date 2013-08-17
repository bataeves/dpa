from collections import OrderedDict
from base_grid import BaseGrid
import numpy as np


class UniformGrid(BaseGrid):
  """docstring for UniformGrid"""

  def __init__(self, **kwargs):
    super(UniformGrid, self).__init__()
    self.series = OrderedDict()
    self.dtype = kwargs.get("dtype", float)
    shape = []
    for serie, start, end, cnt in kwargs.get("series"):
      self.series[serie] = np.linspace(start, end, cnt)
      # self.series[serie] = np.zeros(cnt, dtype=self.dtype)
      # part = (end - start) / (cnt - 1)
      # for i in xrange(0, cnt):
      #   self.series[serie][i] = start + part * i
      shape.append(cnt)

    self.values = np.zeros(tuple(shape))

  def gi(self, **kwargs):
    val = self.values
    for serie in self.series.iterkeys():
      val = val[kwargs.get(serie, 0)]
    return val

  def si(self, value, **kwargs):
    prev_val = val = self.values
    prev_index = 0
    for serie in self.series.iterkeys():
      prev_val = val
      prev_index = kwargs.get(serie, 0)
      val = val[kwargs.get(serie, 0)]
    prev_val[prev_index] = value
    return
