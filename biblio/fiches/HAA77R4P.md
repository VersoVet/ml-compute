# Designing a Kubernetes Operator for Machine Learning Applications



## Resume


Designing a Kubernetes Operator for Machine Learning Applications

The Machine Learning Pipeline

A Lightweight Machine Learning Pipeline for LiDAR-simulation

Production Machine Learning Pipelines

Machine learning for aerial image labeling

Intelligence Orchestration

Composable machine learning pipeline for fast deployment with neural architecture search

Deploying neural networks in real-time, low-latency, and power-constrained environments, such as high-speed imaging systems, requires efficient hardware-aware machine learning workflows. This thesis presents a composable framework designed to automate and accelerate the design, evaluation, and deployment of optimized neural network models for FPGA-based inference. The architecture is implemented using a modular, containerized approach, where each stage of the machine learning lifecycle is encapsulated within dedicated Docker containers. These are orchestrated using Kubernetes, supporting horizontal scalability and efficient parallel experimentation across diverse environments. The pipeline integrates QKeras for model pruning and precision tuning, HLS4ML for high-level synthesis (HLS), and Vivado for hardware compilation and resource reporting. The system aims to minimize latency and power consumption while maintaining accuracy, making it ideal for real-time applications. A specific use

End-to-End MLOps Pipeline on Kubernetes for Scalable Healthcare Applications

Deep Lake: a Lakehouse for Deep Learning

Deep Learning Pipeline

Deep Learning and Data Labeling for Medical Applications

MLHOps: Machine Learning for Healthcare Operations

Predictive Orchestration: Machine Learning Pipelines for Proactive Middleware Scaling

Generation of training dataset for deep-learning noise reduction


## Raw_Kubernetes


Kubernetes [43] is a system used to configure, deploy and manage containers. Interaction with the system is done through files named manifests declaring a state of the application. Kubernetes then either deploy or modify the system so that it matches the description. Kubernetes shares a good part of configurations options contained in Compose but adds its own structures on top of them. Kubernetes' more abstract and particular concepts are sometimes substituted to Compose concepts that are relatively close to the real network entities. For instance, opening passage from the outside to a particular service in Compose is done through the "Port" keyword in the service description. In Kubernetes a particular object named service will act as an intermediary. Kubernetes has the ability to define interior and exterior interfaces with ports but can also manage the routing of endpoints through a specific object called Ingress. Requests going though the Ingress resource are routed to undetermined

Kubernetes [43] is a system used to configure, deploy and manage containers. Interaction with the system is done through files named manifests declaring a state of the application. Kubernetes then either deploy or modify the system so that it matches the description. Kubernetes shares a good part of configurations options contained in Compose but adds its own structures on top of them. Kubernetes' more abstract and particular concepts are sometimes substituted to Compose concepts that are relatively close to the real network entities. For instance, opening passage from the outside to a particular service in Compose is done through the "Port" keyword in the service description. In Kubernetes a particular object named service will act as an intermediary. Kubernetes has the ability to define interior and exterior interfaces with ports but can also manage the routing of endpoints through a specific object called Ingress. Requests going though the Ingress resource are routed to undetermined


## Raw_A._Training


eural network training.

eural network training.


## Raw_Studied_Microservice_Adls_:_Toolboxes


its features such as service discovery, network communication and isolation or security features. It also adds functionalities on the system such as scaling. Kubernetes' files, known as manifests, are intended to be used to interact with a Kubernetes running system that manages resources, taking away the infrastructural concern of deciding where and how to set up the modifications, from the user. Setting up the Kubernetes system has a relatively high initial cost but once its done the infrastructure is made completely abstract. What is left for the user to do is simply to describe what it desires and transmit it to the Kubernetes interface that will take the appropriate measures to make so that the real state of the running application match the description. Kubernetes is often refered as an orchestrator, which is appropriate if we think of orchestration as dealing "with how different services are composed into a coherent whole" [3]. Kubernetes fits that broad and blurry definition by

its features such as service discovery, network communication and isolation or security features. It also adds functionalities on the system such as scaling. Kubernetes' files, known as manifests, are intended to be used to interact with a Kubernetes running system that manages resources, taking away the infrastructural concern of deciding where and how to set up the modifications, from the user. Setting up the Kubernetes system has a relatively high initial cost but once its done the infrastructure is made completely abstract. What is left for the user to do is simply to describe what it desires and transmit it to the Kubernetes interface that will take the appropriate measures to make so that the real state of the running application match the description. Kubernetes is often refered as an orchestrator, which is appropriate if we think of orchestration as dealing "with how different services are composed into a coherent whole" [3]. Kubernetes fits that broad and blurry definition by

taking charge of a multiplicity of strong requirements for a microservice application such as service discovery, scaling (both vertical and horizontal), message routing and many other aspects. It also fits the more precise definition of an orchestrator specifying that "in particular, it specifies the order in which the services are invoked, and the conditions under which a certain service may or may not be invoked¨ [3]. It is to be precised though that Kubernetes does take charge of that aspect from the infrastructural point of view, for instance through load-balancing and routing, but does not get into the control flow of application logic which was historically the initial subject of orchestration. However, to be effective the described Kubernetes system description must match the application logic.

taking charge of a multiplicity of strong requirements for a microservice application such as service discovery, scaling (both vertical and horizontal), message routing and many other aspects. It also fits the more precise definition of an orchestrator specifying that "in particular, it specifies the order in which the services are invoked, and the conditions under which a certain service may or may not be invoked¨ [3]. It is to be precised though that Kubernetes does take charge of that aspect from the infrastructural point of view, for instance through load-balancing and routing, but does not get into the control flow of application logic which was historically the initial subject of orchestration. However, to be effective the described Kubernetes system description must match the application logic.


## Raw_J_Practical_Guidelines


Interpreting outputs.

Interpreting outputs.


## Raw_Services


in microservices have brought orchestrating components e.g. Kubernetes.

in microservices have brought orchestrating components e.g. Kubernetes.


## Raw_Cuda:


-cuBLAS: Optimized linear algebra library for matrix operations.

-cuBLAS: Optimized linear algebra library for matrix operations.


## Raw_Behavior,_Analysis_And_Evaluation


n mitigated by creating behaviors as modules of Concerns that are sometimes affected by default but can always be deactivated. We are confident that if done carefully work on this aspect of the language can bring many benefits while keeping its generality and openness to specific systems and future evolutions. Static analysis leading to architecture evaluation, positive suggestions and mistakes corrections are realistic expectations but another major domain of application would be operation management through implication of online rules for orchestrators such as Kubernetes controllers.

n mitigated by creating behaviors as modules of Concerns that are sometimes affected by default but can always be deactivated. We are confident that if done carefully work on this aspect of the language can bring many benefits while keeping its generality and openness to specific systems and future evolutions. Static analysis leading to architecture evaluation, positive suggestions and mistakes corrections are realistic expectations but another major domain of application would be operation management through implication of online rules for orchestrators such as Kubernetes controllers.