# ShuffleInfer: Disaggregate LLM Inference for Mixed Downstream Workloads



## Resume


ShuffleInfer: Disaggregate LLM Inference for Mixed Downstream Workloads

Transformer-based large language model (LLM) inference serving is now the backbone of many cloud services. LLM inference consists of a prefill phase and a decode phase. However, existing LLM deployment practices often overlook the distinct characteristics of these phases, leading to significant interference. To mitigate interference, our insight is to carefully schedule and group inference requests based on their characteristics. We realize this idea in ShuffleInfer through three pillars. First, it partitions prompts into fixed-size chunks so that the accelerator always runs close to its computation-saturated limit. Second, it disaggregates prefill and decode instances so each can run independently. Finally, it uses a smart two-level scheduling algorithm augmented with predicted resource usage to avoid decode scheduling hotspots. Results show that ShuffleInfer improves time-to-first-token (TTFT), job completion time (JCT), and inference efficiency in terms of performance per dollar by a large margin, e.g., it uses 38% less resources all the while lowering average TTFT and average JCT by 97% and 47%, respectively.

Machine Learning Experiment Management With MLFlow

<jats:p/>

RLlib Flow: Distributed Reinforcement Learning is a Dataflow Problem

Researchers and practitioners in the field of reinforcement learning (RL) frequently leverage parallel computation, which has led to a plethora of new algorithms and systems in the last few years. In this paper, we re-examine the challenges posed by distributed RL and try to view it through the lens of an old idea: distributed dataflow. We show that viewing RL as a dataflow problem leads to highly composable and performant implementations. We propose RLlib Flow, a hybrid actor-dataflow programming model for distributed RL, and validate its practicality by porting the full suite of algorithms in RLlib, a widely adopted distributed RL library. Concretely, RLlib Flow provides 2-9 code savings in real production code and enables the composition of multi-agent algorithms not possible by end users before. The open-source code is available as part of RLlib at https://github.com/ray-project/ray/tree/master/rllib.

LLM-Based Generation of Low-Code Development Platforms

Investigating Retrieval Augmented Generation for LLM-Based Code Generation

Intelligent Workflow Orchestration Using Low-Code BPM Platforms and Machine Learning: Automating Lending Operations in Member-Centric Financial Institutions

An Open-Source Framework for LLM-Based Parallel Python Code Generation and Benchmarking

LLM-based and Retrieval-Augmented Control Code Generation


## Quote


This design enables standardized output, section-level reproducibility, and interoperability across multiple LLMs without retraining 28 .

In this architecture, a structured three-step workflow comprising initial LLM assessment, function calling to invoke specialized open-source deep learning tools, [24,25] and LLM reflection integrating tool outputs anchors predictions in deterministic, reproducible measurements while preserving the model's capacity for high-level clinical reasoning.

In this architecture, a structured three-step workflow comprising initial LLM assessment, function calling to invoke specialized open-source deep learning tools, [24,25] and LLM reflection integrating tool outputs anchors predictions in deterministic, reproducible measurements while preserving the model's capacity for high-level clinical reasoning.

instead of applying LLM iteratively to generate intermediate steps until the full article is obtained, we include the intermediate steps into a mixture of training data and directly fine-tune an LLM to generate all of them in one turn.

Finally, we discuss existing DNN modeling tools and introduce Stream, which we extend to support training workloads across various hardware architectures.

Finally, we discuss existing DNN modeling tools and introduce Stream, which we extend to support training workloads across various hardware architectures.

Our experiments highlight a number of promising research directions, including (1) enhancing retrieval and refining retrieval integrations in LLMs, (2) developing long-context LLMs, and (3) advancing LLMs' ability to synthesize multiple sources.


## Synthese


Cette section introductive expose le paradoxe central motivant RLlib Flow : bien que les algorithmes d'apprentissage par renforcement (RL) distribué soient définis à un haut niveau d'abstraction mathématique, leurs implémentations restent ancrées dans le passage de messages bas niveau, ce qui crée une barrière d'entrée élevée pour les praticiens non spécialistes des systèmes distribués. Les bibliothèques existantes (Acme, RLgraph, RLlib, Coach) ne permettent l'exécution des algorithmes que dans des schémas de distribution prédéfinis, limitant la programmabilité et la capacité de personnalisation nécessaires face à la diversité des tâches RL (mono-agent, multi-agent, méta-apprentissage). Les auteurs proposent RLlib Flow, un modèle hybride combinant acteurs et dataflow, inspiré des systèmes de traitement de données en continu, qui expose explicitement des références aux processus acteurs tout en autorisant un passage de messages limité entre eux via des opérateurs de séquencement et de concurrence. Ce modèle vise à concilier généralité, haut niveau d'abstraction et flexibilité de programmation, contrairement aux approches existantes qui doivent sacrifier l'une de ces dimensions.


## Methodologie


Cette section introductive expose le paradoxe central motivant RLlib Flow : bien que les algorithmes d'apprentissage par renforcement (RL) distribué soient définis à un haut niveau d'abstraction mathématique, leurs implémentations restent ancrées dans le passage de messages bas niveau, ce qui crée une barrière d'entrée élevée pour les praticiens non spécialistes des systèmes distribués. Les bibliothèques existantes (Acme, RLgraph, RLlib, Coach) ne permettent l'exécution des algorithmes que dans des schémas de distribution prédéfinis, limitant la programmabilité et la capacité de personnalisation nécessaires face à la diversité des tâches RL (mono-agent, multi-agent, méta-apprentissage). Les auteurs proposent RLlib Flow, un modèle hybride combinant acteurs et dataflow, inspiré des systèmes de traitement de données en continu, qui expose explicitement des références aux processus acteurs tout en autorisant un passage de messages limité entre eux via des opérateurs de séquencement et de concurrence. Ce modèle vise à concilier généralité, haut niveau d'abstraction et flexibilité de programmation, contrairement aux approches existantes qui doivent sacrifier l'une de ces dimensions.


## Raw_B._Natural_Language_Processing


At the opposite end of the computational spectrum, Large Language Models (LLMs) such as GPT-2 represent the highperformance workloads typical of cloud-scale accelerators. The workload consists of a standard Transformer architecture configured with a fixed sequence length and a causal attention mask. For the hardware architecture, we use Fuse-Max [30] as a recent architecture that can easily be modeled in Stream [39]. A possible HDA representation is shown in Figure 7. This architecture is composed of a large array of Multiply-Accumulate (MAC) elements designed as an outputstationary dataflow accelerator and a large vector array. Both arrays' memories are linked together and they can access a large on-chip buffer that can interact with an off-chip memory. As the architecture consists of two distinct cores, an outputstationary dataflow core and a SIMD core, we primarily employ pipeline parallelism to enable efficient operand transfer and overlap computation between them. We evaluate the

At the opposite end of the computational spectrum, Large Language Models (LLMs) such as GPT-2 represent the highperformance workloads typical of cloud-scale accelerators. The workload consists of a standard Transformer architecture configured with a fixed sequence length and a causal attention mask. For the hardware architecture, we use Fuse-Max [30] as a recent architecture that can easily be modeled in Stream [39]. A possible HDA representation is shown in Figure 7. This architecture is composed of a large array of Multiply-Accumulate (MAC) elements designed as an outputstationary dataflow accelerator and a large vector array. Both arrays' memories are linked together and they can access a large on-chip buffer that can interact with an off-chip memory. As the architecture consists of two distinct cores, an outputstationary dataflow core and a SIMD core, we primarily employ pipeline parallelism to enable efficient operand transfer and overlap computation between them. We evaluate the


## Raw_Increasing_Context_Window


th to 1 billion tokens. LongLoRA [189] proposes shift-short attention, used during fine-tuning to reduce dense attention costs. However, the model during inference uses dense attention and achieves similar performance as full attention fine-tuning. Extrapolation without Training: LM-Infinite [186] and parallel context windows (PCW) [190] show length extrapolation is possible using pre-trained LLMs. LM-Infinite suggested Λshaped attention applied within the original context window limits. Likewise, PCW chunks larger inputs into the pre-trained context lengths and applies the same positional encodings to each chunk.


## Raw_Methods


Baselines To provide a comprehensive comparison, we select several representative LLMs as baselines for our experiments. These baselines include proprietary models such as GPT-4o-mini and GPT-4o, as well as open-source models like Qwen2-7B (qwe, 2024), Llama-3.1-8B, and Llama-3.1-70B (Dubey et al., 2024). Additionally, we apply in-context learning (ICL) (Dong et al., 2022) with one random-sampled instance to these baselines to better adapt them for workflow orchestration.

Baselines To provide a comprehensive comparison, we select several representative LLMs as baselines for our experiments. These baselines include proprietary models such as GPT-4o-mini and GPT-4o, as well as open-source models like Qwen2-7B (qwe, 2024), Llama-3.1-8B, and Llama-3.1-70B (Dubey et al., 2024). Additionally, we apply in-context learning (ICL) (Dong et al., 2022) with one random-sampled instance to these baselines to better adapt them for workflow orchestration.


## Raw_Large_Language_Models_And_Agentic_Ai_Framework


bles the LLM to determine which tools to invoke and in what order, based on input and prompt, rather than following a fixed sequential pipeline. In the third step, the LLM received its initial impression alongside all deep learning model outputs and generated a final integrated diagnostic interpretation and structured report. All combinations of dataset (ORIGA, RIM-ONE-v3), field of view (uncropped, cropped), workflow (LLM-alone, agentic), and LLM (Gemini 2.5 Flash, GPT-5.4 mini) were evaluated, resulting in 16 experimental conditions.

bles the LLM to determine which tools to invoke and in what order, based on input and prompt, rather than following a fixed sequential pipeline. In the third step, the LLM received its initial impression alongside all deep learning model outputs and generated a final integrated diagnostic interpretation and structured report. All combinations of dataset (ORIGA, RIM-ONE-v3), field of view (uncropped, cropped), workflow (LLM-alone, agentic), and LLM (Gemini 2.5 Flash, GPT-5.4 mini) were evaluated, resulting in 16 experimental conditions.


## Raw_Related_Work


ne applications (Huang et al., 2024), enterprise automation (Wornow et al., 2024), financial question answering (Zeng et al., 2023), and data analysis (Li et al., 2024). Despite relying on advanced LLMs (e.g., GPT-4), these approaches have often exhibited suboptimal performance, highlighting challenges faced by existing LLMs in workflow orchestration. While Li et al. (2024) made an effort to fine-tune Mixtral-8×7B (Jiang et al., 2024), it could only orchestrate sequential workflows with an average of 15.6 actions, remaining insufficient for real-world requirements. This work addresses a critical gap by proposing WorkflowLLM framework to enhance the workflow orchestration capabilities of LLMs to meet real-world demands.

ne applications (Huang et al., 2024), enterprise automation (Wornow et al., 2024), financial question answering (Zeng et al., 2023), and data analysis (Li et al., 2024). Despite relying on advanced LLMs (e.g., GPT-4), these approaches have often exhibited suboptimal performance, highlighting challenges faced by existing LLMs in workflow orchestration. While Li et al. (2024) made an effort to fine-tune Mixtral-8×7B (Jiang et al., 2024), it could only orchestrate sequential workflows with an average of 15.6 actions, remaining insufficient for real-world requirements. This work addresses a critical gap by proposing WorkflowLLM framework to enhance the workflow orchestration capabilities of LLMs to meet real-world demands.


## Raw_Training_Strategies


Training models at a huge scale require tricks to reduce training costs, avoid loss divergence, and achieve better performance. We summarize and discuss some of these key tricks used in different LLMs. Mixed Precision: It is a famous method for LLMs to reduce memory usage and improve training efficiency. In mixed precision, forward and backward passes are performed in FP16 format whereas optimizer states and master weights are kept in FP32 format [120]. A drawback associated with this format change is training instability due to a smaller value range resulting in loss spikes [33]. An alternative to FP16 is BF16 which has a comparatively larger range and performs precisionsensitive operations like gradient accumulation and softmax in FP32 [13]. BF16 has better performance and training stability but uses more memory and is supported on specific hardware, for example, A100 GPUs. Therefore, its adoption in LLMs is limited.


## Conclusion


RLlib Flow, un modèle de programmation hybride actor-dataflow pour le RL distribué, simplifie la compréhension, le débogage et la personnalisation des algorithmes RL distribués RLlib Flow offre une performance comparable aux algorithmes de référence implémentés directement sur des primitives actor/RPC de bas niveau RLlib Flow permet des cas d'usage complexes multi-agents et de meta-learning auparavant impossibles pour les utilisateurs finaux RLlib Flow réduit les lignes de code pour l'exécution distribuée dans une bibliothèque RL de production de 2-9× RLlib Flow est disponible en open source dans le projet RLlib et pourrait informer la conception de futures bibliothèques RL


## Raw_Deployment


2) Layer-Fused Scheduling: Layer-fused scheduling is a set of techniques that leverages the cross-layer opportunities inherent in deep neural networks to enhance performance, reduce latency, and lower energy and memory consumption. This approach operates by computing only partial feature maps of a layer and immediately utilizing these partial results for subsequent layers. DNNFusion [31] classifies deep learning operators into mapping types (One-to-One, One-to-Many, Many-to-Many, Reorganize, Shuffle) based on the relationship between input and output elements. Fusion opportunities are analyzed using a compatibility framework that categorizes operator pairs as profitable, unprofitable, or requiring profiling based on their mapping types. The operators are then merged until no more fusion is profitable.

2) Layer-Fused Scheduling: Layer-fused scheduling is a set of techniques that leverages the cross-layer opportunities inherent in deep neural networks to enhance performance, reduce latency, and lower energy and memory consumption. This approach operates by computing only partial feature maps of a layer and immediately utilizing these partial results for subsequent layers. DNNFusion [31] classifies deep learning operators into mapping types (One-to-One, One-to-Many, Many-to-Many, Reorganize, Shuffle) based on the relationship between input and output elements. Fusion opportunities are analyzed using a compatibility framework that categorizes operator pairs as profitable, unprofitable, or requiring profiling based on their mapping types. The operators are then merged until no more fusion is profitable.