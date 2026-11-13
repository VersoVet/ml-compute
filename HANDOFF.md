# Handoff — ml-compute

- **When**: 2026-11-01 00:39:34 UTC
- **From**: previous
- **To**: claude
- **Reason**: credits epuises / switch manuel dashboard

## Instructions pour le nouvel agent

1. Lis ce fichier en entier (transcript ci-dessous).
2. Lis `TODO.md` et `ARCHITECTURE.md`.
3. Verifie `git status` / diffs recents.
4. Reprends le travail sans recommencer de zero.

## Transcript terminal (agent precedent)

```text

  - Ubuntu Server 24.04.4 LTS
  - Hostname : onyxtensor
  - IP DHCP : 10.0.0.73
  - Carte mère : ASRock H510 Pro BTC+
  - BIOS : P1.00 du 26 mai 2021
  - CPU : Celeron G5905, 2 cœurs à 3,5 GHz
  - RAM : 8 Go
  - Stockage : SSD SATA 256 Go, 215 Go disponibles
  - Réseau : Intel I219-V à 1 Gbit/s, pilote e1000e, connexion saine
  - Secure Boot désactivé
  - Aucun GPU NVIDIA installé
  - Aucun pilote NVIDIA installé

  ## Carte à installer en premier

  Pour la mise au point, installe uniquement :

  RTX 5060 Ti 16 Go MSI Inspire 2X dans le premier slot PCIe.

  C’est le meilleur choix de démarrage :

  - 16 Go de VRAM ;
  - compacte : 204 mm ;
  - consommation raisonnable : 180 W ;
  - un seul connecteur PCIe 8 broches ;
  - suffisante pour valider Ubuntu, CUDA, Docker, PyTorch, Ray et les jobs ML.

  MSI recommande une alimentation de 600 W pour cette carte. Spécifications MSI (https://www.msi.com/Graphics-Card/GeForce-RTX-5060-Ti-16G-INSPIRE-2X-OC/Specification)

  N’installe pas encore simultanément la 4080, la 5070 et les 3090.

  ## Cartes disponibles corrigées

  - 2× RTX 3090 24 Go
  - 7× RTX 2060 Super 8 Go
  - RTX 4080 Super 16 Go
  - RTX 5070 Ventus 12 Go
  - RTX 5060 Ti 16 Go
  - RTX 4060 8 Go retrouvée
  - RTX 4070 Super 12 Go dans OnyxCortex
  - T1000 8 Go dans OnyxPoint
  - GTX 1660 Super 6 Go dans Verso-Acqui

  ## Ordre de validation conseillé

  1. RTX 5060 Ti 16 Go seule.
  2. Installer et tester le pilote NVIDIA.
  3. Tester CUDA et PyTorch.
  4. Ajouter la RTX 4060 8 Go pour valider le multi-GPU.
  5. Ajouter ensuite la RTX 5070.
  6. Réserver la RTX 4080 Super et les 3090 jusqu’à validation de l’alimentation et du câblage.

  La 5070 consomme 250 W avec un connecteur 16 broches et MSI recommande 650 W. Spécifications MSI
  (https://www.msi.com/Graphics-Card/GeForce-RTX-5070-12G-VENTUS-3X/Specification)

  La 4080 Super consomme 320 W, utilise un connecteur 16 broches et MSI recommande 850 W pour elle seule. Spécifications MSI
  (https://es.msi.com/Graphics-Card/GeForce-RTX-4080-SUPER-16G-GAMING-X-TRIO/Specification)

  ## Mise à niveau nécessaire

  Les 8 Go de RAM constituent le principal défaut actuel. Pour ce rig :

  - minimum : 16 Go ;
  - recommandé : 32 Go ;
  - stockage recommandé à terme : SSD 1 To pour Docker, caches CUDA et modèles temporaires.

  Avant de brancher la première carte, il me faut le modèle et la puissance exacte de l’alimentation, idéalement une photo de son étiquette et de ses câbles PCIe. Sans
  cela, ne branche surtout pas plusieurs GPU.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› en fait on a une alim hydro g pro. Ca doit tenir avec mes cartes puisantes par contre. J'i un besoinh urgent d'un llm pour ma biblio.


• Pour un LLM bibliographique urgent, la question n’est pas seulement la puissance électrique : il faut vérifier la puissance exacte de l’Hydro G Pro, la RAM système et
  surtout les lignes PCIe de cette carte mère. Je vérifie le câblage officiel des slots avant de te faire installer deux 3090, car du tensor-parallel sur des slots
  limités à x1 peut devenir très lent.

• Searching the web

• Searched the web for site:download.asrock.com Manual H510 Pro BTC+ PCIe x16 x1 slots bandwidth ...

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Le point décisif est confirmé : seul PCIE1 fonctionne en x16; les cinq autres grands connecteurs ne sont câblés qu’en x1. Donc deux 3090 en tensor-parallel seraient
  possibles mais pénalisées par les communications inter-GPU. Pour ton besoin urgent, je cherche l’option mono-GPU la plus utile immédiatement sur 16 Go, puis je te donne
  un montage provisoire sûr.

◦ Searching the web

• Searched the web for site:huggingface.co/Qwen official Qwen latest 32B AWQ model ...

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Pour obtenir rapidement un bon LLM de bibliographie, installe une seule RTX 3090 24 Go dans PCIE1, le slot le plus proche du processeur.

  Pourquoi :

  - PCIE1 est le seul véritable PCIe 3.0 x16.
  - PCIE2–6 sont physiquement x16 mais électriquement x1. Manuel ASRock (https://download.asrock.com/Manual/H510%20Pro%20BTC%2B.pdf)
  - Une 3090 de 24 Go peut faire tourner un modèle 32B quantifié sans communication entre GPU.
  - Les deux 3090 en tensor-parallel fonctionneraient théoriquement, mais la seconde serait en x1 et ralentirait fortement les échanges.

  ### Configuration urgente recommandée

  - PCIE1 x16 : RTX 3090 24 Go
  - Modèle : Qwen/Qwen3-32B-AWQ
  - Contexte initial : 8 192 tokens
  - Serveur : vLLM compatible OpenAI
  - Les autres GPU restent débranchés pour le premier démarrage.

  Le modèle AWQ fait environ 19,3 Go. Il est donc serré mais exploitable sur une 3090 de 24 Go avec un contexte maîtrisé. Modèle officiel Qwen3-32B-AWQ
  (https://huggingface.co/Qwen/Qwen3-32B-AWQ)

  ### Alimentation

  Une Hydro G Pro convient pour une seule 3090 si c’est au minimum la version 850 W. Vérifie néanmoins la valeur inscrite sur son étiquette :

  - 850 W : une 3090, sans autre grosse carte ;
  - 1000 W : une 3090 très confortable, éventuellement une petite seconde carte plus tard ;
  - 1200 W : deux 3090 possibles électriquement.

  Utilise deux câbles PCIe distincts pour la 3090, sans faire alimenter ses deux prises par une seule dérivation en Y.

  ### Blocage actuel : la RAM

  OnyxTensor n’a que 8 Go de RAM. C’est insuffisant pour installer proprement vLLM, charger un 32B et faire fonctionner les outils bibliographiques.

  La carte mère n’a qu’un seul emplacement mémoire :

  - installe directement une barrette DDR4 de 32 Go ;
  - le Celeron limite la mémoire à DDR4-2666 ;
  - la carte mère accepte au maximum 32 Go.

  ### Si tu dois démarrer avant de recevoir la RAM

  Installe plutôt la RTX 4080 Super 16 Go dans PCIE1 et utilise Qwen3-14B-AWQ. Ce sera plus rapide, mais moins performant intellectuellement que le 32B sur la 3090.

  Mon choix pour la bibliographie :

  32 Go RAM + RTX 3090 24 Go en PCIE1 + Qwen3-32B-AWQ

  Une fois la carte et la RAM installées, démarre OnyxTensor. Je pourrai ensuite installer le pilote NVIDIA, CUDA, Docker et le serveur LLM à distance.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› j'ai que des 16go de ram


• Mets une barrette de 16 Go DDR4 : ce sera suffisant pour démarrer le service LLM, même si 32 Go resterait préférable.

  Configuration urgente :

  - 16 Go de RAM DDR4 dans l’unique slot DIMM
  - Une RTX 3090 24 Go dans PCIE1 x16
  - Aucune autre carte au premier démarrage
  - Qwen3-32B-AWQ avec contexte limité à 4 096 ou 8 192 tokens
  - Swap système porté ensuite à 16 Go

  Avec 16 Go, évite les téléchargements, indexations et traitements lourds simultanés pendant le chargement du modèle. Le poids principal restera dans les 24 Go de VRAM.

  Si le modèle 32B est instable ou manque de mémoire :

  Qwen3-14B-AWQ

  Il fonctionnera confortablement, puis on réessaiera le 32B avec des paramètres mémoire plus stricts.

  Avant le montage, confirme seulement la puissance inscrite sur l’Hydro G Pro : 850W, 1000W ou 1200W.


› si on met les 2 3090 meme si c'est lent ce sera meilleur en fonctinnement ?


◦ Searching the web

• Searched the web for site:docs.vllm.ai pipeline parallel tensor parallel GPUs without NVLink official ...

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Oui, deux RTX 3090 donneront accès à de meilleurs modèles, mais elles ne rendront pas automatiquement un même modèle plus performant.

  Avec deux 3090 :

  - VRAM totale : 48 Go.
  - Possibilité de charger un modèle 70/72B quantifié.
  - Qualité généralement supérieure pour la bibliographie complexe, l’extraction et la synthèse.
  - Contexte et cache KV potentiellement plus importants.
  - Génération probablement assez lente à cause du deuxième slot PCIe x1.

  La H510 Pro BTC+ fournit :

  - PCIE1 : PCIe 3.0 x16.
  - PCIE2–6 : PCIe 3.0 x1 seulement. Manuel ASRock (https://download.asrock.com/Manual/H510%20Pro%20BTC%2B.pdf)

  Il faudra utiliser du pipeline parallel, pas du tensor parallel classique :

  RTX 3090 nº1 → PCIE1 x16
  RTX 3090 nº2 → PCIE2 x1
  vLLM : tensor-parallel-size=1, pipeline-parallel-size=2

  vLLM recommande justement le pipeline parallel lorsque les GPU n’ont pas une interconnexion rapide, afin de réduire les communications. Documentation vLLM
  (https://docs.vllm.ai/en/v0.10.1/serving/parallelism_scaling.html)

  Comparaison pratique :

   Montage            Modèle possible                         Vitesse    Qualité bibliographique
  ━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━
   1×3090             Qwen3-32B-AWQ                             Bonne                 Très bonne
  ─────────────────  ─────────────────  ──────────────────────────────  ─────────────────────────
   2×3090             Qwen 70/72B Q4                            Lente                  Meilleure
  ─────────────────  ─────────────────  ──────────────────────────────  ─────────────────────────
   2×3090 avec 32B    Peu d’intérêt      Potentiellement moins rapide                  Identique

  Pour ton besoin, je monterais bien les deux 3090, car la priorité est la qualité du LLM et non le débit maximal. On pourra comparer :

  1. Qwen3-32B-AWQ sur une seule 3090.
  2. Un 70/72B Q4 sur les deux 3090 en pipeline.
  3. Conserver celui offrant le meilleur compromis qualité/vitesse.

  Conditions impératives :

  - Hydro G Pro 1000 W minimum, 1200 W préférable.
  - Quatre câbles PCIe séparés si chaque 3090 utilise deux prises.
  - Aucun câble en Y partagé entre les deux cartes.
  - Barrette RAM 16 Go installée et swap de 16 à 32 Go.
  - Cartes suffisamment espacées et ventilées.
  - Limite de puissance initiale à environ 280 W par 3090, soit 560 W au total.

  Avec une Hydro G Pro 850 W, je resterais sur une seule 3090. Avec 1000 ou 1200 W, les deux sont envisageables.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› eteint la machine onyxtensor


• J’éteins maintenant onyxtensor proprement via le système, puis je vérifie qu’il ne répond plus sur le réseau.

• Ran 2 commands · ctrl + t to view transcript

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• onyxtensor est éteint proprement et ne répond plus sur le réseau. Tu peux maintenant couper l’alimentation et installer les cartes.

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› je viens de relancer onyxtensor J'ai installé 4 cartes


• Je vérifie immédiatement les quatre GPU détectés, leur emplacement PCIe, la largeur de lien négociée, ainsi que l’état du pilote NVIDIA. Je ne modifie encore rien sur
  la machine.

• La machine ne répond pas encore à SSH après la première fenêtre de 30 secondes. Je vérifie si elle a obtenu une autre adresse DHCP ou si elle est bloquée pendant le
  démarrage PCIe avec les quatre cartes.

• Ran for attempt in 1 2 3 4 5; do if ssh -o BatchMode=yes -o ConnectTimeout=5 onyx@10.0.0.73 'true' 2>/dev/null; then break; fi; sleep 2; done; ssh -o BatchMode=yes -o
  │ ConnectTimeout=8 onyx@10.0.0.73 '
  │ printf "=== HOST ===\n"; hostname; uptime
  │ … +8 lines
  └ ssh: connect to host 10.0.0.73 port 22: No route to host

• Ran 4 commands · ctrl + t to view transcript

• Context compacted

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Le bail DHCP montre qu’OnyxTensor est maintenant sur 10.0.0.100 (et non .73). Je m’y connecte avec la clé déjà installée et je vérifie les quatre GPU, leurs liens PCIe,
  la RAM et le pilote NVIDIA.

• Ran ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new onyx@10.0.0.100 'set -u; echo HOST; hostnamectl --static; uptime; echo MEMORY; free -h;
  │ echo NVIDIA_SMI; if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi
  │ --query-gpu=index,name,uuid,memory.total,pci.bus_id,driver_version,pstate,power.draw,power.limit --format=csv,noheader; else echo nvidia-smi_absent; fi; echo
  │ … +4 lines
  └ ssh: connect to host 10.0.0.100 port 22: No route to host

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• La machine n’est pas encore joignable (No route to host) malgré son bail DHCP. Je vérifie si elle apparaît réellement sur le réseau — elle peut encore être en phase de
  démarrage, ou le câble/interface réseau peut avoir changé après l’ajout des cartes.

• Ran ip route get 10.0.0.100; ip neigh show 10.0.0.100; ping -c 3 -W 2 10.0.0.100 || true; ip neigh show 10.0.0.100; for p in 22 80 443; do timeout 2 bash -c "</dev/
  │ tcp/10.0.0.100/$p" >/dev/null 2>&1 && echo "port $p open" || true; done
  └ PING 10.0.0.100 (10.0.0.100) 56(84) bytes of data.
    From 10.0.0.13 icmp_seq=1 Destination Host Unreachable
    … +5 lines (ctrl + t to view transcript)
    pipe 3
    10.0.0.100 dev eno1 FAILED

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Le bail .100 est actuellement périmé ou la carte réseau n’a pas établi de lien : aucune réponse ARP, donc le problème se situe avant SSH. Je recherche maintenant
  OnyxTensor sur tout le sous-réseau au cas où DHCP lui aurait attribué une autre adresse.

• Ran if command -v arp-scan >/dev/null 2>&1; then sudo -n arp-scan --interface=eno1 --localnet 2>/dev/null | grep -Ei 'a8:a1:59:97:e1:bf|ASRock|10\.0\.0\.'; elif command
  │ -v nmap >/dev/null 2>&1; then nmap -sn -PR 10.0.0.0/24 >/dev/null; ip neigh show dev eno1; else for i in $(seq 1 254); do ping -c 1 -W 1 10.0.0.$i >/dev/null 2>&1 &
  │ done; wait; ip neigh show dev eno1; fi
  └ 10.0.0.172 INCOMPLETE
    10.0.0.47 INCOMPLETE
    … +257 lines (ctrl + t to view transcript)
    fe80::1c12:a0a7:1289:1389 lladdr dc:4a:3e:43:fa:7b STALE
    fe80::fce3:754:5452:a3a4 lladdr 18:c0:4d:6a:11:2b STALE

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• Trouvé : OnyxTensor répond à 10.0.0.23 avec la même adresse MAC. Le DHCP a donc changé son adresse depuis la réinstallation/redémarrage; je lance l’audit sur .23.

• Ran ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new onyx@10.0.0.23 'set -u; echo HOST; hostnamectl --static; uptime; echo MEMORY; free -h;
  │ echo NVIDIA_SMI; if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi
  │ --query-gpu=index,name,uuid,memory.total,pci.bus_id,driver_version,pstate,power.draw,power.limit --format=csv,noheader; else echo nvidia-smi_absent; fi; echo
  │ … +4 lines
  └ ssh: connect to host 10.0.0.23 port 22: No route to host

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• La carte réseau a annoncé brièvement .23, puis a disparu avant l’ouverture SSH : le lien réseau est instable, ce n’est pas un problème de clé. Je fais une dernière
  vérification après stabilisation du démarrage; si elle retombe, il faudra contrôler localement l’alimentation et l’état du lien Ethernet.

• Ran for attempt in 1 2 3; do ping -c 1 -W 2 10.0.0.23 >/dev/null 2>&1 && break; sleep 5; done; ip neigh show 10.0.0.23; ssh -o BatchMode=yes -o ConnectTimeout=8 -o
  │ StrictHostKeyChecking=accept-new onyx@10.0.0.23 'hostname; free -h; command -v nvidia-smi >/dev/null && nvidia-smi -L || echo nvidia-smi_absent; lspci -Dnn | grep
  │ -Ei "VGA|3D controller|Display controller"'
  └ 10.0.0.23 dev eno1 FAILED
    ssh: connect to host 10.0.0.23 port 22: No route to host

──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• OnyxTensor n’est pas encore accessible pour l’audit.

  - Son adresse MAC a été vue brièvement sur 10.0.0.23, puis le lien réseau a disparu.
  - 10.0.0.100 ne répond plus non plus.
  - Ce n’est pas un problème d’authentification SSH : aucune réponse ARP n’arrive de la machine.
  - Vérifie sur la console locale qu’Ubuntu a terminé de démarrer, puis lance ip -br address.
  - Vérifie aussi les voyants Ethernet. Avec quatre GPU, un défaut d’alimentation, un riser ou une carte mal enfichée peut empêcher/stabiliser difficilement le démarrage.

  Dès que tu me donnes l’adresse affichée localement — ou que le réseau réapparaît — je contrôle immédiatement les quatre cartes, la VRAM, les liens PCIe et le pilote
  NVIDIA.

─ Worked for 2m 04s ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────


› Ask Codex to do anything

  gpt-5.6-sol default · ~/projects/skills/ml-compute
```
