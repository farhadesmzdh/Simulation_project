import math

import numpy

# GETTING INPUTS
X = int(input("X:   "))
Y = int(input("Y:   "))
Z = int(input("Z:   "))
count_tasks = int(input("count tasks:   "))
time_of_simulation = int(input("time of simulation:    "))


# LAYER ONE : CREATING TASK
class Task:
    def __init__(self, interval, service_time, priority):
        self.interval = interval
        self.service_time = service_time
        self.priority = priority
        self.time_queue = 0


class Queue:
    def __init__(self, name, quantum_time):
        self.name = name
        self.quantum_time = quantum_time
        self.tasks = []


def JobCreator():
    intervals = numpy.random.poisson(X, count_tasks)
    intervals = [sum(intervals[:i]) for i in range(1, count_tasks + 1)]
    service_times = [int(x) for x in numpy.random.exponential(Y, count_tasks)]
    for i in range(count_tasks):
        while True:
            if service_times[i] == 0:
                service_times[i] = int(numpy.random.exponential(Y, 1))
            else:
                break
    priorities = numpy.random.choice(["Low", "Normal", "High"], count_tasks, True, [0.7, 0.2, 0.1])
    return [Task(intervals[i], service_times[i], priorities[i]) for i in range(count_tasks)]


priority_queue = Queue("priority_queue", 0)
priority_queue.tasks = JobCreator()

# LAYER TWO : TRANSFERRING
FCFS = Queue("FCFS", math.inf)
Round_Robin_T1 = Queue("Round_Robin_T1", 6)
Round_Robin_T2 = Queue("Round_Robin_T2", 10)
time_period = 15
k = 5
priority_queue.tasks.sort(key=lambda x: x.interval, reverse=False)


def JobLoading(time):
    if len(FCFS.tasks) + len(Round_Robin_T1.tasks) + len(Round_Robin_T2.tasks) < k:
        counter = 0
        for task in priority_queue.tasks:
            if counter == k or task.interval > time:
                break
            if task.service_time <= Round_Robin_T1.quantum_time:
                Round_Robin_T1.tasks.append(task)
            elif task.service_time <= Round_Robin_T2.quantum_time:
                Round_Robin_T2.tasks.append(task)
            else:
                FCFS.tasks.append(task)
            priority_queue.tasks.remove(task)
            counter += 1


# RUNNING TASKS
class DoneTask:
    def __init__(self, task, time_start):
        self.task = task
        self.time_start = time_start


class CPU:
    def __init__(self):
        self.assigned_task = None
        self.time_working = 0
        self.time_start_task = 0
        self.done_tasks = []
        self.length_queue = []


cpu = CPU()


def assign_task_to_CPU(current_time):
    if len(FCFS.tasks) == 0 and len(Round_Robin_T1.tasks) == 0 and len(Round_Robin_T2.tasks) == 0:
        return
    while True:
        chosen = numpy.random.choice(["FCFS", "Round_Robin_T1", "Round_Robin_T2"], 1, True, [0.1, 0.8, 0.1])
        if chosen == "FCFS":
            chosen_queue = FCFS
        elif chosen == "Round_Robin_T1":
            chosen_queue = Round_Robin_T1
        else:
            chosen_queue = Round_Robin_T2
        if len(chosen_queue.tasks) != 0:
            break
    cpu.assigned_task = chosen_queue.tasks[0]
    chosen_queue.tasks.pop(0)
    cpu.time_start_task = current_time


time_out = int(numpy.random.exponential(Z, 1))

for time in range(time_of_simulation):
    if time % time_period == 0:
        JobLoading(time)

    # UPDATING TIME_QUEUE FOR TASKS
    for task in FCFS.tasks:
        task.time_queue += 1
    for task in Round_Robin_T1.tasks:
        task.time_queue += 1
    for task in Round_Robin_T2.tasks:
        task.time_queue += 1
    for task in priority_queue.tasks:
        task.time_queue += 1

    if cpu.assigned_task is None:
        assign_task_to_CPU(time)
    else:
        cpu.time_working += 1
        # CHECK WHETHER ASSIGNED TASK TO CPU IS FINISHED
        if time >= cpu.time_start_task + cpu.assigned_task.service_time:
            cpu.done_tasks.append(DoneTask(cpu.assigned_task, cpu.time_start_task))
            cpu.assigned_task = None
            assign_task_to_CPU(time)

    # CHECKING WHETHER TIMEOUT IS HAPPENED
    for task in FCFS.tasks:
        if task.time_queue > time_out:
            FCFS.tasks.remove(task)
        else:
            break
    for task in Round_Robin_T1.tasks:
        if task.time_queue > time_out:
            Round_Robin_T1.tasks.remove(task)
        else:
            break
    for task in Round_Robin_T2.tasks:
        if task.time_queue > time_out:
            Round_Robin_T2.tasks.remove(task)
        else:
            break
    for task in priority_queue.tasks:
        if task.time_queue > time_out:
            priority_queue.tasks.remove(task)
        else:
            break
    cpu.length_queue.append(len(FCFS.tasks) + len(Round_Robin_T1.tasks) + len(Round_Robin_T2.tasks))


print("***************************************************")
print(f"Average length of queues = {sum(cpu.length_queue) / time_of_simulation} s")
print("***************************************************")
print("Time spent in queues:")
time_queues = []
for done_task in cpu.done_tasks:
    time_queues.append(done_task.task.time_queue)
print(f"    ", end='')
if len(time_queues) == 0:
    print("empty")
else:
    print(*time_queues)
    print(f"    Average = {sum(time_queues) / len(time_queues)} s")
print("***************************************************")
print(f"CPU efficiency = {cpu.time_working / time_of_simulation} %")
print("***************************************************")
print("If we increase T1 and T2, average time spent in queues would be less.")
print("***************************************************")
print(f"Dumped tasks rate = {(count_tasks - len(cpu.done_tasks)) * 100 / count_tasks} %")