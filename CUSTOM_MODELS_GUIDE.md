# Guide : Personnalisation des Modèles 3D (Sim Studio)

Actuellement, le système "Geometry Nodes POC" génère des formes primitives (Cubes, Cylindres) via le code. Voici comment remplacer ces formes par vos propres modèles 3D ultra-détaillés (Trépieds Manfrotto, Têtes Profoto, Softboxes réalistes...).

## 1. Principe de Fonctionnement
Le "Rig" est un objet Maillage vide qui porte un modificateur **Geometry Nodes**. Ce modificateur contient un "Programme" (Node Tree) qui :
1.  Génère/Importe la géométrie du Trépied.
2.  Génère/Importe la géométrie du Projecteur.
3.  Place le tout en fonction des paramètres (Hauteur, Tilt, Pan).

Pour changer le visuel, il suffit de modifier ce "Programme" dans l'éditeur de nœuds.

## 2. Remplacer les Modèles (Pas à Pas)

### Étape A : Préparer vos Modèles
1.  Importez ou modélisez vos objets dans la scène Blender (ex: `Mon_Trepied_HighPoly`, `Ma_Tete_COB`).
2.  Assurez-vous que leur **Origine** (point orange) est logique :
    -   **Trépied** : Origine à la base (0,0,0).
    -   **Tête Projecteur** : Origine au point de pivot (là où elle tourne).
    -   **Diffuseur** : Origine au point d'attache (ring).
3.  (Optionnel) Mettez-les dans une Collection "Assets_Source" et cachez-la.

### Étape B : Ouvrir le Capot
1.  Sélectionnez l'objet **`COB_100W_Rig`**.
2.  Ouvrez une fenêtre **Geometry Node Editor**.
3.  Vous verrez le réseau de nœuds généré par l'addon (`SimStudio_Light_Rig`).

### Étape C : Remplacer le Trépied
1.  Repérez les nœuds **Cylinder** (il y en a deux : base et mât).
2.  Supprimez-les.
3.  Ajoutez un nœud **Object Info** (Shift+A > Input > Object Info).
4.   Sélectionnez votre objet `Mon_Trepied_HighPoly`.
5.  Connectez la sortie **Geometry** de l'Object Info là où le Cylindre était connecté (souvent vers un nœud `Transform Geometry` ou `Join Geometry`).
    -   *Astuce : Si le trépied est en plusieurs parties mobiles (base + mât télescopique), utilisez deux objets distincts et connectez-les aux parties correspondantes du graphe.*

### Étape D : Remplacer la Tête (Projecteur)
1.  Repérez le nœud **Cube** (c'est la tête actuelle).
2.  Remplacez-le par un **Object Info** pointant vers `Ma_Tete_COB`.
3.  Connectez-le au nœud **Transform Geometry** qui gère la rotation (Tilt/Pan).
    -   *Note : Le système de rotation est déjà en place, votre objet tournera automatiquement si vous le connectez au bon endroit !*

### Étape E : Remplacer les Modifiers (Softbox/Cone)
1.  Repérez la zone avec le **Switch** (activé par "Show Diffuser").
2.  Le nœud **Cone** représente le diffuseur actuel.
3.  Remplacez-le par votre modèle de Softbox.

## 3. Automatisation (Pour les Développeurs)

Si vous voulez que ces modèles soient là *par défaut* à chaque nouveau spawn :

### Option 1 : Assets Blender (.blend)
Au lieu de générer des primitives dans `geometry_nodes.py`, le script peut charger un Node Tree pré-fait depuis un fichier `.blend` d'assets.
1.  Créez le Node Tree parfait manuellement (avec Object Info ou Collection Info).
2.  Sauvegardez-le dans `assets/blender_assets.blend`.
3.  Modifiez le code Python pour faire un "Append" de ce Node Tree au lieu de le créer ligne par ligne.

### Option 2 : Code Python (`src/geometry_nodes.py`)
Vous pouvez modifier la fonction `create_light_rig_nodetree()` pour qu'elle utilise des noms d'objets spécifiques s'ils existent dans la scène, ou charger des collections.

```python
# Exemple conceptuel dans le code
def construct_nodes(ng):
    # Au lieu de 'GeometryNodeMeshCube'
    # On cherche un objet existant ou on le charge
    nodes.new('GeometryNodeObjectInfo')
    # ... configuration ...
```

---
*Besoin d'aide pour intégrer un modèle spécifique ? Envoyez-moi le fichier .blend et je peux adapter le générateur !*
