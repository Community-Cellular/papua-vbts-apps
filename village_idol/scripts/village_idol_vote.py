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
import os, glob, random

REC_HOME = "/var/www/village_idol/"

PLAY_HOME = "/usr/local/freeswitch/sounds/"

STATES = {"INTRO":0,
          "PLAYING":1,
          "FINISHED":2}

BEEP = "tone_stream://%(500,475,1000)"

def input_callback(session, what, obj, arg):
    if (what == "dtmf"):
        if (arg.state == STATES["INTRO"]):
            arg.change_state("PLAYING")
        elif(arg.state == STATES["PLAYING"] and arg.file):
            vote_file = arg.generate_vote_file(arg.file)
            f = open(vote_file, 'w')
            f.write(obj.digit)
            f.close()
            arg.change_state("INTRO")
        else:
            arg.change_state("INTRO")
    else:
        consoleLog("info", what + " " + obj.serialize() + "\n")
    return "stop"

class VillageIdolVoter:

    def __init__(self, session):
        self.session = session            
        self.fs = FreeSwitchMessenger.FreeSwitchMessenger()
        self.state = STATES["INTRO"]
        self.loops = 0
        self.start = True

    def generate_vote_file(self, filename):
        return filename + "." + self.username + ".vote"

    def get_files(self):
        all_audio_files = glob.glob(REC_HOME + "*.gsm")
        need_voting = []
        for f in all_audio_files:
            if not (os.path.exists(self.generate_vote_file(f))):
                need_voting.append(f)
                
        return need_voting

    def main(self):
        self.username = self.session.getVariable("username")
        console_log("info", "username:: %s\n" % self.username)
        while (self.loops < 10):
            self.loops += 1
            if (self.state == STATES["INTRO"]):
                files = self.get_files()
                if (len(files) == 0):
                    self.change_state("FINISHED")
                else:
                    self.file = random.choice(files)
                    if (self.start):
                        thing2say = PLAY_HOME + "vote_intro.wav"
                        self.session.streamFile(thing2say)
                        self.start = False
                    self.change_state("PLAYING")
            elif (self.state == STATES["PLAYING"]):
                #any button causes exit
                self.session.streamFile(self.file)
                self.session.streamFile(BEEP)
                #stay in this state until voted
            elif (self.state == STATES["FINISHED"]):
                    self.file = None
                    thing2say = PLAY_HOME + "vote_fail.wav"
                    self.session.streamFile(thing2say)
                    return

    def change_state(self, state):
        consoleLog("info", "Changing state from %s to %s\n" % (self.state, STATES[state]))
        if (self.state != STATES[state]):
            self.loops = 0
            if state in STATES.keys():
                self.state = STATES[state]

def handler(session, args):
    viv = VillageIdolVoter(session)
    session.setInputCallback(input_callback, viv)
    viv.main()
    consoleLog("info", "Exiting\n")
    session.unsetInputCallback()
