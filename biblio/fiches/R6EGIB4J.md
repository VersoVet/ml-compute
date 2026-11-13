# Trueno: A Cross-Platform Machine Learning Model Serving Framework in Heterogeneous Edge Systems



## Resume


Trueno: A Cross-Platform Machine Learning Model Serving Framework in Heterogeneous Edge Systems

Mélange: Cost Efficient Large Language Model Serving by Exploiting GPU Heterogeneity

Building Scalable Quality Assurance Frameworks for Reliable Training Data Across Frontier Artificial Intelligence Model Development

MONET: Modeling and Optimization of neural NEtwork Training from Edge to Data Centers

While hardware-software co-design has significantly improved the efficiency of neural network inference, modeling the training phase remains a critical yet underexplored challenge. Training workloads impose distinct constraints, particularly regarding memory footprint and backpropagation complexity, which existing inference-focused tools fail to capture. This paper introduces MONET, a framework designed to model the training of neural networks on heterogeneous dataflow accelerators. MONET builds upon Stream, an experimentally verified framework that that models the inference of neural networks on heterogeneous dataflow accelerators with layer fusion. Using MONET, we explore the design space of ResNet-18 and a small GPT-2, demonstrating the framework's capability to model training workflows and find better hardware architectures. We then further examine problems that become more complex in neural network training due to the larger design space, such as determining the best layer-fusion

CTNEE-Net:A Cascaded Transformer Network with Edge Enhancement for Low-Dose femoral head CT Image Denoising


## Raw_Large_Mllms_Used_For_Visual_Assistance


And in work [54] Edge-MultiAI framework is specially crafted to manage the multi-tenancy for latency-sensitive deep learning models running in edge computing environments. Its primary goal is the optimization of the resource utilization to enable co-execution of multiple AI operations with little latency in varied system setups.


## Quote


techniques hand-crafted (Harris corner, template matching, active shape models (ASM), Hough transform, canny edge detection, region growing, GMM, point distribution models) et architectures de deep learning (CNN 3D, U-Net, FCN, FU-Net, DeconvNet, random forest de régression par vote).

This paper proposed an enhanced system design framework for AI engineering, enabling scalable, reliable, and ethical AI applications. By integrating advanced data pipelines, distributed training, hybrid cloud-edge architectures, and MLOps practices, the framework supports diverse use cases

Emerging approaches, including edge-cloud integration and machine learning-based architectures, have been appeared in niche use cases.

This paper introduces MONET, which builds upon the Stream framework to enable modeling and optimization of full neural network training workloads on heterogeneous dataflow accelerators. By incorporating forward and backward execution, optimizer steps, layer fusion, and activation checkpointing into a unified pipeline, MONET provides accurate latency, energy, and memory estimates for training

This paper introduces MONET, which builds upon the Stream framework to enable modeling and optimization of full neural network training workloads on heterogeneous dataflow accelerators. By incorporating forward and backward execution, optimizer steps, layer fusion, and activation checkpointing into a unified pipeline, MONET provides accurate latency, energy, and memory estimates for training

Notably, the UNet framework was used across many ML tasks (i.e., super resolution, segmentation, and prediction), demonstrating its robust utility and consistent model choice.

These examples illustrate the utility of the framework in guiding various AI efforts and offer lessons learned.


## Raw_A._Image_Classification


For computer vision applications, ResNet is a wellestablished architecture commonly employed as a backbone for tasks such as image classification and semantic segmentation. Comparable convolutional neural network (CNN) architectures have also demonstrated efficacy for edge training in MCUNetv3 [38]. In this part, we focus on a ResNet18 model deployed on an Edge TPU platform, as depicted in Figure 4. We select a base ResNet18 and we model its latency and energy cost on a standard CIFAR-10 image size that is (3,32,32).

For computer vision applications, ResNet is a wellestablished architecture commonly employed as a backbone for tasks such as image classification and semantic segmentation. Comparable convolutional neural network (CNN) architectures have also demonstrated efficacy for edge training in MCUNetv3 [38]. In this part, we focus on a ResNet18 model deployed on an Edge TPU platform, as depicted in Figure 4. We select a base ResNet18 and we model its latency and energy cost on a standard CIFAR-10 image size that is (3,32,32).


## Raw_Effect_Of_Cpu-Gpu_Placement


Multi-modal. We leverage selection and join operators to enable cross-modal data fusion by integrating image recognition and text reasoning models along with window functions applied to the data inputs. Figure 13a shows strong adaptability by assigning heterogeneous devices (e.g., GPU for image models and CPU for lightweight text models) to different sub-tasks. This device-aware execution enables global latency minimization, validating the effectiveness of our model in complex, heterogeneous inference scenarios.

Multi-modal. We leverage selection and join operators to enable cross-modal data fusion by integrating image recognition and text reasoning models along with window functions applied to the data inputs. Figure 13a shows strong adaptability by assigning heterogeneous devices (e.g., GPU for image models and CPU for lightweight text models) to different sub-tasks. This device-aware execution enables global latency minimization, validating the effectiveness of our model in complex, heterogeneous inference scenarios.


## Table


Tableau: Hardware platform details.
| commonly-used asynchronous algorithms in deep learning rec- |
| --- |
| ommendation model training include Elastic-Averaging SGD |
| (EASGD) [57], Hogwild! [48] and Facebook's ShadowSync |
| algorithm [?]. |

Tableau: Hardware platform details.
| commonly-used asynchronous algorithms in deep learning rec- |
| --- |
| ommendation model training include Elastic-Averaging SGD |
| (EASGD) [57], Hogwild! [48] and Facebook's ShadowSync |
| algorithm [?]. |

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


## Raw_Software_Architecture_And_Extensibility


The framework relies on ONNX Runtime as a unified inference backend, allowing trained 3D nnU-Net models to be integrated after ONNX conversion without modifying the application backend. This design facilitates adaptation to additional MRI modalities and lesion segmentation tasks while preserving the same deployment infrastructure.

The framework relies on ONNX Runtime as a unified inference backend, allowing trained 3D nnU-Net models to be integrated after ONNX conversion without modifying the application backend. This design facilitates adaptation to additional MRI modalities and lesion segmentation tasks while preserving the same deployment infrastructure.


## Insight


methodology: Le framework proposé repose sur une intégration de pipelines de données, d'architectures de calcul (GPU/TPU/FPGA), de model serving, d'entraînement distribué, de federated learning et de serverless AI pour soutenir des applications d'IA à grande échelle.

methodology: Le pipeline proposé combine un modèle d'apprentissage profond générant des points candidats pour chaque structure osseuse avec un modèle de ligne robuste qui en extrait les axes anatomiques, permettant le calcul automatisé de l'angle entre structures osseuses.

use-cases: Le modèle dataflow proposé permet la composition d'algorithmes multi-agents hétérogènes, par exemple DQN et PPO combinés au sein d'un même environnement, un cas d'usage que les utilisateurs finaux ne pouvaient auparavant réaliser qu'en écrivant du code système de bas niveau.

efficacy: Le framework UNet apparaît comme un choix de modèle robuste et récurrent, utilisé aussi bien pour la super-résolution d'image, la segmentation osseuse que la prédiction de paramètres liés à la santé osseuse.


## Conclusion


Un workflow hybride, cross-border, de NAS conscient du matériel (hardware-aware) fonctionnant en parallèle sur un système HPC et un dispositif edge a été présenté. Le workflow exploite les GPU puissants du système HPC pour entraîner différentes configurations de modèles avec un entraînement data-parallèle, tout en mesurant le temps d'inférence des modèles directement sur le dispositif cible réel, ce qui donne une mesure précise. Pour masquer la latence de communication, chaque architecture de modèle candidate est envoyée au dispositif d'inférence avant l'entraînement sur le système HPC. Les résultats empiriques montrent clairement que d'importantes économies en termes de temps d'inférence et de qualité du modèle (en termes de perte de test finale) peuvent être obtenues. Résultat clé : cette recherche démontre empiriquement qu'augmenter les ressources computationnelles de la boucle HPO peut conduire à une réduction de l'utilisation des ressources computationnelles lors de l'inférence sur le dispositif edge. À l'avenir, de tels workflows pourraient être utilisés pour trouver des architectures encore plus rapides (comparées aux baselines expertes) ou s'adaptant à des dispositifs edge encore plus petits, ce qui est une caractéristique importante non seulement en fabrication additive (AM) mais dans tout domaine où des modèles ML rapides sont déployés sur de petits dispositifs.

HybridGNet peut gérer les étiquettes hétérogènes dans des scénarios multi-centres, là où UNet et nnUNet échouent drastiquement UNet HT (conscient des étiquettes hétérogènes) est utile pour éviter les signaux contradictoires entre annotations manquantes et arrière-plan, mais insuffisant en cas de signaux contradictoires entre organes Les modèles basés sur des points de repère comme HybridGNet offrent un cadre simple pour gérer les structures se chevauchant, en particulier les étiquettes hétérogènes dans des scénarios multi-centres


## Synthese


L'article vise à concevoir une architecture de machine learning légère et edge-based, LightPersML, permettant aux PME e-commerce disposant de ressources limitées de déployer des systèmes de personnalisation et de recommandation sophistiqués en temps réel, jusqu'alors réservés aux grandes plateformes disposant d'infrastructures cloud coûteuses. Le contexte scientifique qui motive cette recherche est double: d'une part, la nécessité croissante de préserver la confidentialité des données client face à des réglementations et attentes toujours plus strictes, et d'autre part, la volonté de réduire les coûts d'infrastructure et la latence des systèmes de recommandation cloud traditionnels. Les objectifs spécifiques incluent l'intégration de l'apprentissage fédéré pour un traitement distribué sans centralisation des données, l'exploitation d'AWS Step Functions et API Gateway pour une orchestration évolutive, ainsi que l'évaluation comparative des performances (latence, précision) entre systèmes edge et cloud. L'hypothèse implicite testée est qu'un compromis favorable entre efficacité computationnelle et précision de recommandation est atteignable en environnement edge contraint, sans sacrifier significativement la qualité de l'expérience de personnalisation.