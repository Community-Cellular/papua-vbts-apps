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
          "PLAYING":1}

BEEP = "tone_stream://%(500,475,1000)"

def input_callback(session, what, obj, arg):
    if (what == "dtmf"):
        if (arg.state == STATES["INTRO"]):
            arg.change_state("PLAYING")
        elif(arg.state == STATES["PLAYING"] and arg.file):
            vote_file = arg.generate_vote_file()
            f = open(vote_file, 'w')
            f.write(obj.digit)
            f.close()
            arg.change_state("INTRO")
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

    def generate_vote_file(self):
        return self.file + "." + self.username + ".vote"

    def get_files(self):
        all_audio_files = glob.glob(REC_HOME + "*.gsm")
        need_voting = []
        for f in audio_files:
            if not (os.path.exists(generate_vote_file())):
                need_voting.append(f)
                
        return need_voting

    def main(self):
        self.username = self.session.getVariable("username")
        console_log("info", "username:: %s\n" % user)
        while (self.loops < 10):
            self.loops += 1
            if (self.state == STATES["INTRO"]):
                files = get_files().
                if (len(files) == 0):
                    self.file = None
                    thing2say = PLAY_HOME + "vote_fail.wav"
                    self.session.streamFile(thing2say)
                    self.session.hangup()
                else:
                    self.file = random.choice(files)
                    thing2say = PLAY_HOME + "vote_intro.wav"
                    self.session.streamFile(thing2say)
                    change_stage("PLAYING")
            elif (self.state == STATES["PLAYING"]):
                #any button causes exit
                self.session.streamFile(self.file)
                #stay in this state until voted


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
