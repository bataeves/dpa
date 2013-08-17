#!/usr/bin/python
# -*- coding: utf-8 -*-
from math import *
import pickle

from PySide.QtGui import *

from functions import Parameter


class Form(QWidget):
  parameters = [
    Parameter('otype', "put", "Option type:", values=["put", "call"]),
    Parameter('K', 100.0, "Strike <K>:"),
    Parameter('T', 1.0, "Time to maturity <T>:"),
    Parameter('r', "0.04", "Risk free <r(t)>:"),
    Parameter('V', "0.2", "Volatility <Vol(S, t)>:"),
    Parameter('S_0', 100.0, "Initial asset price <S(0)>:"),

    Parameter('Nt', 50, "Time interval <Nt>:"),
    Parameter('NS', 50, "Price interval <NS>:"),
    Parameter('Smax', 200.0, "Max price <Smax>:"),
  ]

  def __init__(self, parent=None):
    super(Form, self).__init__(parent)
    self.setWindowTitle(u"Параметры")
    # Create layout and add widgets
    main_layout = QVBoxLayout()

    self.pedit = {}
    for p in self.parameters:
      hl = QHBoxLayout()
      hl.addWidget(QLabel(p.label))

      vals = p.val
      if not type(vals) is list:
        vals = [vals]
      self.pedit[p.name] = {}
      for key, val in enumerate(vals):
        # if p.values:
        #   self.pedit[p.name][key] = QComboBox()
        #   self.pedit[p.name][key].addItems(p.values)
        # else:
        self.pedit[p.name][key] = QLineEdit(str(val))
        hl.addWidget(self.pedit[p.name][key])

      main_layout.addLayout(hl)
    main_layout.addWidget(QLabel("Output:"))
    self.output_field = QTextEdit()
    main_layout.addWidget(self.output_field)

    start_button = QPushButton(u"Считать")
    main_layout.addWidget(start_button)
    start_button.clicked.connect(self.start)

    self.setLayout(main_layout)
    self.resize(200, QDesktopWidget().availableGeometry().height())
    self.activateWindow()

  def start(self):
    for p in self.parameters:
      p.val = type(p.val)(self.pedit[p.name][0].text())

    self.output_field.setText(self.g.set_par(parameters=self.parameters))
    self.g.show()

  def SaveDialog(self):
    fname, _ = QFileDialog.getSaveFileName(self)
    with open(fname, 'w') as f:
      pickle.dump(self.parameters, f)
      #f.write(pickle.encode(self.parameters))

  def OpenDialog(self):
    fname, _ = QFileDialog.getOpenFileName(self)
    with open(fname, 'r') as f:
      #self.parameters = jsonpickle.decode(f.read())
      self.parameters = pickle.load(f)
    self.refresh()

  def refresh(self):
    for p in self.parameters:
      vals = p.val
      if not type(vals) is list:
        vals = [vals]
      for key, val in enumerate(vals):
        self.pedit[p.name][key].setText(str(val))
