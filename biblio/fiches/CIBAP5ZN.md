# Desiderata for next generation of ML model serving



## Quote


The article identifie neuf qualités ('desiderata') essentielles pour les frameworks de model serving ML de nouvelle génération : (1) pipelines d'inférence en tant que graphes de flux de données, (2) abstractions de composants de pipeline, (3) support des scénarios synchrones et asynchrones, (4) déploiement transparent vers le cloud et l'edge, (5) expérimentation flexible, (6) monitoring et explicabilité, (7) apprentissage continu et actif, (8) confidentialité des données et conformité, et (9) efficacité des ressources.

Position paper (article de positionnement/opinion) présentant neuf qualités désirables ('desiderata') pour les systèmes de model serving ML de nouvelle génération, organisées autour du principe de data-centricité. Pas de méthodologie expérimentale ou empirique propre; l'article s'appuie sur une revue de la littérature et de l'état de l'art industriel pour argumenter chaque qualité.

Future plans include supporting larger versions of Meal-SAM and allowing annotation at different levels of granularity depending on use cases

Future directions including multimodal AI models integrating clinical data, prospective validation trials, and fine-tuned LLMs for reporting are essential for safe translation into practice.

l'article discute conceptuellement des plateformes de model serving ML et cite des frameworks/outils existants (ex: TensorFlow Serving, KServe, Seldon, etc. référencés génériquement) et des chiffres issus d'autres sources.

the proposed framework is intended as a preliminary computational tool that may support subsequent expert-guided classification and diagnostic evaluation of atypical or transitional cell populations

Hence, the efficiency of the suggested model can be established for multi-class image classification difficulties.

With this position paper we hope to reinforce the importance of research and development on ML inference systems and encourage a debate on the desired requirements for the next generation of tools to successfully deploy and manage powerful predictive pipelines.

Les bibliothèques ML pour le Big Data à grande échelle (ex: Spark MLlib/ML) sont encore dans un état d'évolution jeune

the proposed framework presents superior runtime and development efficiency compared with an existing MLOps framework

The proposed algorithms are robust to different types of data distributions

Future work will regard creating a GUI, the extension of each sub-module with a more extensive set of state-of-the-art data processing techniques, integration of new recognition, regression, transfer learning models, and implementation of new performance metrics.

The proposed collaborative optimization method.

To summarize, the increased explainability of the ML model enables us to: detect and exclude redundant input, detect examples that are rare and generate more data covering such cases, and detect more influential and also less influential input features.

A follow-up paper is desired to verify that the method proposed by this paper works well for a wider variety of chip designs.

Efficient LLM serving is a fundamental step towards democratizing access to advanced AI technologies.

Future research should prioritize adaptive fusion strategies, theory-grounded agent design, and secure, explainable deployments.

Future research should prioritize adaptive fusion strategies, theory-grounded agent design, and secure, explainable deployments.

Machine learning (ML) approaches have emerged as strong tools in the area of TSO in recent years [5].

suitable for integration with real time human-inthe-loop systems


## Synthese


L'objectif de cet article de positionnement est de définir un ensemble structuré de neuf qualités désirables ('desiderata') que les frameworks de model serving ML de prochaine génération devraient viser, en réponse à l'insuffisance perçue des architectures actuelles majoritairement orientées microservices. Le contexte scientifique qui motive cette réflexion est le constat que la phase d'inférence, bien que représentant jusqu'à 90% des ressources de calcul et de l'énergie consommées sur le cycle de vie d'un modèle ML, reste historiquement moins investie en recherche que la phase d'entraînement. Les auteurs formulent implicitement l'hypothèse que la data-centricité, en tant que principe de conception global, permettrait de satisfaire simultanément et de façon cohérente l'ensemble des neuf qualités identifiées, plutôt que de les traiter comme des exigences techniques indépendantes et potentiellement en tension. L'article vise enfin à catalyser un débat communautaire plus large sur l'avenir des systèmes de déploiement de pipelines prédictifs à grande échelle.

Cet article de positionnement (position paper), publié sur arXiv en 2022 par des auteurs non identifiés, s'attaque à une question centrale et encore peu structurée dans la littérature : quelles qualités ('desiderata') les plateformes de model serving ML de prochaine génération devraient-elles viser, et comment la data-centricité peut-elle servir de principe de conception unificateur pour ces systèmes ? Contrairement à un article empirique, ce travail ne repose pas sur une méthodologie expérimentale, une population étudiée ou des données collectées par les auteurs eux-mêmes ; il s'agit d'une synthèse argumentative s'appuyant sur la littérature existante et l'état de l'art industriel (frameworks tels que TensorFlow Serving, KServe, Seldon, cités génériquement). Les auteurs identifient neuf qualités essentielles que devraient présenter les systèmes de model serving de nouvelle génération : (1) la représentation des pipelines d'inférence comme des graphes de flux de données (dataflow graphs), (2) des abstractions de composants de pipeline réutilisables, (3) le support natif des scénarios synchrones et asynchrones, (4) un déploiement transparent entre cloud et edge, (5) une expérimentation flexible (A/B testing, canary deployments, etc.), (6) le monitoring et l'explicabilité des prédictions en production, (7) l'apprentissage continu et actif à partir des données de production, (8) la confidentialité des données et la conformité réglementaire, et (9) l'efficacité des ressources de calcul. Un résultat chiffré central de l'argumentation est que jusqu'à 90% des ressources de calcul ML et jusqu'à 90% de l'énergie consommée sur l'ensemble du cycle de vie d'un modèle sont attribuées à la phase d'inférence plutôt qu'à l'entraînement, ce qui justifie selon les auteurs un investissement accru en recherche sur les systèmes de serving plutôt que sur l'optimisation exclusive de l'entraînement. Les auteurs recommandent le paradigme du flow-based programming (FBP) comme architecture préférable à l'approche orientée microservices, car il refléterait plus fidèlement la nature intrinsèquement centrée sur les données du processus d'inférence. Ils avancent également le multimodel serving avec overcommit de ressources comme une pratique clé permettant de réduire les coûts opérationnels et de simplifier l'exploitation à grande échelle de nombreux modèles simultanément. La data-centricité est proposée comme le modèle de conception global ('overarching design pattern') capable de satisfaire de façon cohérente l'ensemble des neuf qualités identifiées, plutôt que de les traiter comme des exigences indépendantes et potentiellement contradictoires. En conclusion, les auteurs visent à renforcer l'importance de la recherche et du développement sur les systèmes d'inférence ML et à susciter un débat communautaire sur les exigences souhaitables pour les futurs outils de déploiement de pipelines prédictifs. Les limites principales de cet article résident dans son caractère programmatique et non empirique : aucune validation quantitative propre des neuf desiderata n'est fournie, et les chiffres cités (comme le 90% de ressources/énergie consommées par l'inférence) proviennent de sources tierces non détaillées dans les sections disponibles.


## Resultats


Les résultats de cet article de positionnement consistent en l'identification de neuf desiderata pour le model serving ML de nouvelle génération : (1) pipelines d'inférence représentés comme des graphes de flux de données, (2) abstractions de composants de pipeline réutilisables, (3) support des scénarios synchrones et asynchrones, (4) déploiement transparent cloud/edge, (5) expérimentation flexible, (6) monitoring et explicabilité, (7) apprentissage continu et actif, (8) confidentialité des données et conformité réglementaire, et (9) efficacité des ressources de calcul. La donnée quantitative la plus marquante avancée par les auteurs est que jusqu'à 90% des ressources de calcul ML et jusqu'à 90% de l'énergie consommée sur l'ensemble du cycle de vie d'un modèle sont attribuées à la phase d'inférence, ce qui constitue l'argument empirique central justifiant la priorité accordée à l'optimisation du serving. Sur le plan architectural, les auteurs recommandent le paradigme du flow-based programming (FBP) comme alternative préférable à l'orientation microservices, en raison de sa correspondance plus native avec la nature centrée sur les données du processus d'inférence. Enfin, le multimodel serving combiné à une stratégie d'overcommit de ressources est présenté comme une pratique opérationnelle clé permettant de réduire les coûts et de simplifier l'exploitation à grande échelle de nombreux modèles déployés simultanément. Aucune analyse par sous-groupe, aucun intervalle de confiance ni aucune valeur p ne sont rapportés, conformément à la nature non empirique de l'article.


## Insight


novelty: L'article propose un cadre original de neuf qualités ('desiderata') pour structurer la conception des futurs systèmes de model serving ML, unifiées sous le principe de la data-centricité.
La contribution principale de cet article de positionnement réside dans l'identification et la structuration de neuf qualités jugées essentielles pour les frameworks de model serving de nouvelle génération : pipelines comme graphes de flux de données, abstractions de composants, support synchrone/asynchrone, déploiement cloud/edge transparent, expérimentation flexible, monitoring/explicabilité, apprentissage continu et actif, confidentialité/conformité, et efficacité des ressources. Plutôt que de traiter ces neuf axes comme des exigences techniques disjointes, les auteurs les subsument sous un principe de conception unique, la data-centricité, présentée comme le fil conducteur permettant de les réaliser de manière cohérente et non contradictoire. Cette approche se distingue des travaux antérieurs centrés sur des optimisations ponctuelles (latence, throughput) en proposant une vision systémique et architecturale du problème du serving ML à grande échelle.

secondary_outcomes: Les desiderata de monitoring, d'explicabilité et d'apprentissage continu/actif visent à faire du serving un processus dynamique et auto-améliorant plutôt qu'un simple déploiement statique.
Au-delà des aspects purement architecturaux et de performance, l'article accorde une importance particulière aux desiderata n°6 (monitoring et explicabilité) et n°7 (apprentissage continu et actif), qui positionnent le système de serving non pas comme un point terminal statique du cycle de vie ML, mais comme un composant actif capable de surveiller ses propres prédictions, d'expliquer ses décisions, et de s'améliorer continuellement à partir des données de production. Cette vision s'oppose au modèle traditionnel où l'entraînement et le déploiement sont des phases strictement séquentielles et déconnectées. Le desideratum n°8 (confidentialité des données et conformité) complète cette exigence en intégrant les contraintes réglementaires (par exemple RGPD) comme partie intégrante de la conception des pipelines d'inférence, et non comme une contrainte externe ajoutée a posteriori. Ensemble, ces trois desiderata reflètent une conception du serving ML comme système sociotechnique complexe, devant concilier performance technique, transparence et conformité légale.

implications: L'article vise explicitement à susciter un débat communautaire sur les exigences des futurs outils de model serving, plutôt qu'à imposer une solution technique définitive.
La conclusion de l'article, citée textuellement dans la section originale, formule explicitement l'intention des auteurs : renforcer l'importance de la recherche et du développement sur les systèmes d'inférence ML et encourager un débat sur les exigences souhaitées pour la prochaine génération d'outils de déploiement de pipelines prédictifs. Cette posture délibérément ouverte et programmatique distingue l'article des publications techniques classiques visant à démontrer la supériorité d'une solution spécifique. Elle positionne le travail comme un point de départ pour la communauté de recherche en systèmes ML (MLOps, model serving, infrastructure ML), invitant à des contributions futures qui viendraient valider, réfuter ou affiner empiriquement les neuf desiderata proposés. Cette approche est cohérente avec le contexte de 2022, période où le domaine du model serving à grande échelle était encore en pleine structuration, sans consensus établi sur les meilleures pratiques architecturales.


## Discussion


Les auteurs interprètent l'ensemble de leurs neuf desiderata comme pouvant être unifiés sous le principe de la data-centricité, qu'ils présentent comme le modèle de conception global ('overarching design pattern') optimal pour la conception des futurs systèmes de model serving ML. Cette interprétation s'inscrit en comparaison implicite avec les architectures actuelles dominées par l'orientation microservices, jugées moins adaptées à la nature intrinsèquement centrée sur les données du processus d'inférence que le paradigme alternatif du flow-based programming. Sur le plan pratique, les implications concernent directement la conception des futures plateformes MLOps et d'infrastructure ML, notamment via la recommandation du multimodel serving avec overcommit de ressources pour réduire les coûts opérationnels à grande échelle. La limite principale de cette discussion réside dans son caractère programmatique et non validé empiriquement : les auteurs ne fournissent aucune démonstration quantitative comparant la performance effective d'une architecture data-centrique/FBP par rapport aux architectures microservices existantes, laissant cette validation aux travaux futurs que l'article appelle explicitement de ses vœux.


## Methodologie


Il s'agit d'un position paper (article de positionnement/opinion) publié sur arXiv en 2022, dépourvu de méthodologie expérimentale ou empirique propre, de population étudiée, d'échantillon ou de données collectées directement par les auteurs. L'approche méthodologique repose exclusivement sur une revue argumentative de la littérature scientifique et de l'état de l'art industriel du model serving ML, incluant des références génériques à des frameworks existants tels que TensorFlow Serving, KServe et Seldon. Les auteurs structurent leur contribution autour de l'identification de neuf qualités désirables (desiderata), pour chacune desquelles ils présentent un raisonnement justificatif (rationale) et discutent des moyens pratiques permettant de l'atteindre. Aucun outcome primaire ou secondaire au sens statistique n'est défini, puisqu'il n'y a ni intervention testée ni comparaison contrôlée ; l'article ne comporte donc aucune méthode statistique inférentielle. La seule donnée quantitative rapportée (jusqu'à 90% des ressources de calcul et de l'énergie consommée par l'inférence sur le cycle de vie du modèle) est citée comme argument de contexte issu de sources externes non détaillées dans les sections disponibles, sans durée de suivi ni protocole de mesure propre à l'article.


## Conclusion


Le serving efficace des LLMs constitue une étape fondamentale vers la démocratisation de l'accès aux technologies d'IA avancées Cette survey vise à fournir aux chercheurs, praticiens et développeurs une compréhension complète des méthodologies existantes afin de faciliter des décisions éclairées lors du déploiement de LLMs en environnement réel En consolidant les avancées récentes sur les algorithmes et les systèmes, cette étude espère accélérer le progrès et favoriser l'innovation dans la recherche de solutions de serving LLM hautement efficaces

Ce position paper vise à renforcer l'importance de la recherche et du développement sur les systèmes d'inférence ML et à encourager un débat communautaire sur les exigences souhaitées pour la prochaine génération d'outils permettant de déployer et gérer efficacement des pipelines prédictifs puissants. La data-centricité, en tant que principe de conception prioritaire, permettrait de satisfaire simultanément les neuf qualités identifiées (dataflow, abstractions, synchrone/asynchrone, déploiement cloud/edge, expérimentation, monitoring/explicabilité, apprentissage continu, confidentialité/conformité, et efficacité des ressources).