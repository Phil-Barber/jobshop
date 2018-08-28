import csv
from datetime import time

class Problem:
    def __init__(self, jobs):
        self.jobs = jobs
        self.machines = []
        self.get_machines()

    def flatten(self):
        flat = []
        for j in self.jobs:
            flat.append(j.flatten(self.machines))
        return flat

    # map machines from name to index
    def get_machines(self):
        for j in self.jobs:
            machines = j.get_machines()
            for machine in machines:
                if machine not in self.machines:
                    self.machines.append(machine)

    def get_machine(self, index):
        return self.machines[index]
        
    def mix_machines(self):
        for j in self.jobs:
            for o in j.operations:
                for m in self.machines:
                    new_task = o.tasks[0]
                    if new_task.machine != m: 
                        new_task.machine = m
                        o.tasks.append(new_task)
                 
              
        


class Job:
    def __init__(self, name, operations, dueDate = 0):
        self.name = name
        self.operations = operations
        self.dueDate = dueDate

    def flatten(self, machines):
        flat = []
        for o in self.operations:
            flat.append(o.flatten(machines))
        return flat

    def get_machines(self):
        for o in self.operations:
            return o.get_machines()

class Operation: 
    tasks = []

    def __init__(self, tasks):
        self.tasks = tasks

    def flatten(self, machines):
        flat = []
        for t in self.tasks:
            flat.append(t.flatten(machines))
        return flat

    def get_machines(self):
        machines = []
        for t in self.tasks:
            machine = t.machine
            if machine not in machines:
                machines.append(machine)
        return machines
            

class Task: 
    def __init__(self, machine, duration):
        self.machine = machine
        self.duration = duration


    def flatten(self, machines):
        return (self.duration, machines.index(self.machine))

def load_data(file, indexes):
    jobs = []
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        # skip headers
        next(reader, None)
        for row in reader:
            duration = get_duration_in_secs(row[indexes['duration']])
            task = Task(row[indexes['machine']], duration)
            operation = Operation([task])
            job = Job(row[indexes['name']], [operation])
            jobs.append(job)
            
    return Problem(jobs)

def get_duration_in_secs(string):

    daySplit = string.split('d')
    rest = daySplit[0]
    days = 0
    if len(daySplit) > 1:
        days = int(daySplit[0])
        rest = daySplit[1]

    hourSplit = rest.split('h')
    rest = hourSplit[0]
    hours = days*24
    if len(hourSplit) > 1:
        hours += int(hourSplit[0].replace(":", ""))
        rest = hourSplit[1]

    minSplit = rest.split('m')
    rest = minSplit[0]
    mins = 0
    if len(minSplit) > 1:
        mins += int(minSplit[0].replace(":", ""))
        rest = minSplit[1]

    secSplit = rest.split('s')
    rest = secSplit[0]
    secs = 0
    if len(secSplit) > 1:
        secs += int(secSplit[0].replace(":", ""))
        rest = secSplit[1]

    return secs + (mins * 60) + (hours * 60*60)
  
