# Copyright 2010-2017 Google
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

from collections import defaultdict
from ortools.sat.python import cp_model

# Custom
from load_data import Problem


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
  """Print intermediate solutions."""

  def __init__(self, verbose=True):
    self.__solution_count = 0
    self.verbose = verbose

  def NewSolution(self):
    if self.verbose: print('Solution %i, time = %f s, objective = %i' %
          (self.__solution_count, self.WallTime(), self.ObjectiveValue()))
    self.__solution_count += 1


MAKESPAN = 'makespan'
LMAX = 'Lmax'

def get_schedule(problem, objective, verbose=True):
  jobs = problem.flatten()

  if verbose: print(jobs)

  num_jobs = len(jobs)
  all_jobs = range(num_jobs)

  num_machines = 3
  all_machines = range(num_machines)

  # Model the flexible jobshop problem.
  model = cp_model.CpModel()

  horizon = 0
  for job in jobs:
    for task in job:
      max_task_duration = 0
      for alternative in task:
        max_task_duration = max(max_task_duration, alternative[0])
      horizon += max_task_duration

  # Global storage of variables.
  intervals_per_resources = defaultdict(list)
  starts = {}  # indexed by (job_id, task_id).
  presences = {}  # indexed by (job_id, task_id, alt_id).
  job_ends = []
  job_overdues = []

  # Scan the jobs and create the relevant variables and intervals.
  for job_id in all_jobs:
    job = jobs[job_id]
    num_tasks = len(job)
    previous_end = None
    for task_id in range(num_tasks):
      task = job[task_id]

      min_duration = task[0][0]
      max_duration = task[0][0]

      num_alternatives = len(task)
      all_alternatives = range(num_alternatives)

      for alt_id in range(1, num_alternatives):
        alt_duration = task[alt_id][0]
        min_duration = min(min_duration, alt_duration)
        max_duration = max(max_duration, alt_duration)

      # Create main interval for the task.
      suffix_name = '_j%i_t%i' % (job_id, task_id)
      start = model.NewIntVar(0, horizon, 'start' + suffix_name)
      duration = model.NewIntVar(min_duration, max_duration,
                                 'duration' + suffix_name)
      end = model.NewIntVar(0, horizon, 'end' + suffix_name)
      interval = model.NewIntervalVar(start, duration, end,
        'interval' + suffix_name)

      # Store the start for the solution.
      starts[(job_id, task_id)] = start

      # Add precedence with previous task in the same job.
      if previous_end:
        model.Add(start >= previous_end)
      previous_end = end

      # Create alternative intervals.
      if num_alternatives > 1:
        l_presences = []
        for alt_id in all_alternatives:
          alt_suffix = '_j%i_t%i_a%i' % (job_id, task_id, alt_id)
          l_presence = model.NewBoolVar('presence' + alt_suffix)
          l_start = model.NewIntVar(0, horizon, 'start' + alt_suffix)
          l_duration = task[alt_id][0]
          l_end = model.NewIntVar(0, horizon, 'end' + alt_suffix)
          l_interval = model.NewOptionalIntervalVar(
              l_start, l_duration, l_end, l_presence, 'interval' + alt_suffix)
          l_presences.append(l_presence)

          # Link the master variables with the local ones.
          model.Add(start == l_start).OnlyEnforceIf(l_presence)
          model.Add(duration == l_duration).OnlyEnforceIf(l_presence)
          model.Add(end == l_end).OnlyEnforceIf(l_presence)

          # Add the local interval to the right machine.
          intervals_per_resources[task[alt_id][1]].append(l_interval)

          # Store the presences for the solution.
          presences[(job_id, task_id, alt_id)] = l_presence

        # Select exactly one presence variable.
        model.Add(sum(l_presences) == 1)
      else:
        intervals_per_resources[task[0][1]].append(interval)
        presences[(job_id, task_id, 0)] = model.NewIntVar(1, 1, '')

    job_ends.append(previous_end)

    # Define duedate for Job
    # Calculate lateness from end of job
    job_suffix = "_%i" % job_id
    rawDueDate = problem.jobs[job_id].dueDate
    dueDate = model.NewIntVar(rawDueDate, rawDueDate, "duedate" + job_suffix)
    overdue = model.NewIntVar(-horizon, horizon, "overdue" + job_suffix)
    # Overdue is equal to the end of the job - Due date
    model.Add(overdue == previous_end - dueDate)
    job_overdues.append(overdue)


  # Create machines constraints.
  for machine_id in all_machines:
    intervals = intervals_per_resources[machine_id]
    if len(intervals) > 1:
      model.AddNoOverlap(intervals)

  # Makespan objective
  if objective == MAKESPAN:
    makespan = model.NewIntVar(0, horizon, 'makespan')
    model.AddMaxEquality(makespan, job_ends)
    model.Minimize(makespan)
  elif objective == LMAX:
    # Lmax Objective
    # TODO should use -maxduedate instead of -horizon
    Lmax = model.NewIntVar(-horizon, horizon, 'Lmax')
    model.AddMaxEquality(Lmax, job_overdues)
    model.Minimize(Lmax)


  # Solve model.
  solver = cp_model.CpSolver()
  solution_printer = SolutionPrinter(verbose=verbose)
  status = solver.SolveWithSolutionObserver(model, solution_printer)

  # Print final solution.
  for job_id in all_jobs:
    if verbose: print('Job %i:' % (job_id))
    for task_id in range(len(jobs[job_id])):
      start_value = solver.Value(starts[(job_id, task_id)])
      overdue_value = solver.Value(job_overdues[job_id])
      machine = -1
      duration = -1
      selected = -1
      for alt_id in range(len(jobs[job_id][task_id])):
        if solver.Value(presences[(job_id, task_id, alt_id)]):
          duration = jobs[job_id][task_id][alt_id][0]
          machine = jobs[job_id][task_id][alt_id][1]
          selected = alt_id
      if verbose:
        print('  task_%i_%i starts at %i (alt %i, machine %s, duration %i) overdue %i' %
            (job_id, task_id, start_value, selected, problem.get_machine(machine), duration, overdue_value))


  if verbose:
    print('Solve status: %s' % solver.StatusName(status))
    print('Optimal objective value: %i' % solver.ObjectiveValue())
    print('Statistics')
    print('  - conflicts : %i' % solver.NumConflicts())
    print('  - branches  : %i' % solver.NumBranches())
    print('  - wall time : %f s' % solver.WallTime())

  return solver.ObjectiveValue()
