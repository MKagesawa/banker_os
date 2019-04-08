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
# for debugger
# input = "input-02.txt"
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

        # initialize resource holdings and claims with resources and number set to 0
        for i in range(numResource):
            self.resourceClaims[i+1] = 0
            self.resourceHolding[i+1] = 0

    def addActivity(self, instruction, num, delay, type, numRes):
        self.activityQueue.append([instruction, num, delay, type, numRes])

    def removeActivity(self):
        if self.state == "aborted":
            return
        # pop if delay is 0
        elif self.activityQueue[0][2] == "0":
            return self.activityQueue.pop(0)
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
        if t.state != "terminated" and t.state != "aborted":
            finished = False
    return finished

def isDeadlocked(listA, listB):
    if len(listB) == 0: # check if empty, if nothing is blocked, then not deadlocked
        return False
    # if something is running, then not deadlocked
    for a in listA:
        if a.state == "running":
            return False
    # if request can be granted, not deadlocked
    for b in listB:
        # print('b.activityQueue', b.activityQueue)
        print("b.activityQueue[0][3]: ", int(resources[int(b.activityQueue[0][3])]))
        print("b.activityQueue[0][4]: ", int(b.activityQueue[0][4]))
        if int(resources[int(b.activityQueue[0][3])]) >= int(b.activityQueue[0][4]):
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
            # print('activity', activity)
            # check if resource requested can be fulfilled
            if activity[0] == "request" and int(activity[4]) <= resources[int(activity[3])]:
                task.state = "unstarted"
                task.resourceHolding[activity[3]] = int(activity[4]) + task.resourceHolding[int(activity[3])]
                resources[activity[3]] = resources[int(activity[3])] - int(activity[4])
                unblockable.append(task)

        # remove resolved task from blocked Queue
        if(len(unblockable) > 0):
            for u in unblockable:
                blockedQueue.remove(u)

        # iterate through all tasks
        for task in tasks:
            print('resources: ', resources)
            print(task.taskNum, task.state)
            print('task.resourceHolding: ', task.taskNum, task.resourceHolding)
            activityList = []
            # print('taskNum', task.taskNum)
            # print('activityQueue', task.activityQueue)
            if len(task.activityQueue) > 0:
                activityList = task.removeActivity()
                # if task not processed, delay added
                if activityList is None:
                    task.timeUsed += 1
                    continue
            # print('activityList', activityList)

            if task.state == "running" or task.state == "blocked":

                if activityList[0] == "request":
                    # calculate resources left
                    # print('resources', resources)
                    # print('int(activityList[3]): ', int(activityList[3]))
                    # print('int(activityList[4]): ', int(activityList[4]))
                    resLeft = resources[int(activityList[3])] - int(activityList[4])
                    # if it can be granted then grant
                    if resLeft >= 0:
                        resources[int(activityList[3])] = resLeft
                        task.resourceHolding[int(activityList[3])] = task.resourceHolding[int(activityList[3])] + int(activityList[4])
                        task.state = "running"
                    else:
                        task.state = "blocked"
                        if task not in blockedQueue:
                            blockedQueue.append(task)
                        # add the activity back to the front of activity queue
                        task.activityQueue.insert(0, activityList)
                        task.waitingTime += 1
                    task.timeUsed += 1

                elif activityList[0] == "release":
                    index = activityList[3]
                    if index in addDict:
                        addDict[index] = int(addDict[index]) + int(activityList[4])
                    else:
                        addDict[index] = activityList[4]
                    # new holding prior holding - amount released
                    newHold = task.resourceHolding[int(index)] - int(activityList[3])
                    task.resourceHolding[activityList[3]] = newHold
                    task.timeUsed += 1

                elif activityList[0] == "terminate":
                    task.state = "terminated"

            if task.state == "unstarted":
                # print('activityList', activityList)
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
                    task.resourceClaims[int(activityList[3])] = int(activityList[4])
                    task.timeUsed += counter
                elif activityList[0] == "request":
                    task.state = "running"
                    task.resourceClaims[int(activityList[3])] = int(activityList[4])
                    task.timeUsed += 1

        # run until deadlock resolved
        while isDeadlocked(tasks, blockedQueue) and len(blockedQueue) != 0:
            lowTask = blockedQueue[0]
            # get the task with lowest taskNum
            for blockedTask in blockedQueue:
                if blockedTask.taskNum < lowTask.taskNum:
                    lowTask = blockedTask

            lowTask.state = "aborted"
            for i in range(1, len(resources) + 1):
                # put resource of aborted task back to pool of resources
                resources[i] = resources[i] + lowTask.resourceHolding[i]
                print(resources)
            blockedQueue.remove(lowTask)

        # add back input amount back to pool of resources
        for k in addDict.keys():
            resources[int(k)] = resources[int(k)] + int(addDict[k])

    # print results
    totalTime = 0
    totalWait = 0
    totalPercent = 0
    for i in range(len(tasks)):
        if tasks[i].state == "aborted":
            print("Task " + str(i + 1) + "\taborted")
        else:
            task = tasks[i]
            print("Task " + str(i + 1) + "\t" + str(task.timeUsed) + "\t" + str(task.waitingTime) + "\t" + str(task.getWaitingPercentage()*100) + "%")
            totalTime += task.timeUsed
            totalWait += task.waitingTime

    if totalTime > 0:
        totalPercent = round(Decimal(totalWait / totalTime), 2)
    print("total\t" + str(totalTime) + "\t" + str(totalWait) + "\t" + str(totalPercent*100) + "%")


def Banker():
    return


print("FIFO: ")
print(FIFO())

print("Banker's: ")
print(Banker())
