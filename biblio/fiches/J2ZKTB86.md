# MODEL DEPLOYMENT AND SERVING



## Synthese


Ce chapitre de l'ouvrage IIP Series, intitulé « Model Deployment and Serving » et publié en 2026, propose une synthèse narrative et pédagogique consacrée à l'opérationnalisation des modèles de machine learning entraînés en vue de générer des prédictions en temps réel ou en mode batch dans des contextes applicatifs variés. Il ne s'agit pas d'une étude empirique avec population de patients ou de participants humains, mais d'un chapitre conceptuel qui structure la littérature technique existante, notamment en s'appuyant sur les travaux fondateurs de Sculley et al. concernant la dette technique cachée des systèmes de machine learning. L'objectif poursuivi est d'offrir une compréhension exhaustive des paradigmes de déploiement — sur site (on-premise), dans le cloud, en périphérie (edge) et selon des architectures hybrides — ainsi que des méthodes de service telles que les API RESTful, les microservices, la conteneurisation, le calcul serverless et les plateformes de type Model-as-a-Service (MaaS). La méthodologie adoptée est celle d'une revue de synthèse illustrée par une étude de cas conceptuelle portant sur la détection de fraude en ligne, permettant d'ancrer les principes théoriques dans un scénario opérationnel concret. Sur le plan des résultats principaux, le chapitre établit que le déploiement de modèles ne constitue pas un événement ponctuel mais un cycle de vie continu englobant l'entraînement, le packaging, le déploiement en environnement de staging puis de production, le monitoring, la détection de dérive (drift) et le retraining périodique. Trois modes principaux d'inférence sont identifiés et caractérisés selon leurs contraintes de latence et de coût respectives : le traitement batch, le traitement en ligne (temps réel) et le traitement en streaming. Le déploiement en périphérie est présenté comme pertinent lorsque la latence doit être extrêmement faible, lorsque la connectivité réseau est peu fiable, ou lorsque des contraintes réglementaires de confidentialité des données l'imposent, sous réserve d'appliquer des techniques d'optimisation telles que la quantisation, le pruning et la distillation de modèles pour compenser les ressources matérielles limitées des dispositifs edge. L'architecture de service des modèles est décrite comme suivant une trajectoire de maturation organisationnelle typique, passant d'un service monolithique embarqué à un microservice de service de modèle dédié, puis à une architecture fondée sur un magasin de features (feature store) à mesure que l'organisation gagne en maturité technique. Les considérations techniques clés abordées incluent la scalabilité, l'optimisation de la latence, l'équilibrage de charge, la tolérance aux pannes, la sécurité et la protection des données, ainsi que des stratégies de déploiement sécurisées telles que le déploiement bleu-vert (blue-green), les versions canari (canary releases) et les tests A/B. Les limites principales de ce travail résident dans sa nature non empirique — l'absence de données quantitatives originales (pas de valeurs chiffrées, d'intervalles de confiance ou de p-values au sens statistique classique) et son caractère synthétique/pédagogique plutôt que celui d'une recherche primaire testant des hypothèses. Les implications pratiques sont néanmoins substantielles pour les praticiens du MLOps, puisque le chapitre conclut qu'un système ML de niveau production doit impérativement garantir reproductibilité, scalabilité, observabilité et sécurité tout au long d'un cycle de vie itératif et non figé.

Ce chapitre vise à fournir une compréhension exhaustive de la manière dont les modèles de machine learning entraînés sont opérationnalisés pour générer des prédictions en temps réel ou en mode batch dans des contextes applicatifs diversifiés. Il est motivé par le constat, appuyé sur les travaux de Sculley et al. [1], que les systèmes ML accumulent une dette technique cachée liée aux dépendances entre pipelines de données, transformations de features, calendriers de retraining et boucles de rétroaction métier, rendant le déploiement bien plus complexe qu'une simple mise en production ponctuelle. Les hypothèses implicites qui structurent le chapitre sont que le choix du paradigme de déploiement (on-premise, cloud, edge, hybride) et du mode de service (API REST, microservices, conteneurisation, serverless, MaaS) doit être guidé par des contraintes explicites de latence, de coût, de scalabilité et de conformité réglementaire, et que la maturité organisationnelle conditionne la sophistication de l'architecture de service adoptée.


## Quote


The model is also able to perform classification and we apply it for image annotation.

The simulation result showed that the case study based on the proposed model enables effective service coordination in time-sensitive conditions and ensures responsiveness and interoperability.

Introduire des stratégies de blue-green deployment, canary releases, et A/B testing to ensure safe and reliable model updates

A summary of the datasets used for model training and evaluation is provided in Table 1.

The model was trained on the DF2K dataset and verified using the Set5 and Set14 datasets.

The model was trained on the DF2K dataset and verified using the Set5 and Set14 datasets.

This model has been validated as a promising tool to facilitate rapid and precise clinical assessment of component placement.

Model performance could be improved by training on a distribution more similar to the evaluation set, and also by producing multiple samples from a model.

Le résultat de la simulation montre que l'étude de cas basée sur le modèle proposé permet une coordination efficace des services dans des conditions sensibles au temps, garantissant réactivité et interopérabilité

we discussed model limitations, finding significant room for improvement.

The predictions and acquired semantic features of this agent model are subsequently leveraged to generate prompts for the pre-trained model, thereby activating its encoding and decoding capabilities.

The deployment of the proposed model is developed using a personal computer with the following specifications: CPU: Intel(R) Core (TM) i5-10300 H, GPU: Nvidia GTX 1650, RAM: 8 GB, Storage: 500 GB SSD, and Operating System: 64-bit Windows 11.

evaluations of the performance of the proposed approach and comparisons of the model with other stateof-the-art methods is discussed

we identified the problem of wasted computation for models that are trained in these pipelines but not deployed to downstream services. To this end, we proposed and evaluated a solution to pro-actively identify such cases and thus avoid wasting resources without compromising the freshness of actually deployed models.

Le déploiement de modèles de ML n'est pas un événement unique mais un cycle de vie continu incluant l'entraînement, le packaging, le déploiement en staging/production, le monitoring, la détection de dérive et le retraining.

a prototype implementation of the approach is evaluated

We demonstrate the likely path of successful AI deployment with two use cases -(A) A hospital length-of-stay prediction model (operational AI) and (B) An AI-augmented radiology diagnostic tool (clinical AI).

Actions may employing and managing teams of human expert raters.

the measurement methods and benchmarks described are applied to the four selected models and the key results are presented

The model is poised to support ''early recognition, early triage, and early intervention'' at the first emergency/outpatient encounter, offering a practical technical foundation to help reduce adverse outcomes such as chronic lateral ankle instability and post-traumatic osteoarthritis.

Furthermore, we introduced a student-teacher model to stabilize training and increase generalization.

With performance in keypoint identification and parameter prediction comparable to that of senior radiologists, the model demonstrates significant potential as a clinical decision-support tool.

Regular empirical benchmarking and model selection remain crucial.

The results are reported in Table I and Table II, showing our models outperform the other models.

Coordinated sets of smaller, task-specific models can serve as a practical alternative to relying on a single large model.

our model is optimised for regression using an ordinal and numeric distance objective, allowing it to explicitly model the ordered relationships within the data


## Conclusion


Le déploiement et le service de modèles constituent le fondement technique qui transforme les modèles de machine learning en systèmes de décision opérationnels dans le monde réel. Un système ML de niveau production doit garantir reproductibilité, scalabilité, observabilité et sécurité. Le déploiement n'est pas un événement ponctuel mais un cycle de vie continu impliquant monitoring, détection de dérive, retraining et stratégies de déploiement contrôlées. Un modèle n'a une valeur réelle que lorsqu'il fonctionne de manière fiable dans des conditions réelles.


## Insight


primary_outcomes: Le déploiement de modèles ML est présenté comme un cycle de vie continu — entraînement, packaging, déploiement, monitoring, détection de dérive et retraining — plutôt qu'un événement isolé.
Ce résultat conceptuel central reformule le déploiement non comme une étape finale du pipeline ML mais comme un processus itératif et cyclique nécessitant une infrastructure de gouvernance continue. Le chapitre insiste sur le fait que la performance d'un modèle en production tend à se dégrader avec le temps en raison de la dérive des données (data drift) et de la dérive conceptuelle (concept drift), imposant des mécanismes de monitoring permanents et des calendriers de retraining planifiés. Cette perspective s'inscrit directement dans la lignée des travaux de Sculley et al. [1] sur la dette technique cachée des systèmes ML, qui soulignent que les dépendances aux pipelines de données, aux transformations de features et aux boucles de rétroaction métier créent une fragilité systémique invisible dans les métriques de performance ponctuelles.