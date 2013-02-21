#Copyright 2012 Kurtis Heimerl <kheimerl@cs.berkeley.edu>. All rights reserved.
#
#Redistribution and use in source and binary forms, with or without modification, are
#permitted provided that the following conditions are met:
#
#   1. Redistributions of source code must retain the above copyright notice, this list of
#      conditions and the following disclaimer.
#
#   2. Redistributions in binary form must reproduce the above copyright notice, this list
#      of conditions and the following disclaimer in the documentation and/or other materials
#      provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY Kurtis Heimerl ''AS IS'' AND ANY EXPRESS OR IMPLIED
#WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
#FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Kurtis Heimerl OR
#CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#The views and conclusions contained in the software and documentation are those of the
#authors and should not be interpreted as representing official policies, either expressed
#or implied, of Kurtis Heimerl.
from libvbts import FreeSwitchMessenger
from freeswitch import *
import os, sys, time, ctypes

REC_HOME = "/var/www/village_idol/"

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
    session.unsetInputCallback()
