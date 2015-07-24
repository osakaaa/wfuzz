#!/usr/bin/python

#Covered by GPL V2.0

import sys
from framework.fuzzer.Fuzzer import Fuzzer
from framework.core.facade import Facade
from framework.core.myexception import FuzzException

from framework.ui.console.keystroke import KeyPress
from framework.ui.console.controller import Controller
from framework.ui.console.clparser import CLParser

kb = None
fz = None
printer = None

try:
    # parse command line 
    session_options = CLParser(sys.argv).parse_cl()
    genreqs = session_options.get("genreq")
    #Kostyling (e.g. krutches)
    # Here we try to get list of urls's from session_options and then put it back one by one so basic fuzzing mechanism do not broke
    for genreq in genreqs:
        # Create fuzzer's engine
        session_options.set("genreq",genreq)
        fz = Fuzzer(session_options)

        if session_options.get("interactive"):
            # initialise controller
            try:
                kb = KeyPress()
            except ImportError, e:
                raise FuzzException(FuzzException.FATAL, "Error importing necessary modules for interactive mode: %s" % str(e))
            else:
                mc = Controller(fz, kb)
                kb.start()

        printer = Facade().get_printer(session_options.get("printer_tool"))
        printer.header(fz.genReq.stats)

        for res in fz:
            printer.result(res) if res.is_visible else printer.noresult(res)

        printer.footer(fz.genReq.stats)
except FuzzException, e:
    print "\nFatal exception: %s" % e.msg
    if fz: fz.cancel_job()
except KeyboardInterrupt:
    print "\nFinishing pending requests..."
    if fz: fz.cancel_job()
except NotImplementedError, e:
    print "\nFatal exception: Error importing wfuzz extensions"
finally:
    if kb: kb.cancel_job()
    Facade().sett.save()
