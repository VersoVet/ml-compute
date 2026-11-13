# ROSA: A Robotics Foundation Model Serving System for Robot Factories



## Resume


ROSA: A Robotics Foundation Model Serving System for Robot Factories

Robotics foundation models (RFMs) are making general-purpose robots increasingly practical for factory deployments. While RFM serving systems are central to this vision, existing systems are largely shaped by a single-robot, single-model assumption: inference is treated as an edge-computing problem handled by an on-robot or dedicated nearby GPU, and the serving objective is to minimize the latency of a single action model. In this paper, we propose ROSA, an RFM serving system for robot factories designed around three key principles. First, ROSA adopts shared GPU-pool serving, allowing a fleet of robots to access powerful server-class GPUs over the network in order to improve inference performance, battery duration, and GPU utilization. Second, ROSA provides a robotics-aware programming abstraction and system design that supports multi-model pipelines, per-task performance requirements, and failure handling. Third, ROSA uses factory-objective-driven scheduling to maximize SLO-qualified

Integration and Deployment of Model Serving Framework at Production Scale

Editorial: Synergizing large language models and computational intelligence for advanced robotic systems.

Model based document and report generation for systems engineering

Towards a Modular Architecture for Science Factories

Advances in robotic automation, high-performance computing (HPC), and artificial intelligence (AI) encourage us to conceive of science factories: large, general-purpose computation- and AI-enabled self-driving laboratories (SDLs) with the generality and scale needed both to tackle large discovery problems and to support thousands of scientists. Science factories require modular hardware and software that can be replicated for scale and (re)configured to support many applications. To this end, we propose a prototype modular science factory architecture in which reconfigurable modules encapsulating scientific instruments are linked with manipulators to form workcells, that can themselves be combined to form larger assemblages, and linked with distributed computing for simulation, AI model training and inference, and related tasks. Workflows that perform sets of actions on modules can be specified, and various applications, comprising workflows plus associated computational and data manip


## Quote


a graphical framework called RMA (robot modeldriven architecture) for designing the configuration of a LEGO Mindstorms robot [1] and describing their behaviour from a high level of abstraction

a graphical framework called RMA (robot modeldriven architecture) for designing the configuration of a LEGO Mindstorms robot [1] and describing their behaviour from a high level of abstraction

The science factory architecture that we present here is a work in progress. Its modularity makes it easy to extend with new instruments, AI and other computational methods, and new workflows and applications, and its simplicity enables rapid deployment in new settings.

The science factory architecture that we present here is a work in progress. Its modularity makes it easy to extend with new instruments, AI and other computational methods, and new workflows and applications, and its simplicity enables rapid deployment in new settings.

The work lays the foundation for a metastructure with tunable material properties via the established mathematical model, potentially for metamaterials and soft robotics (e.g., replacing string with shape memory alloy)


## Raw_Overview_Of_Soa_Modeling_Approaches


s a modeling technique for developing and building SOA-based systems proposed by IBM in 2004. SOMA is widely used in multiple industries [29]. SOMA activities focus includes service identification (discovering candidate service and interaction between them), service specification (making the decision for exposing services), and service realization (capturing service realization) [29]. The main focus of SOMA is on the service model, reusing services through service components and flows [6]. SOMA is based on a commercial modeling language.


## Raw_Suitability_Of_Ros:


We initially planned to use ROS to control and monitor all experimental apparatus. However, we found that while ROS was useful in some contexts (e.g., for controlling mobile robots like mir, for which ROS path planing libraries were helpful), it introduced unhelpful complexity in others, such as for instruments that run Windows or that produce large quantities of data. Furthermore, the generality of ROS is not needed in most cases: many of our instruments are not general-purpose robots but rather devices that each perform just a few relatively simple operations. Thus, we arrived at our architecture based on the interface of Table 1.

We initially planned to use ROS to control and monitor all experimental apparatus. However, we found that while ROS was useful in some contexts (e.g., for controlling mobile robots like mir, for which ROS path planing libraries were helpful), it introduced unhelpful complexity in others, such as for instruments that run Windows or that produce large quantities of data. Furthermore, the generality of ROS is not needed in most cases: many of our instruments are not general-purpose robots but rather devices that each perform just a few relatively simple operations. Thus, we arrived at our architecture based on the interface of Table 1.


## Raw_Conclusion


The science factory architecture that we present here is a work in progress. Its modularity makes it easy to extend with new instruments, AI and other computational methods, and new workflows and applications, and its simplicity enables rapid deployment in new settings. We welcome collaboration on any aspect of its implementation and application. github, are: RV, TG, KH for the main module; RV, DO, and TG (camera); DO and RV (pf400, a4s_sealer, brooks_peeler, ur); DO, AS, and RV (platecrane, sciclops); KH, AS, and DO, RV (ot2); AS and DO (biometra); DO and AV (chemspeed, tecan); RB (rpl_omniverse, the virtual reality simulation of the modular workcell). DO designed and implemented the ROS RViz real time visualization. IF led the writing effort with RV, TG, KH, DO, CS, AS, RB, BB, TB, KC, MH, AR, and AV contributing to the writing, editing, and reviewing.

The science factory architecture that we present here is a work in progress. Its modularity makes it easy to extend with new instruments, AI and other computational methods, and new workflows and applications, and its simplicity enables rapid deployment in new settings. We welcome collaboration on any aspect of its implementation and application. github, are: RV, TG, KH for the main module; RV, DO, and TG (camera); DO and RV (pf400, a4s_sealer, brooks_peeler, ur); DO, AS, and RV (platecrane, sciclops); KH, AS, and DO, RV (ot2); AS and DO (biometra); DO and AV (chemspeed, tecan); RB (rpl_omniverse, the virtual reality simulation of the modular workcell). DO designed and implemented the ROS RViz real time visualization. IF led the writing effort with RV, TG, KH, DO, CS, AS, RB, BB, TB, KC, MH, AR, and AV contributing to the writing, editing, and reviewing.

We are working to expand the range of devices, workflows, environments, and applications supported by our science factory architecture; link multiple workcells with mobile robots; incorporate support functions such as supply and waste disposal; run increasingly ambitious science studies; and evaluate performance and resilience. We are also working to expand our simulation capabilities to enable investigation of scaling issues and ultimately the design and validation of science factories in which hundreds or thousands of workcells support many concurrent experiments.

We are working to expand the range of devices, workflows, environments, and applications supported by our science factory architecture; link multiple workcells with mobile robots; incorporate support functions such as supply and waste disposal; run increasingly ambitious science studies; and evaluate performance and resilience. We are also working to expand our simulation capabilities to enable investigation of scaling issues and ultimately the design and validation of science factories in which hundreds or thousands of workcells support many concurrent experiments.


## Raw_Meta_Model_Associated_With_Lego_Mindstorms_Robots


The first step that has been done concerns the definition of the meta model allowing any robot to be designed taking into account the aforementioned conceptual requirements: separation of concerns, abstraction and systemic points of view. We have thus define the robot as being the assembly of three components corresponding to the Decision System, the Information system and the Operating System (see Fig. 2). Each of this component has its own ports representing the physical point of connexion of the robot sub-components. In order to appreciate the meta model, we first present the physical parts of LEGO Minstorms robot, available in the conventional package for ROBAFIS contest. It includes LEGO pieces allowing the robot to be built up. There are several kinds of sensors: color, touch, gyroscopic and ultrasonic, and motors of two kinds: large and medium. The EV3 brick has a ARM9 CPU with a LINUX system and 64 MB of memory. The Decision System is modeled by a state machine (see Fig. 3). Fo

The first step that has been done concerns the definition of the meta model allowing any robot to be designed taking into account the aforementioned conceptual requirements: separation of concerns, abstraction and systemic points of view. We have thus define the robot as being the assembly of three components corresponding to the Decision System, the Information system and the Operating System (see Fig. 2). Each of this component has its own ports representing the physical point of connexion of the robot sub-components. In order to appreciate the meta model, we first present the physical parts of LEGO Minstorms robot, available in the conventional package for ROBAFIS contest. It includes LEGO pieces allowing the robot to be built up. There are several kinds of sensors: color, touch, gyroscopic and ultrasonic, and motors of two kinds: large and medium. The EV3 brick has a ARM9 CPU with a LINUX system and 64 MB of memory. The Decision System is modeled by a state machine (see Fig. 3). Fo


## Raw_Introduction


 a graphical framework called RMA (robot modeldriven architecture) for designing the configuration of a LEGO Mindstorms robot [1] and describing their behaviour from a high level of abstraction and,  a JAVA code module called RMDA2JAVA for generating the architecture of the software that will be embedded in the EV3 module of the robot. In this first experiment, the architecture is a JAVA code skeleton decomposed into packages and classes that has to be completed.

 a graphical framework called RMA (robot modeldriven architecture) for designing the configuration of a LEGO Mindstorms robot [1] and describing their behaviour from a high level of abstraction and,  a JAVA code module called RMDA2JAVA for generating the architecture of the software that will be embedded in the EV3 module of the robot. In this first experiment, the architecture is a JAVA code skeleton decomposed into packages and classes that has to be completed.


## Raw_Overall_Architecture_Of_Service-Oriented_Simulation


The simulation runtime layer hosts concrete engines, scene assets, robot embodiments, sensors, physical interaction, and control interfaces. The platform should support ecosystems such as Isaac Sim, MuJoCo, SAPIEN, Genesis, Habitat, and Gazebo/ROS under a unified runtime framework [13][14][15]21]. Different engines can be used for different task types, while upper layers maintain unified task and data protocols.

The simulation runtime layer hosts concrete engines, scene assets, robot embodiments, sensors, physical interaction, and control interfaces. The platform should support ecosystems such as Isaac Sim, MuJoCo, SAPIEN, Genesis, Habitat, and Gazebo/ROS under a unified runtime framework [13][14][15]21]. Different engines can be used for different task types, while upper layers maintain unified task and data protocols.


## Raw_Conceptual_Requirements_For_Defining_And_Implementing_The_Framework_Rmda


Another paradigm will be presented, since it has been an actual guideline to define the generic architecture of the robot and has implied a generic architecture of the controller:  The Systemic modelling approach [28].

Another paradigm will be presented, since it has been an actual guideline to define the generic architecture of the robot and has implied a generic architecture of the controller:  The Systemic modelling approach [28].


## Raw_Discovery


Our investigations of these issues have led us to develop designs and prototype implementations for several elements of a modular science factory architecture. These include a sixfunction programmatic module interface; an associated (optional) physical form factor, the cart; Increased flexibility Increased speed, reliability Manual Integrated Fig. 2 Automation systems span a continuum of flexibility, speed, and reliability, from the integrated (e.g., as shown here, a microfluidic laboratory) to the fixed (e.g., Adam 27 ), flexible (e.g., a bio workcell at Argonne), reconfigurable (e.g., a "cart" in Argonne's RPL), mobile (e.g., Liverpool's mobile robotic chemist 12 ), and manual. methods for incorporating experimental apparatus into modules and for combining modules into workcells; methods for integrating with other elements of research infrastructure, such as data repositories, computers, and AI models; notations for specifying module and workcell configurations; methods for defining

Our investigations of these issues have led us to develop designs and prototype implementations for several elements of a modular science factory architecture. These include a sixfunction programmatic module interface; an associated (optional) physical form factor, the cart; Increased flexibility Increased speed, reliability Manual Integrated Fig. 2 Automation systems span a continuum of flexibility, speed, and reliability, from the integrated (e.g., as shown here, a microfluidic laboratory) to the fixed (e.g., Adam 27 ), flexible (e.g., a bio workcell at Argonne), reconfigurable (e.g., a "cart" in Argonne's RPL), mobile (e.g., Liverpool's mobile robotic chemist 12 ), and manual. methods for incorporating experimental apparatus into modules and for combining modules into workcells; methods for integrating with other elements of research infrastructure, such as data repositories, computers, and AI models; notations for specifying module and workcell configurations; methods for defining


## Raw_Related_Works


Nevertheless, some works are interesting and offer advice for system architecting and programming. For example, [8] reveals the pros of developing a platform of control for the LEGO Mindstorms Robot. Various types of software architectures are presented in [11], such as deliberative architecture, subsumption architecture [12] or hybrid architecture. It also presents the principle of an architecture with two layers, used in robotics.

Nevertheless, some works are interesting and offer advice for system architecting and programming. For example, [8] reveals the pros of developing a platform of control for the LEGO Mindstorms Robot. Various types of software architectures are presented in [11], such as deliberative architecture, subsumption architecture [12] or hybrid architecture. It also presents the principle of an architecture with two layers, used in robotics.


## Raw_Abstract


This modelling approach includes concepts to represent services and components as primary elements in the robotics system. As stated in [26], main features for quality of architectures are high cohesion and loose coupling which leads to design for change. This is achieved by implementing the principles of abstraction, separation of concerns, and information hiding.