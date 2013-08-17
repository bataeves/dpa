#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os

import functions


os.environ["QT_API"] = "pyside"

import matplotlib

matplotlib.use("Qt4Agg")

import pylab
from numpy import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec

from PySide.QtGui import *
from PySide import QtCore
from main_options import vol, rate


class Window(QWidget):
  def __init__(self, parent=None):
    super(Window, self).__init__(parent)
    self.setWindowTitle(u"График")
    self.resize(QDesktopWidget().availableGeometry().width(), QDesktopWidget().availableGeometry().height())
    self.activateWindow()
    self.init_draw()
    self.main_layout = QVBoxLayout()
    self.main_layout.addWidget(self.graph.canvas)

    self.pbar = QProgressBar(self)
    self.main_layout.addWidget(self.pbar)

    #start_button = QPushButton(u"Моделировать")
    #self.main_layout.addWidget(start_button)
    self.setLayout(self.main_layout)
    #start_button.clicked.connect(self.start)
    self.show()

  def init_draw(self):
    self.graph = plt.figure(dpi=72, facecolor=(1, 1, 1), edgecolor=(0, 0, 0))
    self.graph.canvas = FigureCanvas(self.graph)
    self.graph.canvas.setParent(self)
    #gs = gridspec.GridSpec(3, 3, width_ratios=[6,1])

    self.axis = {
      'ax3d': plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=2, projection='3d'),
      "fb": plt.subplot2grid((3, 3), (0, 2), rowspan=3),
      "rate": plt.subplot2grid((3, 3), (2, 0)),
      "vol": plt.subplot2grid((3, 3), (2, 1), projection='3d')
    };


  def draw_graph(self):
    rate = self.axis['rate']
    vol = self.axis['vol']
    fb = self.axis['fb']

    rate.scatter(self.r_rate["t"], self.r_rate["rate"], c='green')
    rate.set_xlabel('Time to maturity <t>')
    rate.set_ylabel('Rate <r(t)>')
    vol.scatter(self.r_vol["s"], self.r_vol["t"], self.r_vol["vol"], c='green')
    vol.set_xlabel('Asset price <S(t)>')
    vol.set_ylabel('Time to maturity <t>')
    vol.set_zlabel('Volatility <Vol(S, t)>')
    #draw Price
    ax = self.axis['ax3d']
    ax.scatter(self.r_P["s"], self.r_P["t"], self.r_P["p"], c='lightgray')
    #draw Free boundary
    ax.scatter(self.r_fb["fb"], self.r_fb["t"], [0] * len(self.r_fb["t"]), c='blue')
    #draw result point
    ax.scatter(self.point_solution_S, self.point_solution_t, self.point_solution_P, c='red', s=100)

    ax.set_xlabel('Asset price <S(t)>')
    ax.set_ylabel('Time to maturity <t>')
    ax.set_zlabel('Option Price <P(S, t)>')

    #draw free boundary
    fb.scatter(self.r_fb["t"], self.r_fb["fb"], c='blue')
    #draw result point
    fb.scatter(self.point_solution_t, self.point_solution_S, c='red', s=100)
    fb.set_xlabel('Time to maturity <t>')
    fb.set_ylabel('Free boundary <Fb(t)>')
    self.graph.canvas.draw()

  def clear_all_ax(self):
    for ax in self.axis:
      self.axis[ax].clear()
      if ax == 'ax3d':
        self.axis[ax].mouse_init()

  def set_par(self, parameters):
    pars = functions.Parameter.to_dict(parameters)

    self.r_grid_S, self.r_grid_t, r_P, r_fb = functions.opt_pricing(parameters, self.iter_callback)
    self.point_solution_S, self.point_solution_P = functions.find_num_solution(self.r_grid_S[-1], r_P[-1],
                                                                               pars.get("S_0"))
    self.point_solution_t = self.r_grid_t[-1]

    self.r_P = {
      "s": [],
      "t": [],
      "p": []
    }
    self.r_vol = {
      "t": [],
      "s": [],
      "vol": []
    }
    self.r_rate = {
      "t": [],
      "rate": []
    }
    self.r_fb = {
      "t": [],
      "fb": []
    }
    for i in xrange(0, pars.get("Nt") - 1):
      self.r_rate["t"].append(self.r_grid_t[i])
      self.r_rate["rate"].append(rate(self.r_grid_t[i]))

      self.r_fb["t"].append(self.r_grid_t[i])
      self.r_fb["fb"].append(r_fb[i])

      for j in xrange(1, pars.get("NS") - 1):
        self.r_P["s"].append(self.r_grid_S[i][j])
        self.r_P["t"].append(self.r_grid_t[i])
        self.r_P["p"].append(r_P[i][j])

        self.r_vol["s"].append(self.r_grid_S[i][j])
        self.r_vol["t"].append(self.r_grid_t[i])
        self.r_vol["vol"].append(vol(self.r_grid_S[i][j], self.r_grid_t[i]))

    self.clear_all_ax()
    self.draw_graph()
    return "S=%s\nP=%s" % (self.point_solution_S, self.point_solution_P)

  def iter_callback(self, state):
    current = state["i"]
    _all = state["parameters"]["Nt"] - 1
    perc = float(current) / float(_all) * 100
    self.pbar.setValue(perc)
    QApplication.processEvents()

  def SaveImage(self):
    fname, _ = QFileDialog.getSaveFileName(self)
    self.graph.savefig(fname, dpi=300)

    # def start(self):
    #     if hasattr(self, 'm'): 
    #         Thread().do_animate(self.m, self.graph, self.axis)

    # class Thread(QtCore.QThread):
    #     def do_animate(self, m, graph, axis):
    #         import time
    #         for u in m:
    #             if hasattr(self, 'point'):
    #                 self.point.remove()
    #             self.point = axis['ax3d'].scatter([u[0]], [u[1]], [u[2]], c='red', s=60)
    #             graph.canvas.draw_idle()
    #             QApplication.processEvents()
    #             time.sleep(.1)