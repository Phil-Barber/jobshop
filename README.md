## Job Shop Scheduling
Attempt to codify a solution to the job shop scheduling problem using the 
google or-tools python library 

See for help: https://groups.google.com/forum/#!forum/or-tools-discuss

master branch contains solution to basic problem
0-bound branch contians (failed) attempt at solution to problem with transition 
times


### Glossary
A Problem is a collection of Jobs
Jobs have Operations that need to be done in order
Jobs have DueDates by which all Operations should be completed
Operations have a choice of Tasks - they must choose only one Task per Operation
Tasks represent a processing time on a Machine
Machines can only process one Task at a time

We have two different objectives we could choose to optimise for:
Makespan: The shortest duration for all jobs to complete
Min(LMax): Lmax is the lateness of the most overdue job


