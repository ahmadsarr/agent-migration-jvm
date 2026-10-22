# Source unique et miroirs du skill

Modifier uniquement `skills/jvm-spark-migration/`, y compris ses références.
Les dossiers suivants sont générés et doivent rester identiques octet pour octet :

- `.agents/skills/jvm-spark-migration/` pour Codex ;
- `.claude/skills/jvm-spark-migration/` pour Claude Code.

OpenCode est installé directement depuis la source canonique. Les commandes et
agents propres aux assistants restent indépendants : ils ne sont pas générés
par ce script et ne doivent pas redéfinir les règles du skill.

## Modifier et générer

Depuis le checkout du toolkit, avec Python 3.9+ :

```bash
# Après édition du dossier skills/jvm-spark-migration/
python3 scripts/sync_skills.py
python3 scripts/sync_skills.py --check
git diff -- skills/ .agents/skills/ .claude/skills/
```

Commiter les changements de la source et des miroirs ensemble. Le script trouve
le dépôt depuis son propre emplacement et fonctionne aussi depuis un autre
répertoire courant. Il copie tous les fichiers du skill, retire les fichiers
obsolètes dans ses deux miroirs et préserve les autres skills. Une modification
manuelle d'un miroir sera écrasée à la prochaine génération : la reporter d'abord
dans la source canonique si elle doit être conservée.

Le générateur refuse les liens symboliques et un `SKILL.md` source absent ou vide.
Il inspecte les deux destinations avant toute écriture. Une interruption ou erreur
d'entrée/sortie peut néanmoins laisser une génération partielle ; corriger la
cause, relancer le générateur, puis vérifier avec `--check`.

## Contrôle CI

Le workflow **Skill mirror consistency** s'exécute sur les PR et les pushes sur
`master` touchant les chemins concernés, et peut être lancé manuellement.
Il utilise `python scripts/sync_skills.py --check`, qui :

- compare le contenu et la liste des fichiers de chaque miroir à la source ;
- affiche un diff unifié pour les fichiers texte divergents ;
- retourne 1 en cas de dérive, 2 en cas d'erreur de lecture ou de structure ;
- n'écrit aucun fichier, même lorsqu'un miroir est entièrement absent.

Le workflow exécute aussi les tests du générateur et de résolution des liens des
skills installés. Pour rendre ce check obligatoire avant fusion, sélectionner
ce job dans les règles de protection de branche GitHub ; l'ajout du workflow ne
configure pas ces règles automatiquement.

```bash
python3 -m unittest discover -s tests -p 'test_sync_skills.py' -v
```

## Références et installations existantes

Les références de compatibilité, validation, protocole et modèle de rapport qui
n'existaient que dans les copies sont maintenant dans la source canonique.
Le contrat d'orchestration est une référence locale distribuée avec le skill,
afin que ses liens fonctionnent aussi dans une installation globale.

Les modèles de checkpoint, schémas et scripts d'exécution restent dans le checkout
du toolkit ; cette génération n'en fait pas des fichiers du skill. Mettre à jour
les installations existantes avec `install.sh --action update` dans leur portée
habituelle pour recevoir les références complètes. Les contrôles de modification
locale de l'installateur restent applicables.
