# Scalable transcriptomics analysis with Dask: applications in data science and machine learning.



## Insight


scalability: Dask clone les API des bibliothèques scientifiques Python couramment utilisées, ce qui facilite une adoption rapide et permet un calcul multi-cœur et hors mémoire (out-of-core) pour l'analyse de données transcriptomiques à grande échelle.

methodology: Le protocole expérimental compare Dask et SPE sur deux cas d'usage transcriptomiques (prédiction de phénotype à partir de données bulk et prétraitement de données single-cell RNA-seq), avec un code source intégralement publié pour assurer la reproductibilité des résultats.

methodology: Les auteurs comparent les frameworks Dask et SPE sur un pipeline ML de bout en bout pour la prédiction de phénotype à partir de données transcriptomiques bulk (cancer et synthétiques) ainsi que sur le prétraitement de données single-cell RNA-seq, dans des conditions matérielles contrôlées sur une seule machine.

accessibility: En rendant les méthodes de machine learning accessibles sans expertise technique poussée, CancerDiscover ouvre la voie à des applications diversifiées telles que l'identification de biomarqueurs, la prédiction de réponse aux traitements et la classification tissulaire, y compris pour des cohortes de taille modeste.

implications: Le système proposé répond à un enjeu de scalabilité jugé crucial dans un contexte de croissance massive des données d'imagerie médicale, et les auteurs envisagent d'intégrer les connaissances de l'utilisateur pour automatiser davantage le processus.

scalability: L'outil Distributed-CellProfiler permet un traitement d'images à grande échelle en parallélisant les analyses sur des ressources de calcul cloud AWS.

scalability: La plateforme démontre sa scalabilité en traitant des jeux de données allant de moins de 100 points à plus de 10 000 enregistrements, validée sur des domaines aussi variés que la macroéconomie, l'éducation, l'environnement, la physiologie végétale, l'industrie, l'automobile, les sciences sociales et la foresterie.

methodology: Un outil de segmentation adapté aux données 3D de microscopie à grande échelle devrait réunir des propriétés d'utilisabilité, de scalabilité vers des jeux de données de taille pétaoctet, d'interactivité avec d'autres logiciels, de polyvalence, d'organisation des objets labellisés, de visualisation flexible, de prise en charge de l'automatisation et de contrôle de la confidentialité des données.

implications: Le caractère générique et extensible du bloc transformer adaptatif au domaine (DAT) suggère des applications potentielles au-delà de la détection de repères médicaux, à toute tâche d'adaptation de domaine utilisant des architectures transformer.
Au-delà de la performance quantitative démontrée sur trois anatomies radiographiques, l'implication méthodologique la plus significative de ce travail réside dans la généralisabilité annoncée du bloc DAT, explicitement conçu pour être compatible avec tout autre réseau transformer et toute autre tâche nécessitant une adaptation de domaine. Cette caractéristique ouvre la voie à une réutilisation du module dans d'autres contextes d'imagerie médicale multi-source (IRM, échographie, scanner) ou même dans des domaines applicatifs hors imagerie médicale où la mutualisation de connaissances entre domaines hétérogènes constitue un enjeu, tout en conservant une spécialisation par domaine via les paramètres adaptatifs dédiés.

context: L'essor de projets de caractérisation moléculaire à grande échelle (GTEx, TCGA, Geuvadis, ENCODE, Roadmap Epigenomics) portant sur des centaines d'individus et des milliers de cellules uniques a généré des volumes de données transcriptomiques dont l'analyse par machine learning requiert des ressources de calcul haute performance pas toujours accessibles.

efficacy: Les GAN sont rapportés comme utiles à l'augmentation de données, à la segmentation sémantique et à l'amélioration des algorithmes de classification en imagerie médicale.

generalizability: Bien que développé et validé pour l'analyse d'images, ce pipeline d'automatisation reposant sur le deep learning et les technologies de virtualisation n'est pas spécifique aux données visuelles et pourrait s'appliquer à d'autres modalités de données biomédicales, comme les données de spectrométrie de masse ou de séquençage d'ADN.


## Conclusion


Dask est un outil flexible et polyvalent, utilisable seul ou en support d'autres frameworks, facilitant l'analyse de données à grande échelle grâce à des fonctionnalités de calcul multi-cœur et out-of-core En clonant l'API de bibliothèques Python scientifiques couramment utilisées, Dask permet une adoption rapide et transparente Bien que l'étude se soit concentrée sur les méthodes de shallow learning, Dask peut aussi s'interfacer avec des bibliothèques Python de Deep Learning À travers plusieurs exemples d'application, Dask peut améliorer la performance de l'analyse de données transcriptomiques et étendre le calcul au-delà des limites habituelles Les frameworks comme Dask deviendront un élément essentiel de la boîte à outils du data scientist computationnel, allégeant le fardeau de l'implémentation technique La dimensionnalité du dataset et la complexité de l'apprentissage sont les deux déterminants majeurs de la configuration de l'analyse Il existe des scénarios différents où SPE et Dask peuvent être appliqués pour surmonter des limitations et améliorer la performance des modèles ML selon la taille des données et l'optimisation d'hyper-paramètres


## Discussion


La discussion identifie la dimensionnalité du jeu de données et la complexité d'apprentissage comme déterminants majeurs du choix d'une stratégie de calcul, distinguant trois scénarios de taille de données (mémoire suffisante, mémoire étendue par disque, ou dépassement des capacités d'une seule machine) pour lesquels Dask ou des moteurs standards (SPE) peuvent être combinés de manière flexible, y compris via un prétraitement Dask suivi d'un passage à SPE lorsque les données réduites tiennent en mémoire. La conclusion resitue ces résultats dans le contexte de l'explosion des données transcriptomiques issues de cohortes et de projets à grande échelle (GTEx, TCGA, Geuvadis, ENCODE, Roadmap Epigenomics), qui rend le machine learning indispensable mais gourmand en ressources de calcul haute performance souvent indisponibles. Dask est présenté comme un outil flexible, capable de calcul multi-cœur et hors mémoire, dont la compatibilité API avec les bibliothèques scientifiques Python classiques facilite son adoption, y compris en interface avec des bibliothèques de deep learning. Les auteurs concluent que des frameworks comme Dask permettront de démocratiser l'analyse de données transcriptomiques à grande échelle en allégeant la charge d'implémentation technique.


## Quote


It facilitates scalable data analysis with multi-core and out-of-core computation functionalities. By cloning the API of commonly used scientific Python libraries, Dask makes its adoption rapid and seamless.

we benchmark and compare the performance of the Dask and SPE frameworks in two scenarios: (i) an end-to-end ML pipeline for phenotype prediction from cancer and synthetic bulk transcriptomic data, with and without hyper-parameter optimization; (ii) in the preprocessing single-cell RNA-seq data.

Le benchmark compare les performances des frameworks Dask et SPE dans deux scénarios : un pipeline ML de bout en bout pour la prédiction de phénotype à partir de données transcriptomiques bulk (cancer et synthétiques), avec et sans optimisation des hyperparamètres, et le prétraitement de données single-cell RNA-seq.

The source code for processing the data and performing all analyses can be found at: https://github.com/martaccmoreno/gexp-ml-dask.

L'étude de cas Dask sur AWS EMR démontre concrètement que les charges de travail ML distribuées peuvent être optimisées pour réduire significativement temps et coût tout en maintenant, voire améliorant, la précision du modèle

For future work, we are investigating scalability issues when applying our techniques to large databases.

This paradigm now supports diverse workflows including RNAseq processing, gene-set interpretation, protein and structure analysis, spatial-omics annotation, and drug-design loops

This performance benefits from DIT-RMHSE, which models semantic information in textual descriptions such as "quantity" and "location," thereby guiding the recognition of small targets.

Researchers who might have hundreds of samples can now utilize machine learning tools for diverse projects, including biomarker identification, drug response, and tissue classification without extensive technical knowledge, while retaining significant flexibility.

Ce dataset soutient de multiples applications: validation des workflows RECIST automatisés, radiomique, étude de la relation volume-diamètre, benchmarking de modèles de segmentation IA, et développement de modèles de fondation médicaux comme MedSAM

The automated annotation... allows flexible adaption of neural networks to specific experimental datasets.

The system we have proposed offers interesting annotation results while meeting the criterion of scalability is a very crucial point in a context where the mass of data is very important.


## Resultats


Cette section présente une évaluation comparative des performances des frameworks Dask et SPE (Single Program Execution / approche non distribuée) sur deux cas d'usage représentatifs de l'analyse transcriptomique à grande échelle. Le premier scénario concerne un pipeline d'apprentissage automatique complet pour la prédiction de phénotype à partir de données de transcriptomique bulk, issues à la fois de jeux de données sur le cancer et de données synthétiques, évalué avec et sans étape d'optimisation des hyperparamètres. Le second scénario porte sur le prétraitement de données de RNA-seq en cellule unique (single-cell RNA-seq). L'ensemble des tests a été réalisé sur une machine unique (Ubuntu 20.04.2 LTS, 16 Go de RAM, processeur multi-cœur à huit threads, SSD de 500 Go), et Dask a été déployé via son ordonnanceur Distributed selon deux configurations distinctes afin d'isoler l'effet du parallélisme par threads de celui par processus : Distributed Threads (DT), avec un unique worker ayant accès aux huit threads, et Distributed Processes (DP), avec quatre workers disposant chacun de deux threads.


## Synthese


Cette section méthodologique précise que l'ensemble du code source utilisé pour le traitement des données et la conduite des analyses est mis à disposition publiquement sur un dépôt GitHub dédié, garantissant ainsi la reproductibilité du benchmark. L'étude compare les performances des frameworks Dask et SPE (Single Point Execution, ou infrastructure de référence non distribuée) selon deux scénarios applicatifs distincts : un pipeline d'apprentissage automatique de bout en bout visant la prédiction de phénotype à partir de données transcriptomiques bulk (issues de jeux de données oncologiques et synthétiques), et une tâche de prétraitement de données de séquençage ARN en cellule unique (single-cell RNA-seq). Le premier scénario est évalué à la fois avec et sans étape d'optimisation des hyperparamètres, afin d'examiner l'impact de cette dernière sur les performances comparatives des deux frameworks. Par ailleurs, deux configurations de déploiement de Dask Distributed sont testées, désignées DT et DP, permettant de dissocier l'effet du parallélisme par threads de celui du parallélisme par processus sur les performances observées. Cette section présente une évaluation comparative des performances des frameworks Dask et SPE (Single Program Execution / approche non distribuée) sur deux cas d'usage représentatifs de l'analyse transcriptomique à grande échelle. Le premier scénario concerne un pipeline d'apprentissage automatique complet pour la prédiction de phénotype à partir de données de transcriptomique bulk, issues à la fois de jeux de données sur le cancer et de données synthétiques, évalué avec et sans étape d'optimisation des hyperparamètres. Le second scénario porte sur le prétraitement de données de RNA-seq en cellule unique (single-cell RNA-seq). L'ensemble des tests a été réalisé sur une machine unique (Ubuntu 20.04.2 LTS, 16 Go de RAM, processeur multi-cœur à huit threads, SSD de 500 Go), et Dask a été déployé via son ordonnanceur Distributed selon deux configurations distinctes afin d'isoler l'effet du parallélisme par threads de celui par processus : Distributed Threads (DT), avec un unique worker ayant accès aux huit threads, et Distributed Processes (DP), avec quatre workers disposant chacun de deux threads. La discussion identifie la dimensionnalité du jeu de données et la complexité d'apprentissage comme déterminants majeurs du choix d'une stratégie de calcul, distinguant trois scénarios de taille de données (mémoire suffisante, mémoire étendue par disque, ou dépassement des capacités d'une seule machine) pour lesquels Dask ou des moteurs standards (SPE) peuvent être combinés de manière flexible, y compris via un prétraitement Dask suivi d'un passage à SPE lorsque les données réduites tiennent en mémoire. La conclusion resitue ces résultats dans le contexte de l'explosion des données transcriptomiques issues de cohortes et de projets à grande échelle (GTEx, TCGA, Geuvadis, ENCODE, Roadmap Epigenomics), qui rend le machine learning indispensable mais gourmand en ressources de calcul haute performance souvent indisponibles. Dask est présenté comme un outil flexible, capable de calcul multi-cœur et hors mémoire, dont la compatibilité API avec les bibliothèques scientifiques Python classiques facilite son adoption, y compris en interface avec des bibliothèques de deep learning. Les auteurs concluent que des frameworks comme Dask permettront de démocratiser l'analyse de données transcriptomiques à grande échelle en allégeant la charge d'implémentation technique.

Cette section méthodologique précise que l'ensemble du code source utilisé pour le traitement des données et la conduite des analyses est mis à disposition publiquement sur un dépôt GitHub dédié, garantissant ainsi la reproductibilité du benchmark. L'étude compare les performances des frameworks Dask et SPE (Single Point Execution, ou infrastructure de référence non distribuée) selon deux scénarios applicatifs distincts : un pipeline d'apprentissage automatique de bout en bout visant la prédiction de phénotype à partir de données transcriptomiques bulk (issues de jeux de données oncologiques et synthétiques), et une tâche de prétraitement de données de séquençage ARN en cellule unique (single-cell RNA-seq). Le premier scénario est évalué à la fois avec et sans étape d'optimisation des hyperparamètres, afin d'examiner l'impact de cette dernière sur les performances comparatives des deux frameworks. Par ailleurs, deux configurations de déploiement de Dask Distributed sont testées, désignées DT et DP, permettant de dissocier l'effet du parallélisme par threads de celui du parallélisme par processus sur les performances observées.


## Methodologie


Cette section méthodologique précise que l'ensemble du code source utilisé pour le traitement des données et la conduite des analyses est mis à disposition publiquement sur un dépôt GitHub dédié, garantissant ainsi la reproductibilité du benchmark. L'étude compare les performances des frameworks Dask et SPE (Single Point Execution, ou infrastructure de référence non distribuée) selon deux scénarios applicatifs distincts : un pipeline d'apprentissage automatique de bout en bout visant la prédiction de phénotype à partir de données transcriptomiques bulk (issues de jeux de données oncologiques et synthétiques), et une tâche de prétraitement de données de séquençage ARN en cellule unique (single-cell RNA-seq). Le premier scénario est évalué à la fois avec et sans étape d'optimisation des hyperparamètres, afin d'examiner l'impact de cette dernière sur les performances comparatives des deux frameworks. Par ailleurs, deux configurations de déploiement de Dask Distributed sont testées, désignées DT et DP, permettant de dissocier l'effet du parallélisme par threads de celui du parallélisme par processus sur les performances observées.