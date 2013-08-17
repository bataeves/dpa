import urllib2
from dateutil.rrule import DAILY, rrule
from datetime import datetime
from zipfile import ZipFile
from os.path import exists, join
from os import makedirs
from StringIO import StringIO
import logging

import pandas as pd


def download(years, outdir="."):
  if not exists(outdir):
    makedirs(outdir)
  for year in years or []:
    year_url = "ftp://ftp.rts.ru/pub/info/stats/history/F/%s" % year
    for d in rrule(DAILY, dtstart=datetime(year=year, month=1, day=1), until=datetime(year=year + 1, month=1, day=1)):
      req = urllib2.Request("%s/f%s.ZIP" % (year_url, d.strftime("%y%m%d")))
      try:
        response = urllib2.urlopen(req)
      except urllib2.URLError, e:
        logging.warning("bad %s, %s" % (d.strftime("%y%m%d"), e))
        continue
      logging.info("success %s" % d.strftime("%y%m%d"))
      zf = ZipFile(StringIO(response.read()), "r")
      filename = zf.namelist()[0]
      zf.extract(filename, outdir)


def load(days, indir="./input"):
  pieses = []
  for d in days or []:
    filepath = join(indir, "f%s.xls") % d.strftime("%y%m%d")
    if not exists(filepath):
      logging.warning("skip %s" % filepath)
      continue
    logging.info("loaded %s" % filepath)
    with open(filepath) as f:
      xd = pd.ExcelFile(f)
      pieses.append(xd.parse(xd.sheet_names[-1]))
  return pd.concat(pieses)


if __name__ == '__main__':
  #download([2012, 2013], "./input")
  load(rrule(DAILY,
             dtstart=datetime(year=2012, month=1, day=1),
             until=datetime(year=2013, month=1, day=1)))
