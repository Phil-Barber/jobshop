import sys
from load_data import load_data, Problem, Job, Operation, Task
from flexible_job_shop import get_schedule, MAKESPAN, LMAX


def run_test(pos):
  objective = LMAX
  cases = get_test_cases()

  if pos == None:
    for index, case in enumerate(cases):
      result = get_schedule(case['problem'], objective, verbose=False)
      didPass = result == case['expected']
      resultString = ('Passed' if didPass else 'Failed')
      print('Test %i %s!' % (index, resultString))
      if not didPass:
        print('received: %i\texpected: %i' % (result, case['expected']))
        print('Re-runnning verbose:')
        get_schedule(case['problem'], objective, verbose=True)
        doQuit = input("Quit? [y]yes:");
        if doQuit == "y": quit()
  else :
    get_schedule(cases[pos]['problem'], objective, True)


def get_test_cases():
  return [
    {
      'problem': Problem([
        Job("J1", [
          Operation([Task("M1", 400), Task("M2", 300), Task("M3", 400)])
        ], 200)
      ]),
      'expected': 100
    },
    {
      'problem': Problem([
        Job("J1", [
          Operation([Task("M1", 500, 0), Task("M2", 400, 0)])
        ], 800),
        Job("J2", [
          Operation([Task("M1", 400, 1), Task("M2", 300, 1)])
        ], 600),
        Job("J3", [
          Operation([Task("M1", 400, 2), Task("M2", 300, 2)])
        ], 800)
      ]),
      'expected': -200
    },
    {
      'problem': Problem([
        Job("J0", [
          Operation([Task("M1", 500), Task("M2", 400)])
        ], 500),
        Job("J1", [
          Operation([Task("M1", 400), Task("M2", 300)])
        ], 900),
        Job("J2", [
          Operation([Task("M1", 300), Task("M2", 400)])
        ], 1200),
        Job("J3", [
          Operation([Task("M1", 300), Task("M2", 400)])
        ], 1500),
        Job("J4", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 1800),
        Job("J5", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 2100),
        Job("J6", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 2200),
        Job("J7", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 2000),
        Job("J8", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 1800),
        Job("J9", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 1600),
        Job("J10", [
          Operation([Task("M1", 200), Task("M2", 800)])
        ], 1400),
        Job("J11", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 600),
        Job("J12", [
          Operation([Task("M1", 300), Task("M2", 200)])
        ], 400),
        Job("J13", [
          Operation([Task("M1", 200), Task("M2", 200)])
        ], 200)
      ]),
      'expected': 0
    }
  ]



# objective = LMAX
objective = MAKESPAN

if __name__ == "__main__":
    indexes = {
        'name': 0,
        'machine': 1,
        'duration': 2
    }

    file_name = './Production schedule.csv'


    if len(sys.argv) > 1 and sys.argv[1] == '--test':
      pos = None
      if len(sys.argv) == 3:
        pos = int(sys.argv[2])
      run_test(pos)

    else:
        problem = load_data(file_name, indexes)
        # problem.mix_machines()
        get_schedule(problem, objective)

