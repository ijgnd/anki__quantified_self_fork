"""
Add-on for anki "Quantified self", v0.2.21

Copyright (c) 2017 by Thomas TEMPÉ, <thomas.tempe@alysse.org>
          (c) 2020 ijgnd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version, unless otherwise noted.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


import io
import time
import csv
import os.path

from anki.lang import _

from aqt import mw
from aqt.utils import getSaveFile, showInfo
from aqt.qt import *


def gc(arg, fail=False):
    conf = mw.addonManager.getConfig(__name__)
    if conf:
        return conf.get(arg, fail)
    return fail


class PerformanceExtractor():
    def __init__(self, filter=filter):
        self.filter = gc("filter")
        self.history = []

    def parse_revlog(self):
        'Parse the revisions history, card by card'
        #identify the list of cards that will be exported
        cids = mw.col.findCards(self.filter)
        for cid in cids: #for each card
            # card = mw.col.getCard(cid)
            entries = mw.col.db.all(
                "select id/1000.0, ease, ivl, factor/1000.0, time/1000.0, type "
                "from revlog where cid = ? order by id", cid)

            #Go through all revisions in the revisions log
            for index, entry in enumerate(entries):
                (date, ease, interval, factor, taken, ctype) = entry
                try: #try to get the next revision, if it exists
                    (next_date, next_ease, next_interval, next_factor, next_taken, next_ctype) = entries[index+1]
                except IndexError:
                    if gc("also_export_last"):
                        (next_date, next_ease, next_interval, next_factor, next_taken, next_ctype) = ("", "", "", "", "", 5)
                    else:
                        continue
                #Filter by date, if applicable
                date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))
                sr = gc("start_date_range")
                er = gc("end_date_range")
                if (sr and sr>date) or (er and er<date):
                    continue

                #Format the various fields prior to export
                ctype = [_("Learn"), _("Review"), _("Relearn"), _("Filtered"), _("Resched")][ctype]        
                next_ctype = [_("Learn"), _("Review"), _("Relearn"), _("Filtered"), _("Resched"), ""][next_ctype]        
                if next_date:
                    next_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_date))
                if interval < 0: #that's a quirk in Anki, for "learning" cards
                    interval = -interval/24/3600
                if next_interval < 0:
                    next_interval = -next_interval/24/3600

                #store in memory
                self.history.append([date, 
                                     ease, 
                                     interval, 
                                     factor, 
                                     taken, 
                                     ctype, 
                                     next_date, 
                                     next_ease, 
                                     next_taken, 
                                     next_ctype, 
                                     cid])

    def export_csv(self, filename):
        'Save revisions history to a CSV file'
        with io.open(filename, "w", encoding="utf-8") as fd:
            self.parse_revlog()
            w = csv.writer(fd)
            w.writerow(["Date1",
                        "Answer1",
                        "Interval",
                        "Ease factor",
                        "Time to answer1",
                        "Review type1",
                        "Date2",
                        "Answer2",
                        "Time to answer2",
                        "Review type2",
                        "Card ID"])
            w.writerows(self.history)


def do_the_export():
    'Query filename from user, then export revision history to CSV file'
    filename = getSaveFile(parent=None,
                           title="Export memorization performance history",
                           dir_description="qs_addon",
                           key="Comma-separated values",
                           ext="csv",
                           fname="RevisionHistory.csv")
    if filename:
        mw.progress.start()
        pe = PerformanceExtractor()
        try:
            pe.export_csv(filename)
        except IOError:
            showInfo((f"Could not open file <tt>{filename}</tt> for writing. Please make sure"
                      f"it's not open by another application already."))
            return
        mw.progress.finish()
        showInfo("{} reviews exported".format(len(pe.history)))


#Add a pull-down menu item    
action = QAction("Export memorisation performance history", mw)
action.triggered.connect(do_the_export)
mw.form.menuTools.addAction(action)
