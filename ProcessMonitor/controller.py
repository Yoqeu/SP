import psutil
import wx
import pubsub

from model import Process
from threading import Thread
# from wx.lib.pubsub import setupkwargs
from pubsub import pub as Publisher


class ProcThread(Thread):
    """
    Gets all the process information we need as psutil isn't very fast
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        Thread.__init__(self)
        self.start()

        # ----------------------------------------------------------------------

    def run(self):
        """"""
        processes = list(psutil.process_iter())
        proccs = []
        cpu_percent = 0
        mem_percent = 0
        for p in processes:
            try:
                cpu = p.cpu_percent()
                mem = p.memory_percent()
                memory_info = p.memory_info()
                new_proc = Process(p.name(),
                                   str(p.pid),
                                   p.exe(),
                                   p.username(),
                                   str(cpu),
                                   str(mem),
                                   memory_info.rss / 1024 / 1024,
                                   memory_info.vms / 1024 / 1024,
                                   memory_info.num_page_faults,
                                   memory_info.peak_wset
                                   )
                proccs.append(new_proc)
                cpu_percent += cpu
                mem_percent += mem
            except Exception as e:
                print(e)

        # send pids to GUI
        wx.CallAfter(Publisher.sendMessage, "update", msg=proccs)

        number_of_procs = len(proccs)
        wx.CallAfter(Publisher.sendMessage, "update_status", msg=(number_of_procs, cpu_percent, mem_percent))
