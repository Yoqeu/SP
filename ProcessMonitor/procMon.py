import controller
import psutil
import wx
import pubsub

from ObjectListView import ObjectListView, ColumnDefn
# from wx.lib.pubsub import setupkwargs
from pubsub import pub as Publisher


class MainPanel(wx.Panel):
    """"""

    # init
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        self.currentSelection = None
        self.gui_shown = False
        self.proccs = []
        self.sort_col = 0

        self.col_w = {"name": 175,
                      "pid": 50,
                      "exe": 300,
                      "user": 90,
                      "cpu": 60,
                      "mem": 75,
                      "rss": 120,
                      "vms": 120,
                      "pfaults": 120,
                      "pageins": 120}

        self.procmonOlv = ObjectListView(self, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self.procmonOlv.Bind(wx.EVT_LIST_COL_CLICK, self.onColClick)
        self.procmonOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onSelect)
        self.setProcs()

        endProcBtn = wx.Button(self, label="End Process")
        endProcBtn.Bind(wx.EVT_BUTTON, self.onKillProc)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.procmonOlv, 1, wx.EXPAND | wx.ALL, 5)
        mainSizer.Add(endProcBtn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetSizer(mainSizer)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.update, self.timer)
        self.update("")
        self.setProcs()

        # subscribe a pubsub receiver
        Publisher.subscribe(self.updateDisplay, "update")

    # ----------------------------------------------------------------------
    def onColClick(self, event):
        """
        Remember which column to sort by, currently only does ascending
        """
        self.sort_col = event.GetColumn()

    # ----------------------------------------------------------------------
    def onKillProc(self, event):
        """
        Kill the selected process by pid
        """
        obj = self.procmonOlv.GetSelectedObject()
        print('')
        pid = int(obj.pid)
        try:
            p = psutil.Process(pid)
            p.terminate()
            self.update("")
        except Exception as e:
            print("Error: " + e)

    # ----------------------------------------------------------------------
    def onSelect(self, event):
        """
        Gets called when an item is selected and helps keep track of 
        what item is selected
        """
        item = event.GetItem()
        itemId = item.GetId()
        self.currentSelection = itemId

    # ----------------------------------------------------------------------
    def setProcs(self):
        """
        Updates the ObjectListView widget display
        """
        cw = self.col_w
        # change column widths as necessary
        if self.gui_shown:
            cw["name"] = self.procmonOlv.GetColumnWidth(0)
            cw["pid"] = self.procmonOlv.GetColumnWidth(1)
            cw["exe"] = self.procmonOlv.GetColumnWidth(2)
            cw["user"] = self.procmonOlv.GetColumnWidth(3)
            cw["cpu"] = self.procmonOlv.GetColumnWidth(4)
            cw["mem"] = self.procmonOlv.GetColumnWidth(5)
            cw["rss"] = self.procmonOlv.GetColumnWidth(6)
            cw["vms"] = self.procmonOlv.GetColumnWidth(7)
            cw["pfaults"] = self.procmonOlv.GetColumnWidth(8)
            cw["pageins"] = self.procmonOlv.GetColumnWidth(9)

        cols = [
            ColumnDefn("name", "left", cw["name"], "name"),
            ColumnDefn("pid", "left", cw["pid"], "pid"),
            ColumnDefn("exe location", "left", cw["exe"], "exe"),
            ColumnDefn("username", "left", cw["user"], "user"),
            ColumnDefn("cpu", "left", cw["cpu"], "cpu"),
            ColumnDefn("mem", "left", cw["mem"], "mem"),
            ColumnDefn("Resident Set Size", "left", cw["rss"], "rss"),
            ColumnDefn("Virtual Memory Size", "left", cw["vms"], "vms"),
            ColumnDefn("Number of page faults", "left", cw["pfaults"], "pfaults"),
            ColumnDefn("Number of actual pageins", "left", cw["pageins"], "pageins"),
            # ColumnDefn("description", "left", 200, "desc")
        ]
        self.procmonOlv.SetColumns(cols)
        self.procmonOlv.SetObjects(self.proccs)
        self.procmonOlv.SortBy(self.sort_col)
        if self.currentSelection:
            self.procmonOlv.Select(self.currentSelection)
            self.procmonOlv.SetFocus()
        self.gui_shown = True

    # ----------------------------------------------------------------------
    def update(self, event):
        """
        Start a thread to get the pid information
        """
        print("update thread started!")
        self.timer.Stop()
        controller.ProcThread()

    # ----------------------------------------------------------------------
    def updateDisplay(self, msg):
        """
        Catches the pubsub message from the thread and updates the display
        """
        print("thread done, updating display!")
        self.proccs = msg
        self.setProcs()
        if not self.timer.IsRunning():
            self.timer.Start(15000)


########################################################################
class MainFrame(wx.Frame):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, title="procMon", size=(1200, 768))
        panel = MainPanel(self)

        # set up the statusbar
        self.CreateStatusBar()
        self.StatusBar.SetFieldsCount(3)
        self.StatusBar.SetStatusWidths([200, 200, 200])

        # create a pubsub receiver
        Publisher.subscribe(self.updateStatusbar, "update_status")

        self.Show()

    # ----------------------------------------------------------------------
    def updateStatusbar(self, msg):
        """"""
        proccs, cpu, mem = msg
        self.SetStatusText("Processes: %s" % proccs, 0)
        self.SetStatusText("CPU Usage: %s" % cpu, 1)
        self.SetStatusText("Physical Memory: %s" % mem, 2)


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()
