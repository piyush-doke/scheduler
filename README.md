# Scheduler

NOTE: Created in Python 3.

## Description

A Python program to solve the lecture scheduling problem. It encodes the input into a propositional logic formula such that there is a schedule if and only if the formula is satisfiable. The [Z3 theorem prover](https://github.com/Z3Prover/z3.git) is further used to check whether a valid satisfying assignment exists.

## Frameworks/Tools
- [Z3 Theorem Prover](https://github.com/Z3Prover/z3.git)

## Repository Tree
```
./timetable-maker
├── test_inputs                                 # Contains sample inputs to test the code with
│   └── ...
├── README.md
└── makeTable.py                                # Script to run
```

## Usage

### How to Execute
```
python makeTable.py                             # Run the script using Python 3
```

### Inputs
- Schedule Requirements - This file should contain information on: room types, classrooms, courses and timings (refer to [test_inputs](/test_inputs) for some samples).

### Outputs

- Prints a schedule to the terminal containing information on when and where lectures can be held.
