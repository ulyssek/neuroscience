Donc voila mon code ! 

Ca se passe de la facon suivante, tu as des classes Neuron et Synaps, qui constitue le coeur de ton réseau, chacun a tout un tas de variables et de paramètres bien défini. Toutes les constantes dont ils ont besoin. Et ils ont des méthodes run(), qui leur permet de faire ce qu'ils ont a faire (recevoir du courant, spiker, etc...).
Tu as aussi une classe Network, qui elle représente un réseau de neurones. Elle a plein de fonction pour ajouter des neurones, les liés avec des synaps, créer des groupes de neurones, des méthodes de fonctionnement classique (par exemple, le premier groupe recoit un courant constant, ou le deuxieme groupe recoit du bruit, etc...). Elle dispose aussi du méthode run(), qui va appeler les méthodes run() des neurones et synaps associés.
Enfin, le Network a plein de fonctions pour tracer toutes les courbes qu'on pourrait vouloir.

Dernier point, tu as un fichier visual, qui créé un type de Network particulier (par couche), avec certain modes de fonctionnement (Typiquement, les stimulations aléatoires qui permettent de briser la symétrie).

Voila, si tu as des questions, ulysseklatzmann@gmail.com
