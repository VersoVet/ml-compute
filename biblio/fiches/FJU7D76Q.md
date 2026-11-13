# The arctic knowledge-based system: Science gateway integration for petascale arctic data processing and geospatial feature prediction



## Resume


The arctic knowledge-based system: Science gateway integration for petascale arctic data processing and geospatial feature prediction

Science gateways have become essential platforms that integrate computational resources, data services, and workflows for domain researchers, enabling artificial intelligence-driven (AI) analyses at scale. Building on this paradigm, we introduce the Science Gateway component of the Arctic Knowledge-Based System (A-KBS), designed to advance AI-assisted modeling of permafrost dynamics and other Arctic geospatial processes. The A-KBS provides researchers with a unified portal to configure and execute multi-horizon prediction tools for active layer thickness, ground deformation, wildfire occurrence, freeze/thaw states, soil and air temperature analyses, and to run global scale geospatial HPC workflows leveraging data from across the circumpolar Arctic. This system orchestrates workloads through Kubernetes-based (K8s) containerized environments, Globus Data Transfer/Compute services, and distributed computing tools such as Slurm, ParSL, and Ray.io. Its web portal is deployed on the Universi

Data science pipelines in lakehouse architectures: A scalable approach to big data analytics

The exponential growth of data generation across industries has necessitated the development of sophisticated architectures capable of handling diverse data types while maintaining analytical agility. This paper presents a comprehensive framework for implementing end-to-end data science pipelines within lakehouse architectures, bridging the gap between traditional data warehouses and data lakes. The proposed methodology leverages the unified storage and processing capabilities of lakehouse systems to create scalable, reproducible, and maintainable data science workflows that support both exploratory analytics and production machine learning deployments.
Our research introduces a novel modular pipeline framework that seamlessly integrates data engineering and data science operations through containerized microservices architecture. The framework incorporates advanced metadata management systems for comprehensive data lineage tracking and implements cloud-native automation layers that dynamically scale computational resources based on workload demands. Through systematic evaluation of performance metrics and real-world case studies, we demonstrate significant improvements in pipeline execution time, resource utilization efficiency, and model deployment velocity compared to traditional architectures.
The lakehouse paradigm enables data scientists to perform complex analytics on raw, semi-structured, and structured data without the traditional extract-transform-load bottlenecks that characterize conventional data warehouse approaches. By combining Apache Spark's distributed processing capabilities with Databricks' collaborative analytics platform and MLflow's model lifecycle management, our framework provides a comprehensive solution for enterprise-scale data science operations. Experimental results indicate up to 60% reduction in time-to-insight and 40% improvement in computational resource efficiency compared to legacy pipeline architectures.

A Cloud-Native Data Science Platform for Official Statistics

Accelerating earth science discovery via multi-agent LLM systems.

This Perspective explores the transformative potential of multi-agent systems (MAS) powered by Large Language Models (LLMs) in the geosciences. Users of geoscientific data repositories face challenges due to the complexity and diversity of data formats, inconsistent metadata practices, and a considerable number of unprocessed datasets. MAS possesses transformative potential for improving scientists' interaction with geoscientific data by enabling intelligent data processing, natural language interfaces, and collaborative problem-solving capabilities. We illustrate this approach with "PANGAEA GPT," a specialized MAS pipeline integrated with the diverse PANGAEA database for Earth & Environmental Science, demonstrating how MAS-driven workflows can effectively manage complex datasets and accelerate scientific discovery. We discuss how MAS can address current data challenges in geosciences, highlight advancements in other scientific fields, and propose future directions for integrating MAS

Reproducible data science over data lakes: replayable data pipelines with Bauplan and Nessie

Intelligent Data Flow Automation for AI Systems via Advanced Engineering Practices

Modern Artificial Intelligence (AI) systems demand seamless, scalable, and intelligent data flows to support real-time analytics, model training, and automated decision-making. However, traditional data pipelines are often rigid, manual, and inefficient, leading to delays, data silos, and suboptimal model performance. This research explores how advanced data engineering techniques—such as real-time data streaming, automated ETL/ELT processes, data orchestration, schema evolution, and intelligent data validation can automate and optimize the end-to-end data flow in AI systems. A comprehensive framework is proposed that integrates Apache Kafka, Apache Airflow, Delta Lake, and ML-based metadata management into a unified automation stack. Case studies across healthcare, finance, and IoT domains are used to demonstrate measurable improvements in pipeline efficiency, data quality, system scalability, and AI model readiness. The results underscore the transformative potential of advanced data engineering in enabling adaptive, self-healing, and intelligent data infrastructures that power modern AI ecosystems.

Gated spatio and temporal convolutional neural network for activity recognition: towards gated multimodal deep learning

Editorial: Synergizing large language models and computational intelligence for advanced robotic systems.


## Table


Tableau: 10: Dataset coverage of APIGateway coupled with communication patterns and data access and storage patterns.

Tableau: 10: Dataset coverage of APIGateway coupled with communication patterns and data access and storage patterns.

Tableau: 9: Dataset coverage of ApiGateway coupled with databases patterns.

Tableau: 9: Dataset coverage of ApiGateway coupled with databases patterns.

Tableau: Algorithm for the proposed Radial Basis Function Neural Network (RBF-NN) model for interpretable image classification.

Tableau: Algorithm for the proposed Radial Basis Function Neural Network (RBF-NN) model for interpretable image classification.

Tableau: Input variables used for anomaly detection and their physical interpretation.

Tableau: Characteristics of the image dataset.


## Quote


By working together, these agents can efficiently handle heterogeneous datasets, bridge gaps between different branches of geoscience, and provide researchers with more holistic insights.

It comprises one integrated expert-AI decision support system/platform with three modules:

A promising direction involves incorporating anatomical prior knowledge-such as organ shapes, sizes, spatial locations, and temporal relationships-into the adapter design. This integration could offer a more structured and biologically informed method for guiding feature extraction and improving segmentation accuracy.

we introduce multiple innovative network structures, including the Frequency Domain Similarity-Gated Selection Vision Transformer and the Mixed-Scale Frequency Domain Feedforward Network. These structures leverage gating operations, parameter matrices, and frequency domain fusion methods to effectively integrate shallow and deep information


## Raw_Full_Text


Abstract
This dissertation aims at building and using knowledge-driven models in order
to improve the accuracy of automatic image annotation.
Currently, many image
annotation approaches are based on the automatic association between low-level or
mid-level visual features and semantic concepts using machine learning techniques.
Nevertheless, the only use of machine learning seems to be insuﬃcient to bridge the
well-known semantic gap problem, and therefore to achieve eﬃcient systems for auto-
matic image annotation. Structured knowledge models, such as semantic hierarchies
and ontologies, appear to be a good way to improve such approaches. These semantic
structures allow modeling many valuable semantic relations between concepts, as for
instance subsumption, contextual and spatial relationships. Indeed, these relation-
ships have been proved to be of prime importance for the understanding of image
semantics. Moreover, such structured knowledge models about high-level concepts
enable to

Abstract
This dissertation aims at building and using knowledge-driven models in order
to improve the accuracy of automatic image annotation.
Currently, many image
annotation approaches are based on the automatic association between low-level or
mid-level visual features and semantic concepts using machine learning techniques.
Nevertheless, the only use of machine learning seems to be insuﬃcient to bridge the
well-known semantic gap problem, and therefore to achieve eﬃcient systems for auto-
matic image annotation. Structured knowledge models, such as semantic hierarchies
and ontologies, appear to be a good way to improve such approaches. These semantic
structures allow modeling many valuable semantic relations between concepts, as for
instance subsumption, contextual and spatial relationships. Indeed, these relation-
ships have been proved to be of prime importance for the understanding of image
semantics. Moreover, such structured knowledge models about high-level concepts
enable to

al., 2001], image semantics is rather an emergent property of the inter-
action of the user and the image content. We can therefore conclude that the image
interpretation process requires often a reasoning mechanism over the detected objects
in the image, which is usually based on cognition and on the past experiences.
Accordingly, in order to match user expectations in an image retrieval system, it
is important to provide tools that allow building and using knowledge models
representing the image context (and consequently the image semantics). These
will allow reproducing the reasoning process in order to deduce a more consistent
image annotation/interpretation. Speciﬁcally, we believe that these knowledge models
should go further than the simple description of speciﬁc objects that may appear in
images, and rather model the image context through the description of concepts
and the semantic relationships between them. For instance, a good description of
the image 2.3(d) is: a "polar b

al., 2001], image semantics is rather an emergent property of the inter-
action of the user and the image content. We can therefore conclude that the image
interpretation process requires often a reasoning mechanism over the detected objects
in the image, which is usually based on cognition and on the past experiences.
Accordingly, in order to match user expectations in an image retrieval system, it
is important to provide tools that allow building and using knowledge models
representing the image context (and consequently the image semantics). These
will allow reproducing the reasoning process in order to deduce a more consistent
image annotation/interpretation. Speciﬁcally, we believe that these knowledge models
should go further than the simple description of speciﬁc objects that may appear in
images, and rather model the image context through the description of concepts
and the semantic relationships between them. For instance, a good description of
the image 2.3(d) is: a "polar b

integrated knowledge can help in various
spots of the image retrieval process, such as: i) image analysis, ii) mapping visual
41


## Methodologie


L'article situe les architectures lakehouse comme une réponse structurelle aux limites des dichotomies traditionnelles entre data lakes et data warehouses, face à la croissance en volume, vélocité et variété des données issues de sources hétérogènes (IoT, flux temps réel, applications d'entreprise). En s'appuyant sur des formats ouverts tels que Delta Lake, Apache Iceberg et Apache Hudi, cette architecture combine transactions ACID et flexibilité de stockage, permettant de traiter conjointement des charges de travail batch et streaming au sein d'un pipeline de data science unifié. Sur le plan méthodologique, les auteurs proposent un framework modulaire où les modules de feature engineering s'appuient sur Apache Spark pour le traitement distribué et la traçabilité de la lignée des données, tandis que les modules d'entraînement de modèles standardisent l'accès à des frameworks variés (scikit-learn, TensorFlow, PyTorch, XGBoost) via une intégration avec MLflow pour le suivi des expériences et l'optimisation des hyperparamètres. Cette conception modulaire et conteneurisée vise à garantir portabilité, reproductibilité et gouvernance à l'échelle de l'entreprise, tout en s'adaptant dynamiquement à la demande computationnelle.


## Synthese


L'article situe les architectures lakehouse comme une réponse structurelle aux limites des dichotomies traditionnelles entre data lakes et data warehouses, face à la croissance en volume, vélocité et variété des données issues de sources hétérogènes (IoT, flux temps réel, applications d'entreprise). En s'appuyant sur des formats ouverts tels que Delta Lake, Apache Iceberg et Apache Hudi, cette architecture combine transactions ACID et flexibilité de stockage, permettant de traiter conjointement des charges de travail batch et streaming au sein d'un pipeline de data science unifié. Sur le plan méthodologique, les auteurs proposent un framework modulaire où les modules de feature engineering s'appuient sur Apache Spark pour le traitement distribué et la traçabilité de la lignée des données, tandis que les modules d'entraînement de modèles standardisent l'accès à des frameworks variés (scikit-learn, TensorFlow, PyTorch, XGBoost) via une intégration avec MLflow pour le suivi des expériences et l'optimisation des hyperparamètres. Cette conception modulaire et conteneurisée vise à garantir portabilité, reproductibilité et gouvernance à l'échelle de l'entreprise, tout en s'adaptant dynamiquement à la demande computationnelle.


## Raw_Interaction.


integrating domain knowledge [151], or enhancing how the information is provided [31,92,140,153,159].

integrating domain knowledge [151], or enhancing how the information is provided [31,92,140,153,159].


## Insight


methodology: Deux innovations architecturales, le Frequency Domain Similarity-Gated Selection Vision Transformer et le Mixed-Scale Frequency Domain Feedforward Network, s'appuient sur des opérations de gating, des matrices de paramètres et des méthodes de fusion en domaine fréquentiel pour intégrer efficacement information superficielle et profonde, renforçant la capacité du réseau à modéliser à la fois les motifs distants et locaux.