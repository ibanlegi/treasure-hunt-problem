# python3 chasse_tresors_plne.py <file_path> [-MTZ | -DFJ] [-display] (by default : -MTZ)

# python3 chasse_tresors_plne.py data/cat5_500.txt -MTZ
# python3 chasse_tresors_plne.py data/rc201-chasse-tresor-14-25.txt -DFJ

import itertools
from pyscipopt import Model
import sys
import math

# --- Fonctions Utilitaires ---

def lecture_fichier(file_path):
    v = []
    b = 0
    with open(file_path, 'r') as file:
        budget_add = False
        while not budget_add:
            line = file.readline().strip()
            if not(line.startswith('#') or not line):  # Ignore les commentaires et les lignes vides
                b = int(line)
                budget_add = True

        # Lire les informations des villes [id, x, y, value]
        for line in file:  
            line = line.strip()  
            if line.startswith('#') or not line:  
                continue
            ville_info = line.split()
            ville_id = int(ville_info[0])  
            x = int(ville_info[1])         
            y = int(ville_info[2])         
            value = int(ville_info[3])     
            v.append([ville_id, x, y, value])
    
    return v, b

def afficher_graphique(v, sol):
    import matplotlib.pyplot as plt
    # Coordonnées des villes visitées et non visitées
    visited_coords = [(v[i][1], v[i][2]) for i in sol]
    visited_ids = [get_ville_id(v, i) for i in sol]

    all_coords = [(v[i][1], v[i][2]) for i in range(len(v))]

    # Préparer les coordonnées pour l'affichage
    x_all, y_all = zip(*all_coords)
    x_visited, y_visited = zip(*visited_coords)

    # Tracé des villes non visitées en gris clair
    plt.scatter(x_all, y_all, color='lightgray', label='Villes non visitées')

    # Ajouter des annotations pour toutes les villes (non visitées en gris, visitées en bleu)
    for idx, (x, y) in enumerate(all_coords):
        ville_id = get_ville_id(v, idx)
        if ville_id in visited_ids:
            plt.text(x, y, str(ville_id), fontsize=10, color='blue')  # Villes visitées
        else:
            plt.text(x, y, str(ville_id), fontsize=10, color='gray')  # Villes non visitées

    # Tracé des villes visitées en bleu
    plt.plot(x_visited + (0,), y_visited + (0,), 'o-', color='blue', label='Parcours')

    # Légende et affichage
    plt.legend()
    plt.xlabel('Coordonnée X')
    plt.ylabel('Coordonnée Y')
    plt.title('Parcours des villes (villes visitées et non visitées)')
    plt.show()

def distance(p1, p2):
    """Fonction pour calculer la distance euclidienne"""
    return math.sqrt((p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def get_ville_id(v, index):
    """Fonction pour récupérer l'identifiant d'une ville à partir de son index"""
    return v[index][0]

if __name__ == "__main__":
    # Variables
    villes = []     # Liste des points [☺id, x, y, valeur]
    B = 0           # Budget maximal en distance
    N = 0           # Nombre de points

    # Variables par défaut
    MTZ = False
    DFJ = False
    display = False

    # Lecture des arguments
    if len(sys.argv) < 2:
        print(f"Usage: python3 {sys.argv[0]} <file_path> [-MTZ | -DFJ] [-display] (by default: -MTZ)")
        sys.exit(1)

    # Vérification des options supplémentaires
    if "-MTZ" in sys.argv:
        MTZ = True
    elif "-DFJ" in sys.argv:
        DFJ = True
    else:
        MTZ = True

    # Vérification de l'option d'affichage
    if "-display" in sys.argv:
        display = True
                
    # Lecture du fichier
    villes, B = lecture_fichier(sys.argv[1])
    villes.insert(0, [0,0,0,0]) #Ajout de la ville dépôt en début de liste
    N = len(villes)
    # Pré-calcul des distances euclidiennes
    d = [[0.0] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if i != j:
                d[i][j] = distance(villes[i], villes[j])

    # Initialisation du modèle
    M = Model()

    # Dictionnaire de variables binaires x[i,j] : arc entre i et j
    x = {}
    for i in range(N):
        for j in range(N):
            if i != j  and d[i][j] <= B:
                x[i, j] = M.addVar(f"x_{i}_{j}", vtype="B")

    # Dictionnaire de variables binaires : ville k visitée ou non
    y = {}
    for k in range(N):
        y[k] = M.addVar(f"y_{k}", vtype="B")

    if MTZ : 
        # Dictionnaire de variables continues pour interdire les sous-cycles (Variables MTZ)
        u = {}
        for i in range(1, N):
            u[i] = M.addVar(f"u_{i}", vtype="C", lb=0, ub=N-1)

    if DFJ:
        # (Variable DFJ)  
        villes_indices = list(range(1, N))  # Exclure le dépôt (0)

    # Contraintes :

    # 1. Chaque point est visité au plus une fois (liens entrants et sortants)
    for i in range(N):
        M.addCons(sum(x[i, j] for j in range(N) if i != j and (i, j) in x) == y[i])
        M.addCons(sum(x[j, i] for j in range(N) if i != j and (j, i) in x) == y[i])

    # 2. Point de départ et retour au point 0
    M.addCons(sum(x[0, j] for j in range(1, N) if (0, j) in x) == 1)  # Sortie du point 0
    M.addCons(sum(x[j, 0] for j in range(1, N) if (j, 0) in x) == 1)  # Retour au point 0

    # 3. Contrainte de budget (distance totale <= B)
    M.addCons(sum(x[i, j] * d[i][j] for (i, j) in x) <= B)

    # 4. Contraintes pour éliminer les sous-cycles (Contraintes MTZ)
    if MTZ:
        for i in range(1, N):
            for j in range(1, N):
                if i != j:
                    M.addCons(u[i] - u[j] + (N - 1) * x[i, j] <= N - 2)

    # 5. Contraintes pour éliminer les sous-cycles (Contraintes DFJ)
        # Générer tous les sous-ensembles Q de villes (excluant le dépôt) de taille >= 2
    if DFJ:
        for r in range(2, len(villes_indices)+1):
            for Q in itertools.combinations(villes_indices, r):
                # Pour chaque sous-ensemble Q, ajouter la contrainte :
                # somme des x[i,j] pour i,j dans Q, i != j <= |Q| - 1
                M.addCons( sum(x[i, j] for i in Q for j in Q if i != j and (i, j) in x) <= len(Q) - 1)

    # Objectif : Maximiser la valeur totale collectée
    M.setObjective(sum(villes[k][3] * y[k] for k in range(1,N)), "maximize")

    # Lancement du solveur
    print("-----------Exécution du solveur--------")
    M.optimize()
    print("-----------Exécution terminée--------\n")

    # Affichage des résultats
    if M.getStatus() == "optimal":    
        ville_courante = 0
        total_distance = 0.0
        visited = [False] * N
        parcours = [get_ville_id(villes, 0)]  # Pour afficher le chemin sous forme compacte
        solution = [0]

        # Reconstruire le chemin depuis les variables x[i,j]
        while len(parcours) < N and not visited[ville_courante]:
            visited[ville_courante] = True
            next_ville = None
            for j in range(N):
                if ville_courante != j and M.getVal(x[ville_courante, j]) > 0.5:
                    next_ville = j
                    break
            if next_ville is not None:
                total_distance += d[ville_courante][next_ville]
                parcours.append(get_ville_id(villes, next_ville))  # Ajouter l'ID de la ville au parcours
                solution.append(next_ville)
                ville_courante = next_ville

        # Retour au point de départ
        if ville_courante != 0:
            total_distance += d[ville_courante][0]
            parcours.append(get_ville_id(villes, 0))  # Retour au départ
            solution.append(0)
        
        parcours_str = " - ".join(map(str, parcours))

        # Affichage finale
        print(f"Fichier des données :\t\t\t{sys.argv[1]}")
        print(f"Budget disponible :\t\t\t{B}")
        print(f"Nombre de villes disponibles :\t\t{N-1}") #On enlève la ville 0 qui correspond au dépôt
        print(f"Méthode utilisée :\t\t\t{'MTZ' if MTZ else 'DFJ'}")
        print(f"Valeur totale du butin collectée :\t{round(M.getObjVal())}")  
        print(f"Parcours des villes :\t\t\t{parcours_str}")
        print(f"Distance totale parcourue :\t\t{math.ceil(total_distance)}")

        if display:
            afficher_graphique(villes, solution)

    else:
        print("Pas de solution optimale trouvée.")
