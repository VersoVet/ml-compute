# Large batch size training of neural networks with adversarial training and second-order information



## Quote


The proposed approach combines content, texture and pixel loss with adversarial loss to train a conditional GAN.

We have demonstrated that a self-supervised learning technique based on second-order graphmatching, trained on a large-scale medical imaging dataset, significantly enhances performance in various downstream medical imaging tasks compared to other supervised learning methods and foundation models trained on hundreds of millions of image-text instances.

This is achieved by implementing a training strategy that prioritizes a highly varied multi-modal training set over volume of data.

Our results, for corrective training in particular, confirm our first hypothesis by showing that a deep-learning model can be trained to a high accuracy for the three different datasets of varying target objects, background, and image quality in < 2 h of annotation time.

These algorithms can undergo training using extensive datasets consisting of annotated medical images, where each image is accompanied by labels indicating the corresponding medical condition or abnormality

The research depends upon secondary data collection methods to collect the relevant information.

Regarding the issue of lack of training data, It is expected that various techniques of transfer learning will be considered such as training the DL model on large unlabeled image datasets and next transferring the knowledge to train the DL model on a small number of labeled images for the same task.

In this paper, we have estabilished a cycle wasserstein regression adversarial training framework for CT SR imaging. Aided by unpaired data, our approach learns complex structured features more effectively with a limited amount of paired data.

In this paper, we have estabilished a cycle wasserstein regression adversarial training framework for CT SR imaging. Aided by unpaired data, our approach learns complex structured features more effectively with a limited amount of paired data.

The training used the Adam optimizer (learning rate = 0.0001, weight decay = 0.00001) with the dice cross entropy loss and a batch size of 4.

Additionally, the dataset used to train and test the segmentation network is substantially larger than in previous works.

Another work in [88] propose adaptive hierarchical dual consistency to use the dataset from different centers, which learns mapping networks adversarially to align the distributions and extend consistency learning into intra-and inter-consistency in cross-domain segmentation.

Inspired by the most recent advanced neural networks, such as Dense-Net [34], Residual CNN [35], and CycleGAN [36], a cycle Wasserstein regression adversarial training framework, named S-CycleGAN, is proposed and studied for the PET brain imaging in this paper.

The framework consists of a training strategy -deep-reverse active learning (DRAL) -and an advanced network architecture -atrous DenseNet (ADN).

The first two data sets were used for developing a computer vision system that can learn the different patterns of interest from training data

Second, we employ hybrid framework that integrates the two specialized GAN models: a PSNR-driven model that prioritizes per-pixel precision accuracy, and the second GAN model, which is trained in an adversarial manner for improving visual quality

The success of our approach suggests that the rich learning capacity of large language models can effectively compensate for limited task-specific training data.

a negative correlation was found between the reported accuracy and the size of training data. For instance, Hwang et al. trained the AI algorithm with 1983 2D images, each containing 19 annotated landmarks, and observed an accuracy of 73.2% [25]. In contrast, Lee et al. used a training set of 150 images and achieved higher accuracy of 86% [22].

In this paper, we develop a pipeline which relies on 2 deep learning techniques, namely; Convolution Neural Network (CNN) [12] and RBM [6].

Our future perspectives involve the evaluation of the proposed method on larger and different datasets as well as the experimentation of additional training algorithms and other classifications schemes.

The image superresolution has shown a tremendous growth using deep learning approaches, such as convolutional neural networks (CNNs) [5], [6], [7], [8], generative adversarial networks (GANs) [9], [10], [11], recently developed transformer networks [12], [13], [14].

We show that combining information content and cost estimates is a powerful approach for cost-effectively building new training datasets from scratch.

In the first stage, we collect object localization results in the training images from both bottom-up and topdown weakly supervised object detection algorithms. In the second stage, we incorporate both metric learning and density-based clustering to filter detected object instances.


## Insight


methodology: La méthode ABSA combine une adaptation du batch size fondée sur l'information de second ordre (spectre de la Hessienne) avec un entraînement adversarial robuste formulé comme un problème min-max, afin de régulariser implicitement contre la convergence vers des minima à forte courbure caractéristiques du grand batch.

efficacy: L'entraînement à grand batch size (large batch training), bien qu'avantageux pour exploiter le calcul distribué, est associé à une dégradation documentée de la précision, une mauvaise généralisation et une robustesse réduite face aux perturbations adversariales.

methodology: L'agent adversarial combine récupération d'information ciblée et optimisation Best-of-N appliquée uniquement à l'inférence pour produire des arguments incorrects mais rhétoriquement renforcés, sans aucune mise à jour de paramètres ni apprentissage par renforcement.


## Discussion


Cette conclusion synthétise les contributions du travail sur l'entraînement à grande taille de batch avec information de second ordre et entraînement adversarial. Les auteurs ont développé un framework basé sur Ray permettant une mise à l'échelle dynamique efficace du cluster à coût de redimensionnement négligeable, tout en constatant que les méthodes existantes d'adaptive batch size restent limitées par la phase initiale d'entraînement à petite taille de batch. Pour pallier cette limite, ils proposent une méthode basée sur la Hessienne (ABSA) qui accélère l'augmentation de la taille de batch dès la phase initiale, réduisant ainsi son impact sur le gain de vitesse global. Ces approches ont été testées de manière extensive sur cinq jeux de données avec plusieurs architectures de réseaux de neurones (AlexNet, ResNet, Wide ResNet, SqueezeNext), selon deux protocoles expérimentaux (sans réglage d'hyperparamètres et avec réglage limité à la phase de warm-up), montrant dans les deux cas que la méthode ABSA permet d'augmenter la taille de batch plus rapidement et de réduire le nombre d'itérations SGD nécessaires. Les auteurs rapportent également des résultats de scalabilité et des temps d'exécution mesurés sur AWS, comparant leur méthode ABSA à des travaux antérieurs, et rendent leurs outils de distribution open source pour garantir la reproductibilité.


## Synthese


Les auteurs identifient l'entraînement à grand batch size (large batch training) comme un levier essentiel pour exploiter les clusters distribués, mais soulignent ses limites reconnues : dégradation de la précision, mauvaise généralisation, gaspillage de calcul et fragilité accrue face aux perturbations adversariales. Les solutions existantes d'adaptation dynamique du batch size (adaptive batch size) souffrent de deux limites majeures : l'absence de framework permettant de redimensionner les processus en cours d'entraînement, et un goulot d'étranglement lié à la loi d'Amdahl puisque la phase initiale à petit batch ne peut être parallélisée à grande échelle. Pour y répondre, les auteurs proposent deux méthodes : ABS (Adaptive Batch Size), qui ajuste automatiquement batch size et taux d'apprentissage à partir du spectre de la Hessienne (information de second ordre reflétant la courbure du paysage de perte), et ABSA (Adaptive Batch Size Adversarial), qui combine ABS à une régularisation implicite par entraînement robuste (formulation min-max) afin d'éviter la convergence vers des minima à forte courbure. La section Méthodes présente le protocole de comparaison entre SGD à batch fixe (petit et grand), ABS, ABSA et ABSA ajusté (Tuned, où seule la phase de warm-up est réglée), en décomposant le temps total d'entraînement en temps de calcul SGD, temps de communication, coût de redimensionnement du cluster et surcoût lié au calcul de la Hessienne. Cette section introductive présente le protocole expérimental utilisé pour évaluer les méthodes ABS (Adaptive Batch Size) et ABSA (Adaptive Batch Size Adversarial) sur des jeux de données de taille variable, allant de l'ordre de 10^5 à 10^7 exemples d'entraînement, et sur plusieurs architectures de réseaux de neurones. Les auteurs comparent leurs approches à une baseline SGD ainsi qu'à deux méthodes de référence pour l'entraînement à grand batch size, désignées FB [17] et GG [41]. Pour permettre une comparaison équitable malgré des tailles de batch variables entre les méthodes, les résultats rapportent à la fois la taille de batch maximale atteinte, le nombre de mises à jour de poids (un nombre plus faible étant préférable) et le temps d'exécution réel (wall-clock time) mesuré via un framework distribué basé sur Ray. Les auteurs précisent qu'ils n'ajustent aucun hyperparamètre spécifique à ABS/ABSA, utilisant exactement les mêmes paramètres que le modèle de référence, afin de garantir une comparaison rigoureuse et non biaisée. La section annonce ensuite la structure des résultats détaillés dans les sous-sections suivantes : comparaison de base (IV-A), évaluation sur des jeux de données plus complexes tels que TinyImageNet et ImageNet (IV-B), amélioration via un léger ajustement de la phase de warm-up (IV-C), et mesures de temps d'entraînement réel sur AWS (IV-D). Cette conclusion synthétise les contributions du travail sur l'entraînement à grande taille de batch avec information de second ordre et entraînement adversarial. Les auteurs ont développé un framework basé sur Ray permettant une mise à l'échelle dynamique efficace du cluster à coût de redimensionnement négligeable, tout en constatant que les méthodes existantes d'adaptive batch size restent limitées par la phase initiale d'entraînement à petite taille de batch. Pour pallier cette limite, ils proposent une méthode basée sur la Hessienne (ABSA) qui accélère l'augmentation de la taille de batch dès la phase initiale, réduisant ainsi son impact sur le gain de vitesse global. Ces approches ont été testées de manière extensive sur cinq jeux de données avec plusieurs architectures de réseaux de neurones (AlexNet, ResNet, Wide ResNet, SqueezeNext), selon deux protocoles expérimentaux (sans réglage d'hyperparamètres et avec réglage limité à la phase de warm-up), montrant dans les deux cas que la méthode ABSA permet d'augmenter la taille de batch plus rapidement et de réduire le nombre d'itérations SGD nécessaires. Les auteurs rapportent également des résultats de scalabilité et des temps d'exécution mesurés sur AWS, comparant leur méthode ABSA à des travaux antérieurs, et rendent leurs outils de distribution open source pour garantir la reproductibilité.

Les auteurs identifient l'entraînement à grand batch size (large batch training) comme un levier essentiel pour exploiter les clusters distribués, mais soulignent ses limites reconnues : dégradation de la précision, mauvaise généralisation, gaspillage de calcul et fragilité accrue face aux perturbations adversariales. Les solutions existantes d'adaptation dynamique du batch size (adaptive batch size) souffrent de deux limites majeures : l'absence de framework permettant de redimensionner les processus en cours d'entraînement, et un goulot d'étranglement lié à la loi d'Amdahl puisque la phase initiale à petit batch ne peut être parallélisée à grande échelle. Pour y répondre, les auteurs proposent deux méthodes : ABS (Adaptive Batch Size), qui ajuste automatiquement batch size et taux d'apprentissage à partir du spectre de la Hessienne (information de second ordre reflétant la courbure du paysage de perte), et ABSA (Adaptive Batch Size Adversarial), qui combine ABS à une régularisation implicite par entraînement robuste (formulation min-max) afin d'éviter la convergence vers des minima à forte courbure. La section Méthodes présente le protocole de comparaison entre SGD à batch fixe (petit et grand), ABS, ABSA et ABSA ajusté (Tuned, où seule la phase de warm-up est réglée), en décomposant le temps total d'entraînement en temps de calcul SGD, temps de communication, coût de redimensionnement du cluster et surcoût lié au calcul de la Hessienne.


## Methodologie


Les auteurs identifient l'entraînement à grand batch size (large batch training) comme un levier essentiel pour exploiter les clusters distribués, mais soulignent ses limites reconnues : dégradation de la précision, mauvaise généralisation, gaspillage de calcul et fragilité accrue face aux perturbations adversariales. Les solutions existantes d'adaptation dynamique du batch size (adaptive batch size) souffrent de deux limites majeures : l'absence de framework permettant de redimensionner les processus en cours d'entraînement, et un goulot d'étranglement lié à la loi d'Amdahl puisque la phase initiale à petit batch ne peut être parallélisée à grande échelle. Pour y répondre, les auteurs proposent deux méthodes : ABS (Adaptive Batch Size), qui ajuste automatiquement batch size et taux d'apprentissage à partir du spectre de la Hessienne (information de second ordre reflétant la courbure du paysage de perte), et ABSA (Adaptive Batch Size Adversarial), qui combine ABS à une régularisation implicite par entraînement robuste (formulation min-max) afin d'éviter la convergence vers des minima à forte courbure. La section Méthodes présente le protocole de comparaison entre SGD à batch fixe (petit et grand), ABS, ABSA et ABSA ajusté (Tuned, où seule la phase de warm-up est réglée), en décomposant le temps total d'entraînement en temps de calcul SGD, temps de communication, coût de redimensionnement du cluster et surcoût lié au calcul de la Hessienne.