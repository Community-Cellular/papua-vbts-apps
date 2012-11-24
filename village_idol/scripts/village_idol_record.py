from libvbts import FreeSwitchMessenger
from freeswitch import *
import os, sys, time, ctypes

REC_HOME = "/tmp/"

PLAY_HOME = "/usr/local/freeswitch/sounds/"

STATES = {"INTRO":0,
          "RECORDING":1,
          "PLAYING":2}

BEEP = "tone_stream://%(500,475,1000)"

def input_callback(session, what, obj, arg):
    if (what == "dtmf"):
        #duration = ctypes.cast(obj.duration.__long__(), ctypes.POINTER(ctypes.c_uint32)).contents.value
        consoleLog("info", what + " " + obj.digit +  " in state: " + str(arg.state) + "\n")
        if (arg.state == STATES["INTRO"]):
            if (obj.digit == "1"):
                arg.change_state("RECORDING")
            elif (obj.digit == "2"):
                arg.change_state("PLAYING")
            else:
                pass
        else:
            arg.change_state("INTRO")
    else:
        consoleLog("info", what + " " + obj.serialize() + "\n")
    return "stop"

class VillageIdolRecorder:

    def __init__(self, session):
        self.session = session            
        self.fs = FreeSwitchMessenger.FreeSwitchMessenger()
        self.state = STATES["INTRO"]
        self.loops = 0
        
    def main(self):
        user = self.session.getVariable("username")
        console_log("info", "username:: %s\n" % user)
        file_loc = REC_HOME + user + ".gsm"
        while (self.loops < 10):
            self.loops += 1
            if (self.state == STATES["INTRO"]):
                thing2say = PLAY_HOME + "intro.wav"
                self.session.streamFile(thing2say)
                #stay in this state
            elif (self.state == STATES["RECORDING"]):
                self.session.streamFile(BEEP)
                self.session.recordFile(file_loc, 60*3) 
                self.session.streamFile(BEEP)
                #transition back to intro
                self.change_state("INTRO")
            elif (self.state == STATES["PLAYING"]):
                #any button causes exit
                self.session.streamFile(file_loc)
                #transition back to intro


    def change_state(self, state):
        consoleLog("info", "Changing state from %s to %s\n" % (self.state, STATES[state]))
        if (self.state != STATES[state]):
            self.loops = 0
            if state in STATES.keys():
                self.state = STATES[state]

def handler(session, args):
    vir = VillageIdolRecorder(session)
    session.setInputCallback(input_callback, vir)
    vir.main()
    consoleLog("info", "Exiting\n")
