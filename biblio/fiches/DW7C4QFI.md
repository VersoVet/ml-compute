# Feature Engineering Infrastructure



## Resume


Feature Engineering Infrastructure

Model Training Infrastructure

The Role of Data Engineering in Enabling Machine Learning and Artificial Intelligence

Machine learning (ML) and artificial intelligence (AI) systems depend heavily on high-quality, structured data to function effectively. Data engineering plays a fundamental role in creating, managing, and optimizing the pipelines and infrastructure that allow for the seamless flow of data across various stages of the ML/AI workflow. This includes the critical tasks of data ingestion, cleaning, preprocessing, and feature engineering, which ensure that the raw data is transformed into a form suitable for model training. Without solid data engineering practices, AI/ML models are prone to inaccuracies, scalability issues, and poor performance. A robust data engineering foundation is vital for enabling the development of efficient models that can scale and produce reliable results over time. This article investigates the essential role of data engineering in ensuring the success of ML/AI systems. It highlights key data engineering practices such as automation of data pipelines, efficient data storage, and management techniques that ensure data quality and reliability. The study also delves into the impact of modern architecture, including cloud-based solutions and automation tools, which help in reducing human intervention and improving the speed of model deployment. Through the examination of real-world case studies, the paper demonstrates how well-executed data engineering practices lead to faster, more accurate model development, lower operational costs, and improved scalability. Ultimately, the article emphasizes that data engineering is indispensable for organizations aiming to unlock the full potential of their AI and ML initiatives, driving innovation and competitive advantage.

Model Serving Infrastructure

ML Observability Infrastructure

Towards Accountability for Machine Learning Datasets: Practices from Software Engineering and Infrastructure

Performance Engineering for Microservices

The Geometry of Distribution Shift: Topological and Information-Theoretic Invariants for Detecting Regime Change

Abstract:
This book develops an integrated framework for studying distribution shift as a geometric, statistical, and governance problem rather than as a narrow failure of model fit. The manuscript argues that regime change becomes intelligible when shifts are represented through invariants that preserve structural information across domains, scales, and decision settings. Topological summaries identify persistent relational features of data manifolds, while information-theoretic quantities characterise uncertainty, dependence, and irreversibility under evolving environments. Together these tools support a research programme in which explanation, causal reasoning, prediction, and operational deployment are evaluated through common design principles: explicit assumptions, robust validation, reproducibility, and public accountability. Across five chapters, the text develops conceptual foundations, causal and explanatory modeling strategies, predictive machine learning workflows, scalable analytics infrastructures, and sectoral applications linked to governance and policy. The resulting manuscript is intended for researchers designing shift-aware studies, practitioners building trustworthy analytical systems, and policymakers assessing the institutional consequences of automated decisions under uncertainty. By treating regime change as a measurable transformation in geometry, information, and action, the book offers a coherent basis for developing models, metrics, protocols, and governance instruments that remain useful when real-world conditions cease to resemble the past.
Keywords
distribution shift, regime change, topology, information theory, invariants, causal inference, statistical modeling, machine learning, generalization, uncertainty quantification, trustworthiness, big data engineering, reproducibility, MLOps, scalable analytics, governance, policy evaluation, domain adaptation

FeAture Explorer (FAE): A tool for developing and comparing radiomics models.

In radiomics studies, researchers usually need to develop a supervised machine learning model to map image features onto the clinical conclusion. A classical machine learning pipeline consists of several steps, including normalization, feature selection, and classification. It is often tedious to find an optimal pipeline with appropriate combinations. We designed an open-source software package named FeAture Explorer (FAE). It was programmed with Python and used NumPy, pandas, and scikit-learning modules. FAE can be used to extract image features, preprocess the feature matrix, develop different models automatically, and evaluate them with common clinical statistics. FAE features a user-friendly graphical user interface that can be used by radiologists and researchers to build many different pipelines, and to compare their results visually. To prove the effectiveness of FAE, we developed a candidate model to classify the clinical-significant prostate cancer (CS PCa) and non-CS PCa usin

Production Machine Learning Pipelines


## Raw_High-Level_Architecture


The ZSM framework features a closed-control loop for managing 6G services, as illustrated in Fig. 6 As shown in Fig. 6.1, the design of the NMS consists of three stages: (i) Monitoring System (MS), the MS collects KPIs from the 6G infrastructure, including network latency, packet loss, and resource usage metrics. These KPIs are essential for the Anomaly Detection Engines (ADEs) to identify anomalies; (ii) ADEs, the ADEs use AI to detect anomalies and XAI to provide numerical explanations. Each ADE focuses on specific anomalies, such as QoS issues or security threats, and uses XAI to explain feature contributions; (iii) Analytics Engine (AE), the AE processes outputs from the ADEs, using an LLM to reason about predictions and explanations. It provides comprehensive explanations for root causes and suggests actions. If ZSM is enabled, the LLM can autonomously execute these actions without human intervention.

The ZSM framework features a closed-control loop for managing 6G services, as illustrated in Fig. 6 As shown in Fig. 6.1, the design of the NMS consists of three stages: (i) Monitoring System (MS), the MS collects KPIs from the 6G infrastructure, including network latency, packet loss, and resource usage metrics. These KPIs are essential for the Anomaly Detection Engines (ADEs) to identify anomalies; (ii) ADEs, the ADEs use AI to detect anomalies and XAI to provide numerical explanations. Each ADE focuses on specific anomalies, such as QoS issues or security threats, and uses XAI to explain feature contributions; (iii) Analytics Engine (AE), the AE processes outputs from the ADEs, using an LLM to reason about predictions and explanations. It provides comprehensive explanations for root causes and suggests actions. If ZSM is enabled, the LLM can autonomously execute these actions without human intervention.


## Table


Tableau: Association between Motivation and Requirement. The motivation and requirement association matrix reveals structured request patterns. Development Delivery strongly associates with Documentation Improvement (d ij = 13.01, χ 2 ij = 130.91, log OR(HA) = 3.27) and Infrastructure Optimization (d ij = 7.68), suggesting demand for clearer guides and stable infrastructure. Model Adaptation concentrates on Integration Requirement (d ij = 10.9), reflecting demand for connections to diverse model providers and vendor APIs. Framework level results show consistent design-related patterns: in AutoGen, Model Adaptation strongly associates with Integration Requirement (d ij = 8.26), aligning with dialogue-centered multi agent collaboration; in CrewAI, Development Delivery strongly associates with Documentation Improvement (d ij = 9.75), suggesting stronger demand for engineering guidance. Our findings show that agent framework quality assurance should jointly consider failure causes, symptoms, developer requests, and lifecycle stages. Findings 1 and 2 reveal semantic interface faults and silent functional failures. Findings 3, 4, and 7 highlight execution centered concentration and stage specific patterns. Findings 5, 6 and 8 show that developer requests offer structured signals for framework evolution. These results suggest the following implications. Framework Maintainers. Findings 1 and 4 show that API, configuration, parsing, and serialization causes dominate many failures and vary across lifecycle stages. Maintainers should prioritize stable interface contracts, clearer configuration diagnostics, provider compatibility checks, and robust handling of states and structured outputs. Findings 5 and 6 further suggest that requests for orchestration expressiveness, development delivery, model adaptation, tool ecosystem support, and feature enhancement should guide framework evolution. Framework Users. Findings 1 and 2 indicate that many failures occur at API, configuration, schema, state, and output boundaries, and often appear as incorrect or missing results rather than crashes. Users should check API versions, provider settings, tool schemas, serialized states, and execution traces, and validate tool calls, state transitions, structured outputs, and final results. Testing Researchers. Findings 1, 2, and 4 suggest testing beyond crash centered and tensor level techniques. API issues motivate version aware API sequence testing; parsing errors motivate mutation of JSON objects, tool call payloads, and schema constrained responses; serialization errors motivate round trip state testing; incorrect functionality motivates execution trace replay and semantic output validation; and misconfiguration motivates configuration mutation with diagnostic and graceful failure oracles.
| Association across Lifecycle Stages. Mapping motivations |
| --- |
| and requirements onto lifecycle stages reveals stage-specific |
| request signatures. In Agent Initialization, Documentation |
| Improvement shows a strong association (d ij = 6.95, |
| χ 2 ij = 41.12, log OR(HA) = 1.95), suggesting demand |
| for configuration guides and quickstart materials during |
| environment, credential, dependency, and initial agent setup. |
| Other stage associations provide useful but more tentative |
| signals because some stage-level cells contain limited samples. |
| Evolution associates with Development Delivery (d ij = 4.33, |
| χ 2 ij = 14.82, log OR(HA) = 1.36), suggesting that requests |
| tend to emphasize delivery efficiency and engineering conti- |
| nuity during migration, updates, and long-term adaptation. |
| Finding 8: Developer facing requests exhibit structured |
| associations among motivations, requirements, and |
| lifecycle stages. Development Delivery aligns with |
| documentation and infrastructure needs, while Model |
| Adaptation aligns with integration needs. These patterns |
| suggest that framework maintenance should organize fea- |
| ture requests by motivation, requirement type, and lifecycle |
| context rather than treating them as isolated backlog items. |
| V. DISCUSSION |
| A. Implications |

Tableau: Association between Motivation and Requirement. The motivation and requirement association matrix reveals structured request patterns. Development Delivery strongly associates with Documentation Improvement (d ij = 13.01, χ 2 ij = 130.91, log OR(HA) = 3.27) and Infrastructure Optimization (d ij = 7.68), suggesting demand for clearer guides and stable infrastructure. Model Adaptation concentrates on Integration Requirement (d ij = 10.9), reflecting demand for connections to diverse model providers and vendor APIs. Framework level results show consistent design-related patterns: in AutoGen, Model Adaptation strongly associates with Integration Requirement (d ij = 8.26), aligning with dialogue-centered multi agent collaboration; in CrewAI, Development Delivery strongly associates with Documentation Improvement (d ij = 9.75), suggesting stronger demand for engineering guidance. Our findings show that agent framework quality assurance should jointly consider failure causes, symptoms, developer requests, and lifecycle stages. Findings 1 and 2 reveal semantic interface faults and silent functional failures. Findings 3, 4, and 7 highlight execution centered concentration and stage specific patterns. Findings 5, 6 and 8 show that developer requests offer structured signals for framework evolution. These results suggest the following implications. Framework Maintainers. Findings 1 and 4 show that API, configuration, parsing, and serialization causes dominate many failures and vary across lifecycle stages. Maintainers should prioritize stable interface contracts, clearer configuration diagnostics, provider compatibility checks, and robust handling of states and structured outputs. Findings 5 and 6 further suggest that requests for orchestration expressiveness, development delivery, model adaptation, tool ecosystem support, and feature enhancement should guide framework evolution. Framework Users. Findings 1 and 2 indicate that many failures occur at API, configuration, schema, state, and output boundaries, and often appear as incorrect or missing results rather than crashes. Users should check API versions, provider settings, tool schemas, serialized states, and execution traces, and validate tool calls, state transitions, structured outputs, and final results. Testing Researchers. Findings 1, 2, and 4 suggest testing beyond crash centered and tensor level techniques. API issues motivate version aware API sequence testing; parsing errors motivate mutation of JSON objects, tool call payloads, and schema constrained responses; serialization errors motivate round trip state testing; incorrect functionality motivates execution trace replay and semantic output validation; and misconfiguration motivates configuration mutation with diagnostic and graceful failure oracles.
| Association across Lifecycle Stages. Mapping motivations |
| --- |
| and requirements onto lifecycle stages reveals stage-specific |
| request signatures. In Agent Initialization, Documentation |
| Improvement shows a strong association (d ij = 6.95, |
| χ 2 ij = 41.12, log OR(HA) = 1.95), suggesting demand |
| for configuration guides and quickstart materials during |
| environment, credential, dependency, and initial agent setup. |
| Other stage associations provide useful but more tentative |
| signals because some stage-level cells contain limited samples. |
| Evolution associates with Development Delivery (d ij = 4.33, |
| χ 2 ij = 14.82, log OR(HA) = 1.36), suggesting that requests |
| tend to emphasize delivery efficiency and engineering conti- |
| nuity during migration, updates, and long-term adaptation. |
| Finding 8: Developer facing requests exhibit structured |
| associations among motivations, requirements, and |
| lifecycle stages. Development Delivery aligns with |
| documentation and infrastructure needs, while Model |
| Adaptation aligns with integration needs. These patterns |
| suggest that framework maintenance should organize fea- |
| ture requests by motivation, requirement type, and lifecycle |
| context rather than treating them as isolated backlog items. |
| V. DISCUSSION |
| A. Implications |

Tableau: Machine Learning and Model Deployment Pipelines
| Tools/Framework/Platform | Year of Introduction | Source | Primary Language | Data Parsing | Data Organisation Data Dictionary Data Integration | Data Transformation | Canonicalization | Data Quality Missing Data Anomalies | Non-Stationarity | Feature Engineering | ETL | Processing Format Batch | Streaming | DAG / Graph | Environment Local Cloud |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TFX (TensorFlow Extended) 2017 O | Python |  |  |  |  | I I B |  |  | I I | B |
| Kubeflow | 2017 O Py, C++, JS |  |  |  |  |  |  |  |  |  | I I | B |
| Metaflow | 2018 O | Python |  |  |  |  |  |  |  |  | B I B | B |
| ZenML | 2020 O | Python |  |  |  |  |  |  |  |  |  |  | B | B |
| MLRun | 2019 O | Python |  |  |  |  |  |  |  |  |  | I I | B |
| CML |  | O | Python |  | B |  |  |  |  |  |  |  |  | I | B |
| Cortex Lab |  | O | Python |  |  |  |  |  |  |  |  |  |  | B | B |
| Seldon Core | 2016 O Python, Go |  |  |  |  |  |  |  |  |  | I I | B |
| AutoKeras | 2019 O | Python |  |  |  |  |  |  | I |  |  |  | I | B |
| H2O AutoML | 2012 O Python, R |  |  |  |  | I |  | I |  |  |  | I | B |
| a. Py: Python; JS: JavaScript; |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Within the capabilities, B: Built-in capabilities; I: Integrates with other tools to achieve. |  |  |  |

Tableau: Machine Learning and Model Deployment Pipelines
| Tools/Framework/Platform | Year of Introduction | Source | Primary Language | Data Parsing | Data Organisation Data Dictionary Data Integration | Data Transformation | Canonicalization | Data Quality Missing Data Anomalies | Non-Stationarity | Feature Engineering | ETL | Processing Format Batch | Streaming | DAG / Graph | Environment Local Cloud |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TFX (TensorFlow Extended) 2017 O | Python |  |  |  |  | I I B |  |  | I I | B |
| Kubeflow | 2017 O Py, C++, JS |  |  |  |  |  |  |  |  |  | I I | B |
| Metaflow | 2018 O | Python |  |  |  |  |  |  |  |  | B I B | B |
| ZenML | 2020 O | Python |  |  |  |  |  |  |  |  |  |  | B | B |
| MLRun | 2019 O | Python |  |  |  |  |  |  |  |  |  | I I | B |
| CML |  | O | Python |  | B |  |  |  |  |  |  |  |  | I | B |
| Cortex Lab |  | O | Python |  |  |  |  |  |  |  |  |  |  | B | B |
| Seldon Core | 2016 O Python, Go |  |  |  |  |  |  |  |  |  | I I | B |
| AutoKeras | 2019 O | Python |  |  |  |  |  |  | I |  |  |  | I | B |
| H2O AutoML | 2012 O Python, R |  |  |  |  | I |  | I |  |  |  | I | B |
| a. Py: Python; JS: JavaScript; |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| Within the capabilities, B: Built-in capabilities; I: Integrates with other tools to achieve. |  |  |  |


## Quote


we introduce multiple innovative network structures, including the Frequency Domain Similarity-Gated Selection Vision Transformer and the Mixed-Scale Frequency Domain Feedforward Network. These structures leverage gating operations, parameter matrices, and frequency domain fusion methods to effectively integrate shallow and deep information

Our network architecture contains three sequential modules: a feature extraction module, an attentive feature pyramid fusion (AFPF) module, and a prediction module.

obtaining extensive labeled data can be challenging in the civil infrastructure domain due to the diversity and dynamic nature of construction environments


## Insight


methodology: Les modules de feature engineering exploitent les capacités de calcul distribué d'Apache Spark pour transformer les données brutes en variables analytiques exploitables par les algorithmes d'apprentissage automatique, tout en maintenant une traçabilité complète (lineage) de l'ensemble des transformations appliquées.

methodology: Le pipeline proposé associe un FCN léger agissant comme pré-processeur entraînable, qui normalise les images d'entrée, à un FC-ResNet profond de plus de 100 couches réalisant un raffinement itératif de la segmentation.

methodology: Deux innovations architecturales, le Frequency Domain Similarity-Gated Selection Vision Transformer et le Mixed-Scale Frequency Domain Feedforward Network, s'appuient sur des opérations de gating, des matrices de paramètres et des méthodes de fusion en domaine fréquentiel pour intégrer efficacement information superficielle et profonde, renforçant la capacité du réseau à modéliser à la fois les motifs distants et locaux.


## Raw_Data_Engineering_Pipelines


The levels of support available for data engineering pipelines vary, from the existence of just a container for solutions to the availability of plug-and-play components and features. Some pipelines do exist where a specific section comes with preloaded and ready-to-use components such as TFX (TensorFlow Extended) pipeline for machine learning, it's however a wish to have an ideal pipeline where the components at every stage of the pipeline are preloaded and scalable to accommodate changing requirements for data engineering tasks.

The levels of support available for data engineering pipelines vary, from the existence of just a container for solutions to the availability of plug-and-play components and features. Some pipelines do exist where a specific section comes with preloaded and ready-to-use components such as TFX (TensorFlow Extended) pipeline for machine learning, it's however a wish to have an ideal pipeline where the components at every stage of the pipeline are preloaded and scalable to accommodate changing requirements for data engineering tasks.


## Methodologie


Les structures d’ingénierie, constituées de matériaux hétérogènes comportant des grains ou des fibres, présentent un risque accru de rupture lié à l’initiation et à la propagation simultanées de fissures internes et interfaciales. Deux familles d’approches numériques structurent la modélisation de la rupture : les formulations discrètes, traitant la fissure comme une discontinuité géométrique, et les formulations continues, où la discontinuité est régularisée via des variables d’endommagement internes, notamment dans le cadre des modèles à champ de phase (PFM). Ces derniers reposent sur une formulation variationnelle de minimisation de l’énergie globale, reliée aux fissures discrètes par la Γ-convergence, et ont été enrichis pour traiter la nucléation, la dépendance aux modes de fissuration et les chargements mixtes. Parallèlement, les modèles de zone cohésive (CZM) décrivent les relations contrainte–déformation le long d’interfaces prédéfinies en remplaçant les singularités de Griffith par des concentrations de contrainte bornées. La synthèse des approches PFM et CZM, via une fonction de dégradation contrôlant l’adhérence d’une couche mince d’interface, vise à unifier la description des fissures internes et interfaciales.


## Synthese


Les structures d’ingénierie, constituées de matériaux hétérogènes comportant des grains ou des fibres, présentent un risque accru de rupture lié à l’initiation et à la propagation simultanées de fissures internes et interfaciales. Deux familles d’approches numériques structurent la modélisation de la rupture : les formulations discrètes, traitant la fissure comme une discontinuité géométrique, et les formulations continues, où la discontinuité est régularisée via des variables d’endommagement internes, notamment dans le cadre des modèles à champ de phase (PFM). Ces derniers reposent sur une formulation variationnelle de minimisation de l’énergie globale, reliée aux fissures discrètes par la Γ-convergence, et ont été enrichis pour traiter la nucléation, la dépendance aux modes de fissuration et les chargements mixtes. Parallèlement, les modèles de zone cohésive (CZM) décrivent les relations contrainte–déformation le long d’interfaces prédéfinies en remplaçant les singularités de Griffith par des concentrations de contrainte bornées. La synthèse des approches PFM et CZM, via une fonction de dégradation contrôlant l’adhérence d’une couche mince d’interface, vise à unifier la description des fissures internes et interfaciales.