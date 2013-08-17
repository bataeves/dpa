#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PySide.QtCore import *
from PySide.QtGui import *

import parameters
import graph


class Main(QMainWindow):
  def __init__(self):
    super(Main, self).__init__()
    self.initUI()

  def initUI(self):
    self.pform = parameters.Form()
    self.pform.g = graph.Window()

    splitparam = QSplitter(Qt.Vertical)
    splitter = QSplitter()
    splitparam.addWidget(self.pform)
    #splitparam.addWidget(self.pform.g.ep)
    splitter.addWidget(splitparam)
    splitter.addWidget(self.pform.g)
    # splitter.setStretchFactor(0, 1)
    # splitter.setStretchFactor(1, 3)

    self.setCentralWidget(splitter)
    menubar = self.menuBar()
    parmenu = menubar.addMenu(u'Параметры')
    openfile = QAction(u'Загрузить значения', self)
    parmenu.addAction(openfile)
    openfile.triggered.connect(self.pform.OpenDialog)
    savefile = QAction(u'Сохранить значения', self.pform)
    parmenu.addAction(savefile)
    savefile.triggered.connect(self.pform.SaveDialog)
    graphmenu = menubar.addMenu(u'Графика')
    saveimg = QAction(u'Сохранить изображение', self.pform.g)
    graphmenu.addAction(saveimg)
    saveimg.triggered.connect(self.pform.g.SaveImage)

    self.setGeometry(QDesktopWidget().availableGeometry())
    self.show()


if __name__ == '__main__':
  # Create the Qt Application
  app = QApplication(sys.argv)
  # Create and show the form
  main = Main()
  # Run the main Qt loop
  sys.exit(app.exec_())
