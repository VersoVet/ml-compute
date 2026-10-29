# Ray Core



## Quote


Ray automatically allocates resources and concurrently executes MSA tools on CPUs, model runs, and model relaxation on a distinct GPU.

we developed a new framework based on Ray that allows efficient dynamic scaling of the cluster with negligible resize cost... To enable reproducibility, we open source our distribution tools in [20].

Chaque instance d'environnement Project Chrono est encapsulée dans un acteur Ray (un acteur par instance de simulation), avec un processus pilote central qui diffuse les actions à tous les acteurs et collecte les résultats via ray.get, créant une barrière de synchronisation explicite.

The system implementation was carried out through a predictive algorithm written in Python v.3.7.6 (available for different Operating Systems), using PyTorch v.1.4.0 and Fastai v.1.0.60. We used scikit-learn v.0.22.1 for the neural architecture and Pydicom v.1.4.2 to treat CT images in Dicom format.

Implementation via a predictive algorithm written in Python v.3.7.6, using PyTorch v.1.4.0 and Fastai v.1.0.60, with scikit-learn v.0.22.1 for the neural architecture and Pydicom v.1.4.2 to treat CT images in Dicom format.

Implementation via a predictive algorithm written in Python v.3.7.6, using PyTorch v.1.4.0 and Fastai v.1.0.60, with scikit-learn v.0.22.1 for the neural architecture and Pydicom v.1.4.2 to treat CT images in Dicom format.

Imaging studies were split into commercial tools (n = 13; products: BoneView, RBfracture, Rayvolve, MediAI-FX, SmartUrgence) and researcher-developed (no brand) models (n = 39).

In our system, we use ResNet [29], which has very deep depth and shows very powerful ability of representation, as our recognition architecture.

The ROC curve for the test output is depicted in Fig 4.

Our experiment environment is Intel(R) Core(TM) i7-8700 3.20 GHz with 32 GB of memory.

All experiments were conducted using PyTorch 1.13.1 in Python and executed on a single V100 GPU.

Évaluer la précision diagnostique de trois modèles d'IA différents (BoneView, RBfracture, Rayvolve) sur des images radiographiques de diverses fractures osseuses chez des patients admis au service des urgences de l'hôpital municipal n°4 d'Almaty durant la période 2025-2026.

we designed BASE, a robust AL strategy capable of doing just that

We outperform all baselines, including the latest Axial attention Unet [50], Medical transformer [47], 3P-Seg [37] and MedAdaptorSAM [52] , for both the Dice score and Mean-IoU.

Les trois modèles d'IA (BoneView, RBfracture, Rayvolve) démontrent une haute performance diagnostique pour la détection des fractures osseuses, sans différence statistiquement significative entre eux (sensibilité p = 0.151, spécificité p = 0.708) et un accord inter-modèles très élevé (κ = 0.81, IC95%: 0.77-0.84).

It delivers state-of-the-art performance in both accuracy and runtime.


## Methodologie


Le design retenu est celui d'un framework logiciel open-source combinant Project Chrono (moteur physique multi-corps haute-fidélité) et Ray (calcul distribué), exposé via une interface Gymnasium standardisée; chaque instance de simulation est encapsulée dans un acteur Ray indépendant, orchestré par un processus pilote central assurant la synchronisation via ray.get, avec un hyperparamètre n_s contrôlant la fréquence de communication. L'évaluation repose sur deux études de cas computationnelles sans population humaine ou animale. La première (locomotion quadrupède) entraîne une politique PPO (bibliothèque RSL-RL) de suivi de vitesse commandée, avec observation en R^45, action en R^12 (12 cibles de position articulaire, 3 par jambe), réseaux acteur-critique MLP [512, 256, 128] à activation ELU, comparant n_env ∈ {1, 8, 16}; une expérience de transfert additionnelle affine la politique vers un terrain déformable CRM (taux d'apprentissage 10^-5, clip parameter 0.02, KL désiré 0.001, norme de gradient maximale 0.5, pas de temps interne 5×10^-4 s). La seconde étude de cas (atterrisseur planétaire, système multi-corps à 25 éléments) applique une optimisation bayésienne via Optuna et l'échantillonneur TPE sur trois paramètres de conception θ = {f_y, β, α_2}, minimisant une fonction de coût combinant décélération maximale du centre de masse et fraction d'énergie potentielle dissipée, évaluée sur terrain rigide et terrain déformable CRM selon quatre configurations de parallélisme. Les outcomes primaires sont l'efficacité d'apprentissage/optimisation en temps réel (wall-clock time) et la qualité de la solution obtenue (récompense, erreur de suivi MSE, coût de conception J(θ)), comparés entre niveaux de parallélisme croissants.

L'entraînement du modèle WCAY a été réalisé sur une infrastructure Ubuntu 18.04 dotée d'un processeur Intel Xeon Platinum 8255 C et d'un GPU NVIDIA GeForce RTX 3090, avec PyTorch en version 1.11. Les images d'entrée ont été redimensionnées à une résolution de 640 × 640 pixels, et l'apprentissage s'est déroulé sur 300 époques maximum avec une patience de 50, une taille de batch de 32, un taux d'apprentissage initial de 0,01 et l'optimiseur SGD. Chaque jeu de données a été réparti aléatoirement en trois sous-ensembles selon une proportion approximative de 70 % pour l'entraînement, 20 % pour la validation et 10 % pour le test. Cette configuration expérimentale a ensuite permis d'évaluer par inférence la capacité de généralisation du modèle sur quatre jeux de données distincts, incluant deux corpus radiographiques (FracAtlas, GRAZPEDWRI-DX) et deux corpus non médicaux présentant des similarités visuelles avec les images radiographiques (NEU-DET, SSDD).


## Insight


implementation: Le système repose sur un socle logiciel open-source (Python, PyTorch, Fastai, scikit-learn, Pydicom), rendant l'implémentation reproductible sur différents systèmes d'exploitation et adaptée au traitement d'images CT au format Dicom.

methodology: Un framework distribué basé sur Ray a été développé pour permettre une mise à l'échelle dynamique du cluster de calcul avec un coût de redimensionnement négligeable, et les outils associés ont été rendus open source afin de garantir la reproductibilité des résultats.

novelty: L'étude apporte une comparaison directe et simultanée de trois systèmes d'IA commerciaux distincts face à un même standard de référence humain, rare dans la littérature existante.
L'originalité de cette étude réside dans la comparaison simultanée de trois systèmes d'IA commerciaux différents — BoneView, RBfracture et Rayvolve — au sein d'une même cohorte de patients et face à un même gold standard, permettant une évaluation comparative directe rarement disponible dans la littérature, où les études évaluent le plus souvent un seul système d'IA à la fois. Cette approche méthodologique permet de dégager un consensus robuste sur les forces et faiblesses communes aux architectures actuelles de détection de fracture par apprentissage profond, indépendamment des spécificités propriétaires de chaque solution commerciale, renforçant ainsi la généralisabilité des conclusions sur les limites structurelles de l'IA en radiologie musculo-squelettique.

methodology: L'architecture d'APACE repose sur des clusters Ray déployés dynamiquement sur des nœuds de calcul multi-GPU, permettant l'exécution concurrente des outils MSA sur CPU et des modèles de réseau de neurones ainsi que leur relaxation sur GPU distincts.

objectif: L’étude visait à établir la faisabilité clinique préliminaire d’un nouveau système à arceau et détecteur plan réunissant radiographie numérique directe, fluoroscopie et CBCT, en se concentrant sur les applications potentielles de sa composante CBCT.

methodology: La bibliothèque Cellpose est implémentée en Python 3 avec PyTorch comme framework d'apprentissage profond, complété par NumPy, SciPy, Numba et OpenCV pour le traitement d'image, et PyQt/pyqtgraph pour l'interface graphique interactive.

efficacy: Les trois modèles d'IA testés présentent une performance diagnostique élevée et équivalente entre eux pour la détection de fractures osseuses, sans différence statistiquement significative.
L'étude démontre que BoneView, RBfracture et Rayvolve atteignent des niveaux de performance comparables pour la détection de fractures sur radiographies, avec des AUC s'échelonnant entre 0.90 et 0.93. Aucune différence statistiquement significative n'a été observée entre ces trois modèles, que ce soit en termes de sensibilité (p = 0.151) ou de spécificité (p = 0.708), ce qui suggère une convergence des architectures de réseaux de neurones convolutifs actuellement disponibles sur le marché vers un plafond de performance similaire. Cette équivalence est corroborée par un coefficient d'accord inter-modèles très élevé (κ = 0.81, IC95%: 0.77-0.84), indiquant que les trois systèmes tendent à identifier ou manquer les mêmes cas, plutôt que de se compenser mutuellement en cas d'erreur.


## Resultats


Les résultats démontrent que les trois modèles d'IA (BoneView, RBfracture, Rayvolve) affichent des performances diagnostiques élevées et statistiquement équivalentes entre eux, sans différence significative en sensibilité (p = 0.151) ni en spécificité (p = 0.708), avec un accord inter-modèles très élevé (κ = 0.81, IC95%: 0.77-0.84) et des AUC comprises entre 0.90 et 0.93. Le radiologue expérimenté surpasse néanmoins l'ensemble des modèles d'IA sur toutes les métriques diagnostiques mesurées : sensibilité de 91.5% (IC95%: 0.875-0.945), spécificité de 92.3% (IC95%: 0.890-0.950), exactitude globale de 91.9%, et une AUC de 0.96 (IC95%: 0.94-0.98) contre 0.90-0.93 pour les modèles d'IA. La comparaison directe avec le meilleur modèle d'IA (BoneView) révèle une différence de sensibilité statistiquement significative en faveur du radiologue (p = 0.042), bien que jugée d'importance clinique limitée par les auteurs. L'analyse qualitative des erreurs montre un profil distinct entre l'IA et l'humain : 66 à 70% des faux négatifs de l'IA concernent des fractures subtiles, contre seulement 35% pour le radiologue, tandis que 62% des faux positifs de l'IA résultent d'une confusion avec des variantes anatomiques normales. Ces données convergent pour indiquer que si les performances brutes de l'IA restent élevées et stables entre systèmes, un écart de performance persiste face à l'expertise humaine, particulièrement marqué sur les cas diagnostiques les plus difficiles.


## Synthese


L'entraînement du modèle WCAY a été réalisé sur une infrastructure Ubuntu 18.04 dotée d'un processeur Intel Xeon Platinum 8255 C et d'un GPU NVIDIA GeForce RTX 3090, avec PyTorch en version 1.11. Les images d'entrée ont été redimensionnées à une résolution de 640 × 640 pixels, et l'apprentissage s'est déroulé sur 300 époques maximum avec une patience de 50, une taille de batch de 32, un taux d'apprentissage initial de 0,01 et l'optimiseur SGD. Chaque jeu de données a été réparti aléatoirement en trois sous-ensembles selon une proportion approximative de 70 % pour l'entraînement, 20 % pour la validation et 10 % pour le test. Cette configuration expérimentale a ensuite permis d'évaluer par inférence la capacité de généralisation du modèle sur quatre jeux de données distincts, incluant deux corpus radiographiques (FracAtlas, GRAZPEDWRI-DX) et deux corpus non médicaux présentant des similarités visuelles avec les images radiographiques (NEU-DET, SSDD).

L'entraînement du modèle WCAY a été réalisé sur une infrastructure Ubuntu 18.04 dotée d'un processeur Intel Xeon Platinum 8255 C et d'un GPU NVIDIA GeForce RTX 3090, avec PyTorch en version 1.11. Les images d'entrée ont été redimensionnées à une résolution de 640 × 640 pixels, et l'apprentissage s'est déroulé sur 300 époques maximum avec une patience de 50, une taille de batch de 32, un taux d'apprentissage initial de 0,01 et l'optimiseur SGD. Chaque jeu de données a été réparti aléatoirement en trois sous-ensembles selon une proportion approximative de 70 % pour l'entraînement, 20 % pour la validation et 10 % pour le test. Cette configuration expérimentale a ensuite permis d'évaluer par inférence la capacité de généralisation du modèle sur quatre jeux de données distincts, incluant deux corpus radiographiques (FracAtlas, GRAZPEDWRI-DX) et deux corpus non médicaux présentant des similarités visuelles avec les images radiographiques (NEU-DET, SSDD). Les auteurs évaluent la capacité de généralisation du modèle WCAY en effectuant une inférence de détection non seulement sur les deux jeux de données de fractures radiographiques FracAtlas et GRAZPEDWRI-DX, mais également sur les jeux de données publics NEU-DET et SSDD, choisis pour leur similarité structurelle avec les images radiographiques. Les résultats visualisés montrent que le modèle localise avec précision et une confiance élevée les régions de fracture sur FracAtlas, tandis que sur GRAZPEDWRI-DX il détecte à la fois les fractures et d'autres caractéristiques de troubles squelettiques. Sur les jeux de données NEU-DET et SSDD, qui ne sont pas des images radiographiques, le modèle parvient également à détecter correctement les cibles correspondantes. Ces résultats démontrent que l'algorithme WCAY est capable de détecter des objets présentant des orientations aléatoires et des échelles variées, indépendamment du domaine ou de l'angle des images, ce qui confirme son efficacité et sa capacité de généralisation dans des tâches de détection variées et complexes. Cette conclusion présente WCAY, un nouvel algorithme de détection de fractures sur images radiographiques couvrant plusieurs sites anatomiques. Les auteurs y intègrent le module DSConv pour améliorer le module C2f, aboutissant à un nouvel opérateur central nommé DSC-C2f, ainsi qu'un mécanisme d'attention par canal original (WCA) destiné à mieux capturer les dépendances à longue portée. Les résultats expérimentaux montrent que WCAY dépasse plusieurs méthodes de détection d'objets en temps réel de référence, atteignant un niveau état de l'art sur les métriques de précision, de rappel et de mAP. Le modèle améliore notamment le mAP de 8,8 % sur le jeu de données FracAtlas par rapport au modèle de base pour des tailles de modèle réduites, et de 1,1 % toutes catégories confondues sur GRAZPEDWRI-DX, avec un mAP de 93,9 % pour la catégorie fracture spécifiquement.


## Conclusion


Les trois modèles d'IA commerciaux (BoneView, RBfracture, Rayvolve) possèdent une haute performance diagnostique pour la détection de fractures osseuses sur radiographies, sans différence statistiquement significative entre eux et avec un coefficient d'accord très élevé (κ = 0.81), indiquant la stabilité et la fiabilité des algorithmes d'IA en détection de fractures. Le radiologue expérimenté surpasse néanmoins les modèles d'IA sur l'ensemble des métriques diagnostiques, en particulier en spécificité et en exactitude, son principal avantage résidant dans la détection des fractures subtiles et la différenciation des variantes anatomiques par rapport aux changements pathologiques. L'IA apparaît plus efficace comme outil d'assistance au radiologue que comme système entièrement autonome, en raison de ses limites principales : sensibilité plus faible pour les fractures subtiles, tendance à confondre variantes anatomiques/anciennes lésions avec des fractures, et sensibilité à la mauvaise qualité d'image. Les technologies d'IA ne peuvent pas remplacer complètement les radiologues dans le diagnostic des fractures osseuses, mais peuvent significativement améliorer l'efficacité et la qualité du processus diagnostique lorsqu'elles sont utilisées en collaboration avec eux. Les efforts futurs devraient se concentrer sur l'amélioration de la capacité des algorithmes d'IA à détecter les fractures subtiles et sur le développement de stratégies optimales d'intégration dans les flux de travail cliniques.

Les auteurs concluent que l’intégration de convolutions dilatées multi-échelles et de mécanismes d’attention de canal élargit efficacement le champ réceptif avec un faible surcoût de calcul et améliore la capture ainsi que le recalibrage des caractéristiques micro-pathologiques. Les auteurs concluent que l’ordonnancement dynamique reposant sur un échauffement multi-étapes et un recuit cosinus permet de combiner les pertes MSE et adversariale afin d’équilibrer la précision anatomique au niveau des pixels et la récupération des textures à haute fréquence. Les auteurs affirment que cette stratégie réduit le sur-lissage associé à la MSE tout en évitant les hallucinations structurelles induites par les GAN. Les auteurs concluent que les évaluations sur Bone FD et sur les jeux de données généraux démontrent la fiabilité clinique et la robustesse d’IDCASR-MMF pour des tâches diagnostiques en aval. Les auteurs affirment qu’IDCASR-MMF atteint un compromis perception-distorsion optimal, mais les données quantitatives permettant de vérifier ce caractère optimal ne figurent pas dans le texte fourni. Les travaux futurs viseront à développer des mécanismes adaptatifs intermodaux permettant de transférer l’architecture à d’autres modalités médicales, notamment l’IRM et l’échographie.