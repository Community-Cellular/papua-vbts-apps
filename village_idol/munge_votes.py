#!/usr/bin/python

import sys
import re
import numpy

VOTE_RE = re.compile("(IMSI\d{15})\.gsm\.(IMSI\d{15})\.vote")

VOTES = {}

def insert_vote(target, vote):
    if target not in VOTES:
        VOTES[target] = []
    VOTES[target].append(vote)

for v in sys.argv[1:]:
    m = VOTE_RE.match(v)
    if not (m):
        print ("Malformed vote: " + v)
    else:
        f = open(v)
        vote = int(f.readline())
        insert_vote(m.group(1), vote)

print ("VOTE FILE,N,MEAN,MEDIAN")
for t in VOTES.keys():
    print (t + ".gsm," + str(len(VOTES[t])) + "," + str(numpy.mean(VOTES[t])) + "," + str(numpy.median(VOTES[t])))
