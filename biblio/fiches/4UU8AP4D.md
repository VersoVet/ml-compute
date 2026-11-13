# Multiple-UAV Reinforcement Learning Algorithm Based on Improved PPO in Ray Framework



## Resume


Multiple-UAV Reinforcement Learning Algorithm Based on Improved PPO in Ray Framework

Distributed multi-agent collaborative decision-making technology is the key to general artificial intelligence. This paper takes the self-developed Unity3D collaborative combat environment as the test scenario, setting a task that requires heterogeneous unmanned aerial vehicles (UAVs) to perform a distributed decision-making and complete cooperation task. Aiming at the problem of the traditional proximal policy optimization (PPO) algorithm’s poor performance in the field of complex multi-agent collaboration scenarios based on the distributed training framework Ray, the Critic network in the PPO algorithm is improved to learn a centralized value function, and the muti-agent proximal policy optimization (MAPPO) algorithm is proposed. At the same time, the inheritance training method based on course learning is adopted to improve the generalization performance of the algorithm. In the experiment, MAPPO can obtain the highest average accumulate reward compared with other algorithms and can complete the task goal with the fewest steps after convergence, which fully demonstrates that the MAPPO algorithm outperforms the state-of-the-art.

Boost the Performance of Model Training with the Ray Framework for Emerging AI Applications

Deep Learning Based Crack Detection MLOps Pipeline using Incremental Learning

An Introduction to the Ray AI Libraries

Prediction Refinement with Optical Flow for Affine Motion Compensation

Deep reinforcement learning and its applications in medical imaging and radiation therapy: a survey.

Abstract
                  Reinforcement learning takes sequential decision-making approaches by learning the policy through trial and error based on interaction with the environment. Combining deep learning and reinforcement learning can empower the agent to learn the interactions and the distribution of rewards from state-action pairs to achieve effective and efficient solutions in more complex and dynamic environments. Deep reinforcement learning (DRL) has demonstrated astonishing performance in surpassing the human-level performance in the game domain and many other simulated environments. This paper introduces the basics of reinforcement learning and reviews various categories of DRL algorithms and DRL models developed for medical image analysis and radiation treatment planning optimization. We will also discuss the current challenges of DRL and approaches proposed to make DRL more generalizable and robust in a real-world environment. DRL algorithms, by fostering the designs of the reward function, agents interactions and environment models, can resolve the challenges from scarce and heterogeneous annotated medical image data, which has been a major obstacle to implementing deep learning models in the clinic. DRL is an active research area with enormous potential to improve deep learning applications in medical imaging and radiation therapy planning.

Intent-Based Network Resource Orchestration in Space-Air-Ground Integrated Networks: A Graph Neural Networks and Deep Reinforcement Learning Approach


## Quote


First, we align LLMs with established surface-level text structures (cf. Figure 1) by leveraging an external LLM to guide or evaluate generation within a Proximal Policy Optimization (PPO) framework (Schulman et al. 2017) under a Reinforcement Learning from AI Feedback (RLAIF) paradigm (Bai et al. 2022).

Ray automatically allocates resources and concurrently executes MSA tools on CPUs, model runs, and model relaxation on a distinct GPU.


## Raw_References


he focus of unmanned aerial vehicle (UAV) path planning includes challenging tasks such as obstacle avoidance and efficient target reaching in complex environments. Building upon these fundamental challenges, an additional need exists for agents that can handle diverse missions like round-trip navigation without requiring retraining for each specific task. In our study, we present a path planning method using reinforcement learning (RL) for a fully controllable UAV agent. We combine goal-conditioned RL and curriculum learning to enable agents to progressively master increasingly complex missions, from single-target reaching to round-trip navigation.

he focus of unmanned aerial vehicle (UAV) path planning includes challenging tasks such as obstacle avoidance and efficient target reaching in complex environments. Building upon these fundamental challenges, an additional need exists for agents that can handle diverse missions like round-trip navigation without requiring retraining for each specific task. In our study, we present a path planning method using reinforcement learning (RL) for a fully controllable UAV agent. We combine goal-conditioned RL and curriculum learning to enable agents to progressively master increasingly complex missions, from single-target reaching to round-trip navigation.

CL can facilitate learning and training in the CARLA [68] simulator and target search for UAV swarms. Anzalone etal. [55] aim to learn an end-to-end urban driving policy for the CARLA driving simulator by combining the PPO algorithm with CL. In their approach, the RL phase is divided into several stages of increasing difficulty, so that the agent is guided to learn a better driving policy. The curriculum-based agent is evaluated using different metrics, cities, weather conditions, and traffic scenarios. Furthermore, Brunnbauer etal. [63] develop a multi-agent, scenario-based AD training and evaluation framework for the CARLA simulator. The results show that the proposed approach is practical for multi-agent learning and can generate auto-curricula from scenario descriptions. In a similar vein, Xiao etal. [62] use a UAV swarm for target search in disaster management scenarios. An adaptive embedded curriculum can adjust the difficulty of the task based on the success rate achieved in tra

CL can facilitate learning and training in the CARLA [68] simulator and target search for UAV swarms. Anzalone etal. [55] aim to learn an end-to-end urban driving policy for the CARLA driving simulator by combining the PPO algorithm with CL. In their approach, the RL phase is divided into several stages of increasing difficulty, so that the agent is guided to learn a better driving policy. The curriculum-based agent is evaluated using different metrics, cities, weather conditions, and traffic scenarios. Furthermore, Brunnbauer etal. [63] develop a multi-agent, scenario-based AD training and evaluation framework for the CARLA simulator. The results show that the proposed approach is practical for multi-agent learning and can generate auto-curricula from scenario descriptions. In a similar vein, Xiao etal. [62] use a UAV swarm for target search in disaster management scenarios. An adaptive embedded curriculum can adjust the difficulty of the task based on the success rate achieved in tra

Objective ML Technique Scenario [42] assist the UAV in obstacle avoidance. DRL Navigation / UAV [43] improve the agent's learning ability and performance. DRL Intelligence / AV [44] tackle sparse reward and low learning efficiency. RL Exploration / AUV [45] facilitate mapless obstacle avoidance. DRL Navigation / UAV swarm [46] improve the learning performance of RL DRL AD [47] mitigate in-flight UAV anomalies by using semi-supervised SVM AL Anomaly detection / UAV [48] develop a new path planning framework for AL AL Path planning / Semantic mapping [49] detect unknown network attacks in the UAV network. AL IDS / UAV [35] facilitate manual labeling of large-scale surveillance data. AL VTR / ITS [50] learn the decentralized flocking and obstacle avoidance policy CL Obstacle avoidance / UAV swarm [51] reduce the required training time and improve agent performance CL AD [52] enable mission planning for controlling a UAV ML Mission planning / UAV [53] address 3D object detection in AV AL O

Objective ML Technique Scenario [42] assist the UAV in obstacle avoidance. DRL Navigation / UAV [43] improve the agent's learning ability and performance. DRL Intelligence / AV [44] tackle sparse reward and low learning efficiency. RL Exploration / AUV [45] facilitate mapless obstacle avoidance. DRL Navigation / UAV swarm [46] improve the learning performance of RL DRL AD [47] mitigate in-flight UAV anomalies by using semi-supervised SVM AL Anomaly detection / UAV [48] develop a new path planning framework for AL AL Path planning / Semantic mapping [49] detect unknown network attacks in the UAV network. AL IDS / UAV [35] facilitate manual labeling of large-scale surveillance data. AL VTR / ITS [50] learn the decentralized flocking and obstacle avoidance policy CL Obstacle avoidance / UAV swarm [51] reduce the required training time and improve agent performance CL AD [52] enable mission planning for controlling a UAV ML Mission planning / UAV [53] address 3D object detection in AV AL O

Automatic CL approach in conjunction with the Twin Delayed Deterministic Policy Gradient (TD3) that breaks down UAV landing control into a series of simpler subtasks, and learns the landing tasks under different conditions of UGV motions and wind interference. Table IV summarizes the above findings. Traditional MARL setups face with performance issue when scaling up the number of agents. Curriculum learning facilitates the management of complex UAV swarm tasks, such as collision avoidance, flocking, and navigation, by gradually increasing the complexity of training scenarios. By applying curriculum learning, MARL scalability is improved but also effectively enhancing system performance in large-scale deployments. CL combined with multi-agent DRL improves learning efficiency, scalability, and the ability of UAVs to achieve safe and coordinated flight in complex environments.

Automatic CL approach in conjunction with the Twin Delayed Deterministic Policy Gradient (TD3) that breaks down UAV landing control into a series of simpler subtasks, and learns the landing tasks under different conditions of UGV motions and wind interference. Table IV summarizes the above findings. Traditional MARL setups face with performance issue when scaling up the number of agents. Curriculum learning facilitates the management of complex UAV swarm tasks, such as collision avoidance, flocking, and navigation, by gradually increasing the complexity of training scenarios. By applying curriculum learning, MARL scalability is improved but also effectively enhancing system performance in large-scale deployments. CL combined with multi-agent DRL improves learning efficiency, scalability, and the ability of UAVs to achieve safe and coordinated flight in complex environments.

Moreover, data collection [67] and UAV landing tasks require structured task and training-data organization. Seong etal. [59] address the collection of data from wireless sensor nodes to minimize the Age of Information during data collection, while considering the energy sustainability of UAVs. They introduce Multi-Agent Reinforcement Learning (MARL) in combination with CL and an evolutionary strategy to improve the performance of traditional MARL setups as the number of agents increases. Their method promotes MARL scalability and integrates energy-efficient charging mechanisms that improve system performance in large-scale deployments. Moreover, the collaborative autonomous landing of a quadrotor UAV on a moving Unmanned Ground Vehicle (UGV) is challenging due to the need for accurate real-time tracking of the UGV and the adjustment of the landing policy. Wang et al. [60] propose the Landing Vision System to offer rapid localization and pose estimation of the UGV. Then, they design an

Moreover, data collection [67] and UAV landing tasks require structured task and training-data organization. Seong etal. [59] address the collection of data from wireless sensor nodes to minimize the Age of Information during data collection, while considering the energy sustainability of UAVs. They introduce Multi-Agent Reinforcement Learning (MARL) in combination with CL and an evolutionary strategy to improve the performance of traditional MARL setups as the number of agents increases. Their method promotes MARL scalability and integrates energy-efficient charging mechanisms that improve system performance in large-scale deployments. Moreover, the collaborative autonomous landing of a quadrotor UAV on a moving Unmanned Ground Vehicle (UGV) is challenging due to the need for accurate real-time tracking of the UGV and the adjustment of the landing policy. Wang et al. [60] propose the Landing Vision System to offer rapid localization and pose estimation of the UGV. Then, they design an


## Discussion


Les auteurs proposent une approche d’alignement par apprentissage par renforcement (PPO) qui combine deux modèles de récompense — l’un portant sur la fluidité de surface, l’autre sur la structure discursive globale — afin de produire des textes longs plus clairs et plus cohérents, surpassant des baselines RLHF. Les expériences d’évaluation (jugement GPT-4O sur essais, n=1000 prompts ; summarization GOVREPORT) indiquent que l’alignement structurel dépasse systématiquement le modèle d’instruction de base et la baseline RLHF_OA, l’alignement au niveau graphe (SA_G) apportant les gains les plus marqués. L’alignement séquentiel en deux étapes (SA_S→G, SA_G→S) améliore légèrement la qualité des essais, mais les gains restent marginaux au regard du coût computationnel additionnel. Sur le plan méthodologique, l’évaluateur de structure textuelle (QWEN2-72B-INSTRUCT-AWQ, servi via SGLang) et le scoring discursif au niveau graphe (motifs RST et classificateur Longformer, enrichi de 5K générations négatives) ont été intégrés en ligne dans un pipeline TRL/PPO ; les modèles de politique convergent vers l’optimisation de la récompense après environ 7K épisodes.

Les auteurs présentent une approche RLAIF fondée sur PPO qui aligne QWEN2-1.5B-INSTRUCT à l’aide de deux modèles de récompense complémentaires, l’un évaluant les propriétés textuelles de surface et l’autre la structure discursive globale. L’évaluateur de surface repose sur QWEN2-72B-INSTRUCT-AWQ, déployé avec SGLang sur huit GPU NVIDIA A100 de 80 Go, tandis que l’évaluation structurelle mobilise des motifs discursifs et un classifieur Longformer enrichi par 5 000 essais générés comme exemples négatifs. Selon les auteurs, les variantes structurellement alignées produisent des textes longs plus clairs et cohérents que les baselines RLHF, l’approche fondée sur les graphes obtenant les meilleures performances rapportées en génération d’essais et sur GOVREPORT; toutefois, l’extrait ne fournit ni scores comparatifs complets, ni intervalles de confiance, ni valeurs p. Les travaux futurs envisagent un passage à des modèles et corpus plus vastes ainsi que l’intégration d’autres cadres linguistiques afin d’affiner les signaux de récompense et d’améliorer la robustesse [Unknown](zotero://select/library/items/9TSMZFWB).


## Methodologie


Le design retenu est celui d'un framework logiciel open-source combinant Project Chrono (moteur physique multi-corps haute-fidélité) et Ray (calcul distribué), exposé via une interface Gymnasium standardisée; chaque instance de simulation est encapsulée dans un acteur Ray indépendant, orchestré par un processus pilote central assurant la synchronisation via ray.get, avec un hyperparamètre n_s contrôlant la fréquence de communication. L'évaluation repose sur deux études de cas computationnelles sans population humaine ou animale. La première (locomotion quadrupède) entraîne une politique PPO (bibliothèque RSL-RL) de suivi de vitesse commandée, avec observation en R^45, action en R^12 (12 cibles de position articulaire, 3 par jambe), réseaux acteur-critique MLP [512, 256, 128] à activation ELU, comparant n_env ∈ {1, 8, 16}; une expérience de transfert additionnelle affine la politique vers un terrain déformable CRM (taux d'apprentissage 10^-5, clip parameter 0.02, KL désiré 0.001, norme de gradient maximale 0.5, pas de temps interne 5×10^-4 s). La seconde étude de cas (atterrisseur planétaire, système multi-corps à 25 éléments) applique une optimisation bayésienne via Optuna et l'échantillonneur TPE sur trois paramètres de conception θ = {f_y, β, α_2}, minimisant une fonction de coût combinant décélération maximale du centre de masse et fraction d'énergie potentielle dissipée, évaluée sur terrain rigide et terrain déformable CRM selon quatre configurations de parallélisme. Les outcomes primaires sont l'efficacité d'apprentissage/optimisation en temps réel (wall-clock time) et la qualité de la solution obtenue (récompense, erreur de suivi MSE, coût de conception J(θ)), comparés entre niveaux de parallélisme croissants.


## Insight


primary_outcomes: L'augmentation du nombre d'environnements parallèles (n_env = 1, 8, 16) améliore significativement l'efficacité d'apprentissage en temps réel pour la locomotion quadrupède, n_env=16 convergeant le plus rapidement vers la récompense la plus élevée.
Dans l'étude de cas de locomotion quadrupède, l'entraînement PPO (via RSL-RL) d'une politique de suivi de vitesse commandée, opérant sur un espace d'observation en R^45 et un espace d'action en R^12 (cibles de position articulaire pour 3 articulations par jambe) avec des réseaux acteur-critique MLP [512, 256, 128] à activations ELU, a été comparé pour trois niveaux de parallélisme (n_env ∈ {1, 8, 16}). Les résultats montrent une relation monotone entre le degré de parallélisme et l'efficacité d'apprentissage en temps réel (wall-clock), la configuration n_env=16 atteignant la récompense la plus élevée dans le délai le plus court parmi les trois configurations testées. Ce résultat démontre empiriquement que la distribution des instances de simulation sur plusieurs acteurs Ray permet de collecter davantage d'expérience par unité de temps physique, sans que l'article ne rapporte cependant de valeurs numériques précises de récompense ni d'intervalles de confiance statistiques associés à ces comparaisons.


## Table


Tableau: Key Techniques for Navigation and Data Collection
| Ref | Technique |  | Application | Strengths and Limitations |
| --- | --- | --- | --- | --- | --- |
| [50] | Curriculum- | Flocking and ob- | Learns decentralized policies; |
|  | based | Multi- | stacle avoidance | requires knowledge transfer |
|  | agent DRL |  | for UAVs | mechanisms. |
| [54] | Curriculum | Collision-free | Scalable to large swarms; |
|  | Learning | with | flocking for large | gradually increases swarm |
|  | Multi-agent DRL | UAV swarms | size. |
| [58] | Curriculum- | UAV navigation | Improves navigation reliabil- |
|  | based DRL | in complex 3D | ity; relies on human-defined |
|  |  |  | environments | curriculum. |
| [59] | MARL with Cur- | Data collection | Promotes MARL scalability; |
|  | riculum Learning | from | wireless | integrates | energy-efficient |
|  | and Evolutionary | sensor | nodes | charging | mechanisms; |
|  | Strategy |  | with UAVs | enhances AoI minimization |
|  |  |  |  |  | and energetic sustainability. |
| [60] | Automatic |  | Collaborative | Offers rapid localization and |
|  | Curriculum | autonomous | pose estimation; handles |
|  | Learning | with | landing of UAV | different UGV motions and |
|  | TD3 |  | on UGV |  | wind interference; breaks |
|  |  |  |  |  | down tasks into simpler |
|  |  |  |  |  | subtasks. |

Tableau: Key Techniques for Navigation and Data Collection
| Ref | Technique |  | Application | Strengths and Limitations |
| --- | --- | --- | --- | --- | --- |
| [50] | Curriculum- | Flocking and ob- | Learns decentralized policies; |
|  | based | Multi- | stacle avoidance | requires knowledge transfer |
|  | agent DRL |  | for UAVs | mechanisms. |
| [54] | Curriculum | Collision-free | Scalable to large swarms; |
|  | Learning | with | flocking for large | gradually increases swarm |
|  | Multi-agent DRL | UAV swarms | size. |
| [58] | Curriculum- | UAV navigation | Improves navigation reliabil- |
|  | based DRL | in complex 3D | ity; relies on human-defined |
|  |  |  | environments | curriculum. |
| [59] | MARL with Cur- | Data collection | Promotes MARL scalability; |
|  | riculum Learning | from | wireless | integrates | energy-efficient |
|  | and Evolutionary | sensor | nodes | charging | mechanisms; |
|  | Strategy |  | with UAVs | enhances AoI minimization |
|  |  |  |  |  | and energetic sustainability. |
| [60] | Automatic |  | Collaborative | Offers rapid localization and |
|  | Curriculum | autonomous | pose estimation; handles |
|  | Learning | with | landing of UAV | different UGV motions and |
|  | TD3 |  | on UGV |  | wind interference; breaks |
|  |  |  |  |  | down tasks into simpler |
|  |  |  |  |  | subtasks. |

Tableau: Key Techniques for AD and UAV Swarm Navigation
| Ref | Technique |  | Application | Strengths and Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [51] | CL with DRL | AD at urban in- | Reduces training time; im- |
|  |  |  | tersections | proves performance; uses au- |
|  |  |  |  |  | tomated curriculum creation; |
|  |  |  |  |  | avoids human handcrafting. |
| [62] | Adaptive Embed- | UAV | swarm | Adjusts task difficulty based |
|  | ded Curriculum | target | search | on success rate; handles |
|  |  |  | in | disaster | sparse rewards. |
|  |  |  | management |
| [55] | PPO with Cur- | Urban | driving | Guides agent to better policy; |
|  | riculum Learning | policy | for | improves learning efficiency. |
|  |  |  | CARLA |  |
|  |  |  | simulator |  |
| [36] | RD-ACPPO |  | Self-driving tasks | Adaptive curriculum learning; |
|  |  |  | at unsignalized | allocates importance weights |
|  |  |  | intersections | dynamically; demonstrates ef- |
|  |  |  |  |  | fective curriculum transition |
|  |  |  |  |  | timings and high task success |
|  |  |  |  |  | rate. |
| [63] | Multi-agent |  | CARLA simula- | Practical for multi-agent |
|  | scenario-based | tor for AD | learning; generates auto- |
|  | framework |  |  |  | curricula | from | scenario |
|  |  |  |  |  | descriptions. |
| [64] | Curriculum |  | Motion planning | Incorporates map and traffic |
|  | Learning | with | in AD |  | rule information; decomposes |
|  | GNN-RL |  |  |  | learning task into sub-tasks |
|  |  |  |  |  | with increasing difficulty; in- |
|  |  |  |  |  | cludes rewards for temporal- |
|  |  |  |  |  | logic-based traffic rules. |

Tableau: Key Techniques for AD and UAV Swarm Navigation
| Ref | Technique |  | Application | Strengths and Limitations |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [51] | CL with DRL | AD at urban in- | Reduces training time; im- |
|  |  |  | tersections | proves performance; uses au- |
|  |  |  |  |  | tomated curriculum creation; |
|  |  |  |  |  | avoids human handcrafting. |
| [62] | Adaptive Embed- | UAV | swarm | Adjusts task difficulty based |
|  | ded Curriculum | target | search | on success rate; handles |
|  |  |  | in | disaster | sparse rewards. |
|  |  |  | management |
| [55] | PPO with Cur- | Urban | driving | Guides agent to better policy; |
|  | riculum Learning | policy | for | improves learning efficiency. |
|  |  |  | CARLA |  |
|  |  |  | simulator |  |
| [36] | RD-ACPPO |  | Self-driving tasks | Adaptive curriculum learning; |
|  |  |  | at unsignalized | allocates importance weights |
|  |  |  | intersections | dynamically; demonstrates ef- |
|  |  |  |  |  | fective curriculum transition |
|  |  |  |  |  | timings and high task success |
|  |  |  |  |  | rate. |
| [63] | Multi-agent |  | CARLA simula- | Practical for multi-agent |
|  | scenario-based | tor for AD | learning; generates auto- |
|  | framework |  |  |  | curricula | from | scenario |
|  |  |  |  |  | descriptions. |
| [64] | Curriculum |  | Motion planning | Incorporates map and traffic |
|  | Learning | with | in AD |  | rule information; decomposes |
|  | GNN-RL |  |  |  | learning task into sub-tasks |
|  |  |  |  |  | with increasing difficulty; in- |
|  |  |  |  |  | cludes rewards for temporal- |
|  |  |  |  |  | logic-based traffic rules. |


## Raw_Human-In-The-Loop_Reinforcement_Learning


Li etal. [42] develop a HITL-DRL framework for UAV navigation in large-scale 3D complex environments. This work aims to enable the UAV to avoid obstacles automatically during flight. The role of HITL is to assist the UAV in obstacle avoidance by dynamically switching between multiple UAV reward functions in different situations. The combined approach improves the success rate and navigation efficiency. In a similar vein, Karumanchi etal. [70] address the problem of autonomous UAV navigation and develop a practical solution based on Preference-based Reinforcement Learning (PbRL). In PbRL, the manual construction of the reward function is replaced with human feedback. A human is presented with a pair of trajectories followed by the RL agent and is asked to indicate a preference for one over the other. The PbRL algorithm then computes a policy or action sequence using only the set of preferences collected over different trajectories.

Li etal. [42] develop a HITL-DRL framework for UAV navigation in large-scale 3D complex environments. This work aims to enable the UAV to avoid obstacles automatically during flight. The role of HITL is to assist the UAV in obstacle avoidance by dynamically switching between multiple UAV reward functions in different situations. The combined approach improves the success rate and navigation efficiency. In a similar vein, Karumanchi etal. [70] address the problem of autonomous UAV navigation and develop a practical solution based on Preference-based Reinforcement Learning (PbRL). In PbRL, the manual construction of the reward function is replaced with human feedback. A human is presented with a pair of trajectories followed by the RL agent and is asked to indicate a preference for one over the other. The PbRL algorithm then computes a policy or action sequence using only the set of preferences collected over different trajectories.