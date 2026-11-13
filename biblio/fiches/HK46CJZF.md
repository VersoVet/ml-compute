# Serverless data pipeline architecture supporting distributed machine learning on fog devices



## Resume


Serverless data pipeline architecture supporting distributed machine learning on fog devices

Adaptive Federated Data Science & MLOps Architecture: A Comprehensive Framework for Distributed Machine Learning Systems

A modular framework for mission-critical services in fog-based remote healthcare systems: identification, categorization, and evaluation.

An advanced data fabric architecture leveraging homomorphic encryption and federated learning

Composable machine learning pipeline for fast deployment with neural architecture search

Deploying neural networks in real-time, low-latency, and power-constrained environments, such as high-speed imaging systems, requires efficient hardware-aware machine learning workflows. This thesis presents a composable framework designed to automate and accelerate the design, evaluation, and deployment of optimized neural network models for FPGA-based inference. The architecture is implemented using a modular, containerized approach, where each stage of the machine learning lifecycle is encapsulated within dedicated Docker containers. These are orchestrated using Kubernetes, supporting horizontal scalability and efficient parallel experimentation across diverse environments. The pipeline integrates QKeras for model pruning and precision tuning, HLS4ML for high-level synthesis (HLS), and Vivado for hardware compilation and resource reporting. The system aims to minimize latency and power consumption while maintaining accuracy, making it ideal for real-time applications. A specific use

Nightcore: efficient and scalable serverless computing for latency-sensitive, interactive microservices


## Insight


methodology: Le framework proposé repose sur une intégration de pipelines de données, d'architectures de calcul (GPU/TPU/FPGA), de model serving, d'entraînement distribué, de federated learning et de serverless AI pour soutenir des applications d'IA à grande échelle.

efficacy: Le modèle hybride proposé, s'appuyant sur une architecture distribuée combinant fog et cloud computing, permet de réduire la latence des communications, ce qui souligne l'importance de telles architectures pour garantir des soins d'urgence rapides et fiables.

study_design: Les expérimentations en apprentissage fédéré ont été conduites avec dix nœuds fog clients (K=10), sous l'hypothèse de distribution indépendante et identiquement distribuée (IID) des données entre les clients.

methodology: L'architecture proposée combine chiffrement homomorphe partiel et apprentissage fédéré au sein d'une data fabric distribuée afin d'entraîner des modèles de deep learning sur des données médicales sensibles sans les déplacer vers un dépôt centralisé, garantissant ainsi l'intégrité des données et la confidentialité durant l'apprentissage décentralisé.


## Quote


Expérimentations en apprentissage fédéré menées avec K = 10 nœuds fog clients, sous l'hypothèse de données Indépendantes et Identiquement Distribuées (IID) entre les clients

Our experiments involved a relatively small number of fog nodes ( clients K = 10)... Our current implementation assumes Independent and Identically Distributed (IID) data across clients.

Framework LightPersML : architecture edge-based intégrant apprentissage fédéré (federated learning) pour le traitement distribué des données, orchestration via AWS Step Functions et API Gateway, distillation de connaissances (knowledge distillation) pour compresser les modèles, techniques de confidentialité différentielle (differential privacy), chiffrement homomorphique, et mécanismes de sécurité edge

This research demonstrates an advanced data fabric architecture that enables data fusion, integration, and model parameters sharing framework to apply machine learning models without moving the data to a centralized repository.

The decoupled design of the pipeline allows for registration, image processing, and AI segmentation tools to be readily substituted without changing the business logic

This paper proposed an enhanced system design framework for AI engineering, enabling scalable, reliable, and ethical AI applications. By integrating advanced data pipelines, distributed training, hybrid cloud-edge architectures, and MLOps practices, the framework supports diverse use cases

Emerging approaches, including edge-cloud integration and machine learning-based architectures, have been appeared in niche use cases.


## Discussion


En conclusion, les auteurs soutiennent la nécessité de concevoir des architectures capables d'intégrer des capteurs et dispositifs évolutifs afin de faciliter la transformation numérique du secteur agricole, tout en soulignant que la plupart des exigences identifiées rejoignent celles observées dans d'autres secteurs industriels. L'étude met en évidence que la gestion des données hétérogènes issues de capteurs et de services externes peut être résolue par les paradigmes Fog et Edge ou par le développement de scripts côté cloud utilisant des protocoles tels que HTTP et MQTT ainsi que des bases NoSQL comme MongoDB. Une approche microservices couplée à la conteneurisation Docker s'avère déterminante pour assurer scalabilité, portabilité et interopérabilité de la plateforme, tandis que des mécanismes de sécurité (rôles, authentification) demeurent indispensables. L'étude de cas, fondée exclusivement sur des technologies open-source dans un scénario réel d'élevage porcin, démontre la faisabilité de l'architecture proposée et illustre un transfert fluide entre les outils de modélisation développés en R et l'équipe de développement de la plateforme, tout en restant généralisable à d'autres processus agro-industriels. Les perspectives futures évoquées incluent l'intégration de nouveaux capteurs et de nœuds Edge, l'enregistrement de dispositifs IoT via codes QR, les notifications push, la traçabilité par Blockchain, et l'intégration d'un framework de calcul distribué tel qu'Apache Spark pour le traitement de volumes de données importants.

Cet article présente SA-FLIDS, un système de détection d'intrusion réseau basé sur l'apprentissage fédéré, sécurisé et authentifié, conçu pour les environnements de santé intelligente reposant sur le paradigme Fog-IoT. L'objectif principal est de détecter et de contrer les cyberattaques ciblant les dispositifs médicaux connectés (IoMT) en exploitant les capacités de calcul en périphérie (fog computing), tout en préservant la confidentialité des données et en réduisant la surcharge de communication. Le système répond spécifiquement aux vulnérabilités propres aux architectures d'apprentissage fédéré décentralisées, notamment les attaques par empoisonnement (poisoning) et les attaques Sybil. Pour ce faire, les auteurs combinent un modèle d'identité auto-souveraine (SSI) fondé sur la blockchain pour l'authentification des clients, une agrégation par moyenne tronquée (trimmed mean) au sein du processus fédéré, ainsi que des protocoles de communication sécurisés TLS et gRPC. L'évaluation expérimentale a été menée avec dix nœuds fog clients sous l'hypothèse de données indépendantes et identiquement distribuées (IID).


## Synthese


L'article vise à concevoir une architecture de machine learning légère et edge-based, LightPersML, permettant aux PME e-commerce disposant de ressources limitées de déployer des systèmes de personnalisation et de recommandation sophistiqués en temps réel, jusqu'alors réservés aux grandes plateformes disposant d'infrastructures cloud coûteuses. Le contexte scientifique qui motive cette recherche est double: d'une part, la nécessité croissante de préserver la confidentialité des données client face à des réglementations et attentes toujours plus strictes, et d'autre part, la volonté de réduire les coûts d'infrastructure et la latence des systèmes de recommandation cloud traditionnels. Les objectifs spécifiques incluent l'intégration de l'apprentissage fédéré pour un traitement distribué sans centralisation des données, l'exploitation d'AWS Step Functions et API Gateway pour une orchestration évolutive, ainsi que l'évaluation comparative des performances (latence, précision) entre systèmes edge et cloud. L'hypothèse implicite testée est qu'un compromis favorable entre efficacité computationnelle et précision de recommandation est atteignable en environnement edge contraint, sans sacrifier significativement la qualité de l'expérience de personnalisation.


## Raw_Aws_Lambda


A comparison between traditional and Serverless technologies in a microservices settingSupported by University of Oviedo and DXC Technology A PREPRINT Fig. 2. ECS fargate architecture

A comparison between traditional and Serverless technologies in a microservices settingSupported by University of Oviedo and DXC Technology A PREPRINT Fig. 2. ECS fargate architecture


## Raw_Introduction


(1) It employs an innovative approach that combines pre-embedding with SIMD to share vectorized data, thereby eliminating redundant embedding computations. (2) To maximize device utilization and scalability, MorphingDB implements a pipeline-based batch inference strategy using a Directed Acyclic Graph (DAG) of operators. By leveraging adaptive CPU-GPU device placement and applying advanced pipeline techniques to optimize execution order, Morph-ingDB streamlines complex inference workflows and minimizes bottlenecks.

(1) It employs an innovative approach that combines pre-embedding with SIMD to share vectorized data, thereby eliminating redundant embedding computations. (2) To maximize device utilization and scalability, MorphingDB implements a pipeline-based batch inference strategy using a Directed Acyclic Graph (DAG) of operators. By leveraging adaptive CPU-GPU device placement and applying advanced pipeline techniques to optimize execution order, Morph-ingDB streamlines complex inference workflows and minimizes bottlenecks.


## Raw_Aws_Eks_With_Dynamodb


A comparison between traditional and Serverless technologies in a microservices settingSupported by University of Oviedo and DXC Technology A PREPRINT Fig. 3. AWS lambda architecture

A comparison between traditional and Serverless technologies in a microservices settingSupported by University of Oviedo and DXC Technology A PREPRINT Fig. 3. AWS lambda architecture


## Raw_Orchestration_And_Workflow_Management


Table 3 presents Pipeline Orchestration and Workflow Management tools, frameworks, or platforms which are designed to centralise the automation, execution, monitoring, and management of workflow through the entire data pipelines from data sourcing through to utilization. These pipelines ensure that other interconnected pipelines or phases of a pipeline are executed in an orderly fashion to process data end-to-end. Apache Airflow is an open-source web-interfaced data pipeline orchestration and workflow management tool for ETL and data integration. It supports Python language and can perform automated workflow orchestration, scheduling, and monitoring of processes in parallel or as dependent processing of tasks and displays processes with graphs or DAGs to indicate the position and status of data processing (https://airflow.apache.org/). It works as a standalone or deployed to the cloud and performs data processing in batches but can integrate with frameworks like Apache Kafka to provide

Table 3 presents Pipeline Orchestration and Workflow Management tools, frameworks, or platforms which are designed to centralise the automation, execution, monitoring, and management of workflow through the entire data pipelines from data sourcing through to utilization. These pipelines ensure that other interconnected pipelines or phases of a pipeline are executed in an orderly fashion to process data end-to-end. Apache Airflow is an open-source web-interfaced data pipeline orchestration and workflow management tool for ETL and data integration. It supports Python language and can perform automated workflow orchestration, scheduling, and monitoring of processes in parallel or as dependent processing of tasks and displays processes with graphs or DAGs to indicate the position and status of data processing (https://airflow.apache.org/). It works as a standalone or deployed to the cloud and performs data processing in batches but can integrate with frameworks like Apache Kafka to provide


## Raw_Data_Acquisition_And_Transmission_Stability


nd data handling pipeline implemented at the ESP32-based edge device. These results demonstrate that the proposed architecture reliably supports continuous multisensor monitoring under representative assisted mobility conditions.


## Conclusion


Les services critiques en santé à distance basée sur le fog computing ont été systématiquement identifiés, catégorisés et analysés en cinq catégories essentielles : I/O, IA, données, sécurité/confidentialité, et sensible au contexte Une architecture conceptuelle a été proposée pour organiser tous les services critiques en un système modulaire cohérent L'étude de cas sur les soins aux traumatisés démontre la faisabilité pratique de l'approche, du moment de l'accident jusqu'à l'hospitalisation du patient, modélisée via des graphes de tâches mappés sur les couches de calcul fog appropriées Les travaux futurs porteront sur la conception d'algorithmes spécifiques à chaque composant de service, des stratégies de placement dynamique de services, et des mécanismes tolérants aux pannes