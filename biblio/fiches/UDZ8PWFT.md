# APACE: AlphaFold2 and advanced computing as a service for accelerated discovery in biophysics.



## Conclusion


APACE constitue une avancée significative en permettant l'utilisation d'AlphaFold2 à grande échelle sur des infrastructures de supercalcul, rendant la prédiction de structure protéique accessible et rapide pour un large éventail d'utilisateurs L'approche computationnelle d'APACE, combinant parallélisation CPU/GPU via Ray, optimisation I/O et conteneurisation Singularity/Apptainer, permet de réduire le temps de calcul de semaines/jours à quelques minutes sans sacrifier la précision APACE peut être limité pour la prédiction de protéines transmembranaires et/ou de multimères à plusieurs chaînes, une limite héritée du modèle AlphaFold2 original Ce framework computationnel pourrait être directement relié à des laboratoires robotisés pour automatiser et accélérer la découverte scientifique à grande échelle


## Insight


efficacy: APACE permet une réduction drastique du temps de calcul nécessaire à la prédiction de structures protéiques par rapport à AlphaFold2 standard, transformant des délais de plusieurs jours en quelques dizaines de minutes.

efficacy: En parallélisant les trois recherches MSA indépendantes selon une approche inspirée de ParaFold, APACE réduit considérablement le temps de prédiction de structure protéique par rapport à AlphaFold2 standard, avec un gain de performance atteignant jusqu'à deux ordres de grandeur.

infrastructure: Les comparaisons de performance entre APACE et AlphaFold2 ont été réalisées sur deux supercalculateurs de pointe, Delta (NCSA) et Polaris (ALCF), en utilisant à la fois des GPU NVIDIA A100 et A40, avec des temps de prédiction systématiquement plus courts sur les GPU A100.

methodology: Le déploiement d'AlphaFold2 sur les supercalculateurs Delta et Polaris a nécessité de remplacer la compilation locale de HHsuite par une version statiquement compilée compatible AVX2, afin d'éliminer les erreurs d'exécution liées à l'architecture du processeur et d'assurer la portabilité de l'image Singularity.

methodology: L'architecture d'APACE repose sur des clusters Ray déployés dynamiquement sur des nœuds de calcul multi-GPU, permettant l'exécution concurrente des outils MSA sur CPU et des modèles de réseau de neurones ainsi que leur relaxation sur GPU distincts.

efficacy: Le framework proposé offre une efficacité computationnelle comparable ou supérieure aux méthodes concurrentes tout en atteignant une précision accrue de segmentation et de détection.

efficacy: Le déploiement du human-in-the-loop computing est envisagé comme un levier permettant d'améliorer la rapidité et la qualité des résultats obtenus par les utilisateurs cliniques tout en réduisant l'expertise requise, libérant ainsi le temps des experts pour les cas les plus complexes.

efficacy: Les GAN sont rapportés comme utiles à l'augmentation de données, à la segmentation sémantique et à l'amélioration des algorithmes de classification en imagerie médicale.

methodology: Les limitations computationnelles d'AlphaFold2 original incluent un temps d'inférence long, une forte demande en ressources CPU et GPU utilisées séquentiellement, une empreinte mémoire substantielle ainsi qu'une base de données de référence volumineuse d'environ 2,6 To, générant des recherches MSA pouvant durer plusieurs heures.

efficacy: Les performances de calcul de la vraisemblance ont été substantiellement améliorées grâce aux extensions SSE du processeur et à la bibliothèque BEAGLE, qui permet notamment l'exploitation du calcul sur GPU.

future_directions: Les auteurs identifient l'optimisation algorithmique, la collaboration interdisciplinaire, la fusion de données multimodales et la validation clinique extensive comme axes prioritaires pour renforcer l'applicabilité réelle de l'IA en imagerie oncologique.


## Resultats


Trois expériences computationnelles ont été menées afin de comparer les performances d'APACE, une version optimisée d'AlphaFold2, à celles du modèle AlphaFold2 standard, en s'appuyant sur les supercalculateurs Delta (NCSA) et Polaris (ALCF). La première expérience a porté sur la prédiction de structures pour quatre protéines de référence, incluant un monomère (6AWO, transporteur de sérotonine) et trois multimères (6OAN, 7MEZ, 6D6U), en exploitant des clusters Ray déployés sur des GPU NVIDIA A100 et A40 pour paralléliser l'exécution des tâches CPU (recherche MSA) et GPU (inférence du réseau de neurones et relaxation des modèles). Cette architecture permet d'exploiter simultanément l'ensemble des ressources CPU et GPU disponibles sur les nœuds de calcul, contrairement au flux de travail séquentiel d'AlphaFold2 standard. Les résultats démontrent des gains de performance substantiels, avec des accélérations atteignant jusqu'à deux ordres de grandeur, illustrées notamment par la protéine 7MEZ dont le temps de prédiction est réduit de 12,5 jours à 68,2 minutes sur Delta, et de 10,6 jours à 76,9 minutes sur Polaris.


## Synthese


Cette section détaille les adaptations techniques nécessaires au déploiement d'AlphaFold2 sur les supercalculateurs Delta (NCSA) et Polaris (ALCF), qui ne supportent que la conteneurisation Apptainer/Singularity et non Docker. Les auteurs ont notamment remplacé la compilation locale de HHsuite, source d'erreurs d'exécution liées à l'architecture du processeur, par une version statiquement compilée compatible AVX2, améliorant ainsi la portabilité de l'image Singularity. Un script shell personnalisé a également été conçu pour reproduire les fonctionnalités de run_docker.py en environnement Singularity. La section identifie par ailleurs plusieurs limitations computationnelles du modèle AlphaFold2 original — temps d'inférence élevé, forte demande en ressources CPU/GPU, empreinte mémoire importante et base de données volumineuse (2,6 To) — qui motivent le développement de l'approche APACE, inspirée de ParaFold, consistant à paralléliser les trois recherches MSA indépendantes afin d'accélérer l'étape CPU. Trois expériences computationnelles ont été menées afin de comparer les performances d'APACE, une version optimisée d'AlphaFold2, à celles du modèle AlphaFold2 standard, en s'appuyant sur les supercalculateurs Delta (NCSA) et Polaris (ALCF). La première expérience a porté sur la prédiction de structures pour quatre protéines de référence, incluant un monomère (6AWO, transporteur de sérotonine) et trois multimères (6OAN, 7MEZ, 6D6U), en exploitant des clusters Ray déployés sur des GPU NVIDIA A100 et A40 pour paralléliser l'exécution des tâches CPU (recherche MSA) et GPU (inférence du réseau de neurones et relaxation des modèles). Cette architecture permet d'exploiter simultanément l'ensemble des ressources CPU et GPU disponibles sur les nœuds de calcul, contrairement au flux de travail séquentiel d'AlphaFold2 standard. Les résultats démontrent des gains de performance substantiels, avec des accélérations atteignant jusqu'à deux ordres de grandeur, illustrées notamment par la protéine 7MEZ dont le temps de prédiction est réduit de 12,5 jours à 68,2 minutes sur Delta, et de 10,6 jours à 76,9 minutes sur Polaris.

Cette section détaille les adaptations techniques nécessaires au déploiement d'AlphaFold2 sur les supercalculateurs Delta (NCSA) et Polaris (ALCF), qui ne supportent que la conteneurisation Apptainer/Singularity et non Docker. Les auteurs ont notamment remplacé la compilation locale de HHsuite, source d'erreurs d'exécution liées à l'architecture du processeur, par une version statiquement compilée compatible AVX2, améliorant ainsi la portabilité de l'image Singularity. Un script shell personnalisé a également été conçu pour reproduire les fonctionnalités de run_docker.py en environnement Singularity. La section identifie par ailleurs plusieurs limitations computationnelles du modèle AlphaFold2 original — temps d'inférence élevé, forte demande en ressources CPU/GPU, empreinte mémoire importante et base de données volumineuse (2,6 To) — qui motivent le développement de l'approche APACE, inspirée de ParaFold, consistant à paralléliser les trois recherches MSA indépendantes afin d'accélérer l'étape CPU.


## Quote


To expedite the CPU stage, we implemented an approach inspired by ParaFold (13). By orchestrating the three independent sequential MSA searches in parallel, APACE significantly enhances the speed of MSA construction.

the AFPF module can get high-resolution and semantically enhanced fusion feature with attention to improve the prediction accuracy

Advanced algorithms and potentially external tools will be applied further to enhance the scalability and efficiency of information retrieval processes, making them more responsive to user needs [43].

we introduce an open-source, end-to-end automated lesion and feature extraction pipeline (ALFE), that performs preprocessing, registration, segmentation, and feature extraction tasks on MRI scans of adult brains independent of the underlying pathology

In this study, we employed pix2pixHD, an improved version of pix2pix that can deal with high-resolution images (Wang et al., 2018), and finally developed DIC2Cells.

We have presented a pipeline for facade parsing. It relies on the state-of-the-art techniques of computer vision, and acheives on-par results with related research efforts.

This pipeline includes bone extraction (BE), acetabulum and femoral head segmentation (AFS) and active learning based annotation refinement (AAR).

These modules leverage Apache Spark's distributed computing capabilities to process large datasets efficiently while maintaining lineage tracking for all transformations.

Emerging architectures, including transformers and hybrid models, demonstrated adaptability to complex HCC datasets... Bayesian hyperparameter tuning enhancing performance by 1.7% for liver and 5.0% for tumors

DeepPrep offers a computationally efficient, robust and scalable neuroimaging preprocessing pipeline, incorporating recent advancements in deep learning for neuroimaging processing and the workflow manager.

Les calculs de vraisemblance sont significativement accélérés grâce aux extensions SSE et à la bibliothèque BEAGLE (support GPU)

BRIEF proposed adaptive data partitioning and parameter allocation modules. Such modules enable high fidelity at high compression ratios and also allow parallel compression, which can be helpful due to the wide availability of multicore processor and the maturity of multithread programming.

These findings support its feasibility as a clinical decision-support tool and highlight the need for further validation and workflow integration. Further multi-center and prospective validation is warranted.

There is emerging evidence that integrating AI can help address both tasks


## Methodologie


Cette section détaille les adaptations techniques nécessaires au déploiement d'AlphaFold2 sur les supercalculateurs Delta (NCSA) et Polaris (ALCF), qui ne supportent que la conteneurisation Apptainer/Singularity et non Docker. Les auteurs ont notamment remplacé la compilation locale de HHsuite, source d'erreurs d'exécution liées à l'architecture du processeur, par une version statiquement compilée compatible AVX2, améliorant ainsi la portabilité de l'image Singularity. Un script shell personnalisé a également été conçu pour reproduire les fonctionnalités de run_docker.py en environnement Singularity. La section identifie par ailleurs plusieurs limitations computationnelles du modèle AlphaFold2 original — temps d'inférence élevé, forte demande en ressources CPU/GPU, empreinte mémoire importante et base de données volumineuse (2,6 To) — qui motivent le développement de l'approche APACE, inspirée de ParaFold, consistant à paralléliser les trois recherches MSA indépendantes afin d'accélérer l'étape CPU.