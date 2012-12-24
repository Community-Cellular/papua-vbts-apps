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
import sqlite3, random

class FriendDB:

    DB_HOME = "/etc/OpenBTS/"
    
    DB_NAME = "find_a_friend.db"

    USER_DB_INIT = "CREATE TABLE IF NOT EXISTS users (user TEXT UNIQUE PRIMARY KEY)"

    FRIEND_DB_INIT = "CREATE TABLE IF NOT EXISTS %s (friend TEXT UNIQUE PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP')"

    def __init__(self):
        self.conn = sqlite3.connect(FriendDB.DB_HOME + FriendDB.DB_NAME)
        self.cur = self.conn.cursor()
        self.cur.execute(FriendDB.USER_DB_INIT)
        self.conn.commit()
        
    def find_friend(self, name):
        #first make sure they have a table and insert them into main table
        self.cur.execute("CREATE TABLE IF NOT EXISTS %s (friend TEXT PRIMARY KEY)" % name)
        self.conn.commit()
        try:
            self.cur.execute("INSERT INTO users (user) values (?)", (name,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass #already in the DB
        #ok, they're in the DB, let's get all the users
        users = self.cur.execute("SELECT user FROM users").fetchall()
        #and all the friends
        friends = self.cur.execute("SELECT friend FROM %s" % name).fetchall()
        friends.append((name,))
        #and remove each friend from the pool of users


        for friend in friends:
            if friend in users:
                users.remove(friend)

        if (len(users)== 0):
            return None
        else:
            return random.choice(users)[0]

class FindAFriend:

    def __init__(self):
        self.fs = FreeSwitchMessenger.FreeSwitchMessenger()
        
    def main(self, username):
        user = username
        console_log("info", "username:: %s\n" % user)
        fdb = FriendDB()
        return fdb.find_friend(username)


