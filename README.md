# Timetable Maker

NOTE: Created in Python 3.

## Objective

A Python program to solve the lecture scheduling problem. It encodes the input into a propositional logic formula such that there is a schedule if and only if the formula is satisfiable. We further use the [Z3 Theorem Prover](https://github.com/Z3Prover/z3.git) to check whether a valid satisfying assignment exists.

## About the Repository
```
./timetable-maker
├── test_inputs                                 # Contains sample inputs to test the code with
│   └── ...
├── README.md
└── makeTable.py
```

## Frameworks
- [Z3 Theorem Prover](https://github.com/Z3Prover/z3.git)

## Instructions to Run
```
python makeTable.py                             # Run the script using python 3
```

## Inputs
- Schedule Requirements - This file should contain information on: room types, classrooms, courses and timings (refer to [test_inputs](timetable-maker/test_inputs/) for some samples).

## Outputs
```
To the Terminal                                 # Prints a schedule with the information on when and where lectures can be held
