from libvbts import FreeSwitchMessenger
from freeswitch import *
import os, sys

REC_HOME = "/tmp/"

STATES = {"INTRO":0,
          "RECORDING":1,
          "PLAYING":2}

class VillageIdolRecorder:

    def __init__(self, session):
        self.session = session            
        session.setDTMFCallback(self.dtmf_handler, "")
        self.fs = FreeSwitchMessenger.FreeSwitchMessenger()
        self.state = STATES["INTRO"]
        
    def dtmf_handler(self, input, itype, funcargs):
        console_log("INFO","\n\nDTMF input: %s\n" % input)
        return "stop"

    def main(self):
        user = self.session.getVariable("username")
        console_log("info", "username:: %s" % user)
        file_loc = REC_HOME + self.username + ".wav"
        while (True):
            if (self.state == STATES["INTRO"]):
                thing2say = "intro.wav"
                in_rslt = self.session.playAndGetDigits(1,1,1,10000,
                                                        "*#",thing2say,
                                                        "","")[1]
                if in_rslt:
                    if int(in_rslt) == 1:
                        self.state = STATES["RECORDING"]
                    elif int(in_rslt) == 2:
                        self.state = STATES["PLAYING"]
                    else:
                        #pass, go back to intro
                        pass
            elif (self.state == STATES["RECORDING"]):
                self.session.recordFile(file_loc, 60*3, 200) 
                #transition back to intro
                self.state = STATES["INTRO"]
            elif (self.state == STATES["PLAYING"]):
                in_rslt = self.session.streamFile(file_loc)
                #transition back to intro
                self.state = STATES["INTRO"]
            else:
                exit(1)

def handler(uuid):
    if not uuid:
        console_log("info", "\nNo uuid given\n")
        return
    session = PySession(uuid)
    vir = VillageIdolRecorder(session)
    vir.main()
