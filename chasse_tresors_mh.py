# python3 chasse_tresors_mh.py <file_path> <max_iteration> <size_tabu> [-display]

# python3 chasse_tresors_mh.py data/cat5_175.txt 100 5
# python3 chasse_tresors_mh.py data/rc201-chasse-tresor-14-25.txt 500 10

import random
import sys
import math
import time

# --- Fonctions Utilitaires ---

def lecture_fichier(file_path):
    v = []
    b = 0  # Budget par défaut
    with open(file_path, 'r') as file:
        budget_add = False
        while not budget_add:
            line = file.readline().strip()
            if not(line.startswith('#') or not line):  # Ignorer commentaires et lignes vides
                b = int(line)  # Lire le budget
                budget_add = True

        # Lire les informations des villes
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

def calculer_cout(solution, villes):
    """Calcul du coût total du trajet d'une solution"""
    cout = 0
    dernier_point = [0, 0, 0, 0]  # Point de départ
    for ville_id in solution:
        ville = villes[ville_id]
        cout += distance(dernier_point, ville)
        dernier_point = ville
    cout += distance(dernier_point, [0, 0, 0, 0])  # Retour au dépôt
    return cout

def calculer_valeur(solution, villes):
    """Calcul de la valeur totale des butins récupérés"""
    return sum(villes[ville_id][3] for ville_id in solution)

def greedy(villes, B, N):
    """Algorithme greedy pour générer une solution initiale"""
    reste = list(range(1, N))  # Exclure le dépôt
    solution = []
    while reste:
        i = random.choice(reste)
        reste.remove(i)
        meilleure_position = None
        meilleur_cout = float('inf')
        for j in range(len(solution) + 1):
            nouvelle_solution = solution[:j] + [i] + solution[j:]
            cout = calculer_cout(nouvelle_solution, villes)
            if cout <= B and cout < meilleur_cout:
                meilleur_cout = cout
                meilleure_position = j
        if meilleure_position is not None:
            solution.insert(meilleure_position, i)
    return solution

def ajouter_point(solution, villes, B, N, liste_tabou):
    """Ajouter un point à la solution."""
    reste = [i for i in range(1, N) if i not in solution and i not in liste_tabou]
    if reste:
        i = random.choice(reste)
        meilleure_position = None
        meilleur_cout = float('inf')
        for j in range(len(solution) + 1):
            nouvelle_solution = solution[:j] + [i] + solution[j:]
            cout = calculer_cout(nouvelle_solution, villes)
            if cout <= B and cout < meilleur_cout:
                meilleur_cout = cout
                meilleure_position = j
        if meilleure_position is not None:
            solution.insert(meilleure_position, i)
            liste_tabou.append(i)
    return solution

def supprimer_point(solution, villes, B, N, liste_tabou):
    """Supprimer un point de la solution."""
    if len(solution) > 1:
        i = random.choice(solution)
        if i not in liste_tabou:
            solution.remove(i)
            liste_tabou.append(i)
    return solution

def echanger_point(solution, villes, B, N, liste_tabou):
    """Échanger un point dans la solution avec un point non utilisé."""
    reste = [i for i in range(1, N) if i not in solution and i not in liste_tabou]
    if len(solution) > 1 and reste:
        i = random.choice(solution)
        j = random.choice(reste)
        nouvelle_solution = solution[:]
        nouvelle_solution[solution.index(i)] = j
        cout = calculer_cout(nouvelle_solution, villes)
        if cout <= B:
            liste_tabou.append(i)
            liste_tabou.append(j)
            return nouvelle_solution
    return solution

def voisinage(solution, villes, B, liste_tabou):
    """Trouve un voisin en appliquant une des opérations : ajouter, supprimer ou échanger."""
    operations = [ajouter_point, supprimer_point, echanger_point]
    random.shuffle(operations)
    for operation in operations:
        nouvelle_solution = operation(solution[:], villes, B, N, liste_tabou)
        if nouvelle_solution != solution:  # Vérifier si la solution a changé
            return nouvelle_solution
    return solution

def recherche_tabou(villes, B, N, max_iterations, taille_tabou):
    """Recherche avec liste tabou pour maximiser la valeur"""
    solution = greedy(villes, B, N)
    meilleure_solution = solution[:]
    meilleure_valeur = calculer_valeur(solution, villes)
    liste_tabou = []
    for _ in range(max_iterations):
        solution = voisinage(solution, villes, B, liste_tabou)
        valeur = calculer_valeur(solution, villes)
        if valeur > meilleure_valeur:
            meilleure_solution = solution[:]
            meilleure_valeur = valeur
        if len(liste_tabou) > taille_tabou:
            liste_tabou.pop(0)
    return meilleure_solution, meilleure_valeur

if __name__ == "__main__":
    #Lecture des arguments
    if len(sys.argv) < 4:
        print(f"Usage: python3 {sys.argv[0]} <file_path> <max_iteration> <size_tabu> [-display]")
        sys.exit(1)

    #Variables avec lecture du fichier
    file_path = sys.argv[1]
    villes, B = lecture_fichier(file_path)
    villes.insert(0, [0, 0, 0, 0])  # Ajouter le dépôt
    N = len(villes)
    display = False
    
    # Vérification de l'option d'affichage
    if "-display" in sys.argv:
        display = True

    # Mesure du temps de début
    temps_debut = time.time()

    # Lancement de la recherche
    solution, valeur = recherche_tabou(villes, B, N, max_iterations=int(sys.argv[2]), taille_tabou=int(sys.argv[3]))
    cout = calculer_cout(solution, villes)

    # Mesure du temps de fin
    temps_fin = time.time()
    temps_total = temps_fin - temps_debut

    #Affichage des résultats

    #Ajout pour l'affichage de la position du dépôt en début et fin de la solution
    solution.insert(0, 0)
    solution.append(0)

    parcours_str = " - ".join(map(lambda id_ville: str(get_ville_id(villes, id_ville)), solution))

    # Affichage finale
    print(f"Fichier des données :\t\t\t{sys.argv[1]}")
    print(f"Budget disponible :\t\t\t{B}")
    print(f"Nombre de villes disponibles :\t\t{N-1}") #On enlève la ville 0 qui correspond au dépôt
    print(f"Nombre maximum d'itération :\t\t{sys.argv[2]}")
    print(f"Taille de la liste tabou :\t\t{sys.argv[3]}")
    print(f"Temps calcul :\t\t\t\t{temps_total} s.")
    print(f"Valeur totale du butin collectée :\t{round(valeur)}")  
    print(f"Parcours des villes :\t\t\t{parcours_str}")
    print(f"Distance totale parcourue :\t\t{round(cout)}")

    if display:
        afficher_graphique(villes, solution)
