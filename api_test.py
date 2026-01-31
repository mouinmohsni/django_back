# --- Partie 1 : Initialisation et Structure ---

# 1. Initialisation de la Liste
inventaire_produits = []

# 2. Définition des Produits (Dictionnaires)
produit_a = {
    "nom": "Ordinateur Portable",
    "prix": 850.50,
    "quantite": 12,
    "categorie": "Électronique"
}

produit_b = {
    "nom": "Pommes",
    "prix": 2.99,
    "quantite": 50,
    "categorie": "Alimentaire"
}

produit_c = {
    "nom": "Souris Sans Fil",
    "prix": 15.00,
    "quantite": 30,
    "categorie": "Électronique"
}

# 3. Remplissage de l'Inventaire (Liste de Dictionnaires)
inventaire_produits.append(produit_a)
inventaire_produits.append(produit_b)
inventaire_produits.append(produit_c)

# Affichage initial pour vérification
print("Inventaire initial :", inventaire_produits)
print("-" * 30)


# --- Partie 2 : Fonctions d'Analyse ---

# 4. Fonction afficher_inventaire
def afficher_inventaire(inventaire):
    """Affiche les détails de chaque produit dans l'inventaire."""
    print("\n--- Inventaire Actuel ---")
    # Boucle for pour parcourir la liste (chaque 'produit' est un dictionnaire)
    for produit in inventaire:
        # Accès aux valeurs du dictionnaire par leurs clés
        nom = produit["nom"]
        prix = produit["prix"]
        quantite = produit["quantite"]
        categorie = produit["categorie"]

        print(f"Nom: {nom:<20} | Prix: {prix:6.2f} € | Qté: {quantite:3} | Catégorie: {categorie}")
    print("-------------------------")


# 5. Fonction rechercher_par_categorie
def rechercher_par_categorie(inventaire, categorie_recherchee):
    """Retourne une liste des produits appartenant à la catégorie spécifiée."""
    resultats = []

    # Boucle for pour parcourir l'inventaire
    for produit in inventaire:
        # Conditionnelle pour vérifier la catégorie du dictionnaire
        if produit["categorie"] == categorie_recherchee:
            resultats.append(produit)

    return resultats


# 6. Fonction calculer_valeur_totale
def calculer_valeur_totale(inventaire):
    """Calcule la valeur totale de l'inventaire."""
    valeur_totale = 0.0

    # Boucle for pour parcourir l'inventaire
    for produit in inventaire:
        # Calcul de la valeur du stock pour ce produit et ajout à la somme
        valeur_produit = produit["prix"] * produit["quantite"]
        valeur_totale += valeur_produit  # Opérateur d'affectation +=

    return valeur_totale


# --- Partie 3 : Mise à Jour ---

# 7. Fonction mettre_a_jour_prix
def mettre_a_jour_prix(inventaire, nom_produit, nouveau_prix):
    """Met à jour le prix d'un produit spécifique."""
    produit_trouve = False

    # Boucle for pour parcourir l'inventaire
    for produit in inventaire:
        # Conditionnelle pour identifier le produit par son nom
        if produit["nom"] == nom_produit:
            # Mise à jour de la valeur dans le dictionnaire
            produit["prix"] = nouveau_prix
            produit_trouve = True
            print(f"Confirmation : Le prix de '{nom_produit}' a été mis à jour à {nouveau_prix} €.")
            # On peut utiliser 'break' ici pour optimiser la sortie de la boucle
            break

    if not produit_trouve:
        print(f"Erreur : Le produit '{nom_produit}' n'a pas été trouvé dans l'inventaire.")


# --- Exécution des Fonctions pour Test ---

# Affichage de l'inventaire
afficher_inventaire(inventaire_produits)

# Recherche par catégorie
electronique = rechercher_par_categorie(inventaire_produits, "Électronique")
print("\nProduits Électroniques trouvés :", len(electronique))
afficher_inventaire(electronique)

# Calcul de la valeur totale
valeur = calculer_valeur_totale(inventaire_produits)
print(f"\nValeur totale de l'inventaire : {valeur:.2f} €")

# Mise à jour du prix
mettre_a_jour_prix(inventaire_produits, "Ordinateur Portable", 799.99)

# Vérification après mise à jour
afficher_inventaire(inventaire_produits)
valeur_apres_maj = calculer_valeur_totale(inventaire_produits)
print(f"Nouvelle valeur totale de l'inventaire : {valeur_apres_maj:.2f} €")