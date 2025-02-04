# Problème de la Chasse au Trésor (*en : Treasure Hunt Problem*)

### M1 Informatique (SECIL) - Module Algorithmes Avancés
### Université Toulouse III - Paul Sabatier 
### December 2024

## Table of Contents
1. [Objective](#objective)
2. [Working Folder](#working-folder)
3. [Running the Files](#running-the-files)
   - [Linear Programming Integer Model (PLNE)](#linear-programming-integer-model-plne)
   - [Metaheuristic](#metaheuristic)

---

> **Note** : The project documentation is written in French.

## Objective
The objective of this project is to develop an advanced algorithm to solve the "Treasure Hunt Problem." This problem involves searching for an unknown treasure within a large area, with limited resources and constraints. The goal is to design a solution that efficiently locates the treasure by exploring the environment using various search strategies and techniques.

The project aims to analyze different algorithms, compare their performances, and select the most optimal approach based on factors like time complexity, resource consumption, and the ability to adapt to changing conditions in the search area. It explores real-world applications where such algorithms can be used, such as robotics, navigation systems, or automated exploration tasks.

---

## Working Folder

A working folder has been created :
- [Working Folder [PDF]](./Compte_Rendu.pdf)

---

## Running the Files

### Linear Programming Integer Model (PLNE)

To execute the **PLNE** model, use the following command:

```bash
python3 chasse_tresors_plne.py <file_path> [-MTZ | -DFJ] [-display]
```

- `<file_path>`: Path to the input file containing the instance data.
- `-MTZ`: Specifies the MTZ formulation (default).
- `-DFJ`: Specifies the DFJ formulation.
- `-display`: Optionally display results during execution.

#### Example :
```bash
python3 chasse_tresors_plne.py instances/cat5_175.txt -MTZ -display
```

### Metaheuristic

To execute the **metaheuristic** (tabu search) algorithm, use the following command:

```bash
python3 chasse_tresors_mh.py <file_path> <max_iterations> <size_tabu> [-display]
```

- `<file_path>`: Path to the input file.
- `<max_iterations>`: Maximum number of iterations for the search.
- `<size_tabu>`: Size of the tabu list to avoid revisiting recent solutions.
- `-display`: Optionally display the results during execution.

#### Example :
```bash
python3 chasse_tresors_mh.py instances/cat5_175.txt 100 5 -display
```

---

> ### Note:
> Both scripts (`chasse_tresors_plne.py` and `chasse_tresors_mh.py`) require Python 3 and appropriate libraries.
> The `-display` option can be omitted if you do not want the results to be shown during execution.
