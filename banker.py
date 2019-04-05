"""
- optimistic resource manager: satisfy request if possible, if not make task wait.
- pending request in FIFO
- input 1st line: # tasks, # resource type with # units
- initiate  task-number  delay  resource-type  initial-claim
- request  ..................................  number-requested
- release  ..................................  number-released
- terminate  task-number  delay
- optimistic manager ignores claim
- process retain resource during delay
- add comment for data structure, checking for safety, checking deadlock, releasing blocked task
- output: time taken, waiting time, percentage of time spent waiting
- Banker error check: if initial claim exceed resource present or request exceed during
  execution, print message, abort task, release all its resources.
- If deadlocked, print message, abort lowest numbered deadlocked task after releasing all its resources
- deadlock detection: all non-terminated tasks have outstanding requests that manager can't satisfy
-
"""

import sys
from decimal import Decimal

input = sys.argv[1]
firstLine = []
data = []

with open(input, 'r') as f:
    lines = f.readlines()

    # append the first line of inputs to firstLine list
    temp = lines[0].rstrip("\n").split(" ")
    for t in temp:
        firstLine.append(int(t))

    # append data except first line to data, making list of lists
    for line in range(1, len(lines)):
        data.append(lines[line].rstrip("\n").split())

class Task:
    def __init__(self, taskNum, numResource):
        self.taskNum = taskNum
        self.numResource = numResource
        self.state = "unstarted"
        self.resourceClaims = []
        self.resourceHolding = []
        self.activityQueue = [[]]  # everything needed to do for each task
        self.timeUsed = 0
        self.waitingTime = 0

    def addActivity(self, ins, num, delay, type, numRes):
        self.activityQueue.append([ins, num, delay, type, numRes])

    def removeActivity(self):
        if self.state == "aborted":
            return
        # pop if delay is 0
        elif self.activityQueue[0][2] == "0":
            return self.activityQueue.remove(0)
        else:
        # if delay isn't 0 yet, decrement it
            self.activityQueue[0][2] -= 1
            return

    def getWaitingPercentage(self):
        return round(Decimal(self.waitingTime/self.timeUsed), 2)

def FIFO():

    return



def Banker():
    return


print("FIFO: ")
print(FIFO())

print("Banker's: ")
print(Banker())
