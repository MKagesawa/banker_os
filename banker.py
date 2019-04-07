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

tVal = firstLine[0]
rVal = firstLine[1]

resources = {}

class Task:
    def __init__(self, taskNum, numResource):
        self.taskNum = taskNum
        self.numResource = numResource
        self.state = "unstarted"
        self.resourceClaims = {}
        self.resourceHolding = {}
        self.activityQueue = []  # everything needed to do for each task
        self.timeUsed = 0
        self.waitingTime = 0

    def addActivity(self, instruction, num, delay, type, numRes):
        self.activityQueue.append([instruction, num, delay, type, numRes])

    def removeActivity(self):
        if self.state == "aborted":
            return
        # pop if delay is 0
        elif self.activityQueue[0][2] == 0:
            return self.activityQueue.remove(0)
        else:
        # if delay isn't 0 yet, decrement it
            self.activityQueue[0][2] = int(self.activityQueue[0][2]) - 1
            return

    def getWaitingPercentage(self):
        if self.timeUsed > 0:
            return round(Decimal(self.waitingTime/self.timeUsed), 2)
        else:
            return 0

def taskFinished(tasks):
    finished = True
    for t in tasks:
        if t != "terminated" and t != "aborted":
            finished = False
    return finished

def isDeadlocked(listA, listB):
    if not listB: # check if empty, if nothing is blocked, then not deadlocked
        return False
    # if something is running, then not deadlocked
    for a in listA:
        if a == "running":
            return False
    # if request can be granted, not deadlocked
    for b in listB:
        if int(resources[b.activityQueue[0][3]]) >= int(b.activityQueue[0][4]):
            return False
    return True



def FIFO():
    tasks = []
    # initialize tasks and add to list
    for i in range(1, tVal + 1):
        tasks.append(Task(i, rVal))

    # print('tasks: ', tasks)
    # print('firstLine: ', firstLine)

    # add resources
    for i in range(2, rVal + 2):
        resources[i-1] = int(firstLine[i])
    # print('resources: ', resources)

    # add instructions to activity Queue of Task class
    for ins in data:
        tasksNum = int(ins[1])
        tasks[tasksNum - 1].addActivity(ins[0], ins[1], ins[2], ins[3], ins[4])
    # print(tasks[0].activityQueue)

    blockedQueue = []

    # keep running until every task is either terminated or aborted
    while not taskFinished(tasks):
        # resources to be added at end of each cycle
        addDict = {}
        # tasks that can be unblocked and removed from blokckedQueue
        unblockable = []
        # check if task can be resolved
        for task in blockedQueue:
            activity = task.activityQueue[0]
            print('activity', activity)
            # check if resource requested can be fulfilled
            if activity[0] == "request" and activity[4] <= resources[int(activity[3])]:
                task.state = "unstarted"
                task.resourceHolding.replace(activity[3], (activity[4] + task.resourceHolding[int(activity[3])]))
                resources[activity[3]] = resources[activity[3]] - activity[4]
                unblockable.append(task)

        # remove resolved task from blocked Queue
        if(len(unblockable) > 0):
            for u in unblockable:
                blockedQueue.remove(u)

        # iterate through all tasks
        for task in tasks:
            activityList = []
            if len(task.activityQueue) > 0:
                activityList.append(task.removeActivity())
                # if task not processed, delay added
                if len(activityList) == 0:
                    task.timeUsed += 1
                    continue

            if task.state == "running" or task.state == "blocked":

                if activityList[0] == "request":
                    # calculate resources left
                    resLeft = resources[activity[3] - activity[4]]
                    # if it can be granted then grant
                    if resLeft >= 0:
                        resources[int(activity[3])] = resLeft
                        task.resourceHolding[int(activityList[3])] = int(activityList[3]) + int(activityList[4])
                        task.state = "running"
                    else:
                        task.state = "blocked"
                        if task not in blockedQueue:
                            blockedQueue.append(task)
                        # add the activity back to the front of activity queue
                        task.activityQueue[0].append(activity)
                        task.waitingTime += 1
                    task.timeUsed += 1

                elif activityList[0] == "release":
                    index = activityList[3]
                    if index in addDict:
                        addDict[index] = int(addDict[index]) + int(activityList[4])
                    else:
                        addDict[index] = activityList[4]
                    # new holding prior holding - amount released
                    newHold = task.resourceHolding[index] - activityList[3]
                    task.resourceHolding[activityList[3]] = newHold
                    task.timeUsed += 1

                elif activityList[0] == "terminate":
                    task.state = "terminated"

            if task.state == "unstarted":
                if activityList[0] == "terminate":
                    task.state = "terminated"
                elif activityList[0] == "initiate":
                    # count number of initiates
                    counter = 1
                    for t in task.activityQueue:
                        if t[0] == "initiate":
                            counter += 1
                        else:
                            break
                    task.state = "running"
                    task.resourceClaims[activityList[3]-1] = activityList[4]
                    task.timeUsed += counter
                elif activityList[0] == "request":
                    task.state = "running"
                    task.resourceClaims[activityList[3]-1] = activityList[4]
                    task.timeUsed += 1

        # run until deadlock resolved
        while not isDeadlocked(tasks, blockedQueue) and not len(blockedQueue) == 0:
            lowTask = blockedQueue[0].taskNum
            # get the task with lowest taskNum
            for blockedTask in blockedQueue:
                if blockedTask.taskNum < lowTask:
                    lowTask = blockedTask

            lowTask.state = "aborted"
            for i in range(len(resources)):
                # put resource of aborted task back to pool of resources
                resources[i] = resources[i] + lowTask.resourceHolding[i]
            blockedQueue.remove(lowTask)

        # add back input amount back to pool of resources
        for k in addDict.keys():
            resources[k] = resources[k] + int(addDict[k])

        # print results
        totalTime = 0
        totalWait = 0
        for i in range(len(tasks)):
            if tasks[i].state == "aborted":
                print("Task " + str(i) + "\taborted")
            else:
                task = tasks[i]
                print("Task " + str(i) + str(task.timeUsed) + " " + str(task.waitingTime) + " " + str(task.getWaitingPercentage()) + "%")
                totalTime += task.timeUsed
                totalWait += task.waitingTime



def Banker():
    return


print("FIFO: ")
print(FIFO())

print("Banker's: ")
print(Banker())
