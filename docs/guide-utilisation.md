# Guide d'utilisation du toolkit JVM

Ce guide couvre la migration d'une application et le développement d'une évolution
avec Spec Kit. Les commandes de terminal sont en Bash. Les commandes commençant
par `/` sont à saisir dans la conversation OpenCode.

## Sommaire

- [Choisir son parcours](#parcours)
- [Préparer son environnement](#environnement)
- [Migrer une application avec OpenCode](#migration)
- [Choisir les tests de régression](#regressions)
- [Automatiser avec Spec Kit](#speckit)
- [Rapports et checkpoints](#rapports)
- [Claude Code et Codex](#assistants)
- [Maintenance](#maintenance)
- [Dépannage](#depannage)

<a id="parcours"></a>
## Choisir son parcours

| Besoin | Outil | Résultat attendu |
|---|---|---|
| Migrer une application Java, Scala ou Spark depuis Java 11 | Skill `jvm-spark-migration` et commandes OpenCode | Audit, compatibilité vérifiée, lots réversibles et preuves de validation |
| Développer une évolution du toolkit ou d'une application | `scripts/speckit_opencode.py` | Constitution, spécification, plan, tâches, analyse et implémentation |
| Clôturer un objectif documenté | `scripts/goal_executor.py` | Vérification du checkpoint et passage à `COMPLETED` si ses conditions sont satisfaites |

Spec Kit est optionnel pour une migration interactive. `/plan` prépare des lots
de migration ; `/speckit.plan` prépare le plan technique d'une fonctionnalité.
Le validateur de checkpoints ne lance ni tests ni modèle : il contrôle les données
et fichiers enregistrés. Aucun de ces outils ne prouve à lui seul une migration réussie.

<a id="environnement"></a>
## Préparer son environnement

- Installer [OpenCode](https://opencode.ai/docs/) et configurer son fournisseur de modèle.
- Disposer de Git et d'un checkout de l'application avec un état de travail connu.
- Pour l'installateur : Bash 4+, `sha256sum`, GNU `find`, `sort` et coreutils.
  Linux ou WSL convient ; sur macOS, installer les outils GNU compatibles.
- Pour les scripts Python : Python 3.9+. Spec Kit s'installe séparément, avec Python 3.12 dans l'exemple ci-dessous.
- Pour exécuter la migration : JDK source, outil de build du projet et services
  nécessaires aux tests. Déterminer le JDK cible après l'étude de compatibilité.

Dans le terminal :

```bash
git clone https://github.com/ahmadsarr/agent-migration-jvm.git
cd agent-migration-jvm
toolkit_dir="$PWD"
project_dir="/chemin/absolu/vers/application"
```

Remplacer `project_dir` par un répertoire existant, distinct du toolkit pour une
migration applicative. Conserver ces variables dans le terminal ou les redéfinir
à chaque session. Le toolkit n'installe ni OpenCode, ni les JDK, ni les dépendances.

<a id="migration"></a>
## Migrer une application avec OpenCode

Pour Spring ou Spring Boot, suivre aussi le [parcours Spring](spring-jvm-migration.md) :
compatibilité JDK/framework, Jakarta, Security, JPA et tests HTTP/JSON ciblés.

### 1. Installer les instructions

Choisir une installation projet (ci-dessous) ou une installation utilisateur
avec `bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global`.
Pour le projet courant, utiliser `--scope project` sans `--target` depuis sa racine.
Voir les [portées et emplacements](harness-installation.md). Les rapports restent
propres à chaque projet, même avec une installation globale.

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir"
cd "$project_dir"
opencode
```

L'installation crée le skill sous `.opencode/skills/jvm-spark-migration/`, les
commandes dans `.opencode/commands/` et le manifeste `.jvm-migration/opencode.manifest`.
Elle ne crée pas `migration/state.json`. Voir [les destinations](harness-installation.md).

### 2. Auditer l'existant

Dans OpenCode, préciser le périmètre, par exemple :

```text
Charge le skill jvm-spark-migration pour cette application.
Audite le JDK, les dépendances, le build, la CI et les runtimes de déploiement.
Inclus Spark et Scala si le projet les utilise.
Pour cette première étape, reste en lecture seule et présente les résultats ici.
Indique les versions constatées, les preuves et les informations manquantes.
```

Puis saisir `/audit`. Les versions doivent être étayées par les fichiers ou
commandes examinés. Un environnement absent reste une inconnue. Pour conserver
ensuite les résultats, convenir d'une destination, par exemple `migration/assessment.md`.

### 3. Choisir la cible et préparer les lots

Saisir `/compatibility`, puis `/plan`, en examinant chaque résultat. La cible
dépend des versions exactes : JDK, Spark, Scala, plugins et connecteurs. Une
version Java plus récente n'est pas automatiquement compatible.

Chaque lot doit préciser les fichiers concernés, risques, tests existants,
tests manquants, critères d'acceptation et marche arrière. Séparer les montées
de version des refontes fonctionnelles facilite le diagnostic d'une régression.

### 4. Capturer la référence avant modification

Communiquer le lot et le périmètre autorisé dans la conversation :

```text
Pour le lot 1 décrit dans le plan, réutilise les tests existants adéquats.
Tu peux ajouter uniquement les tests manquants identifiés dans ce lot,
exécuter les tests locaux convenus et écrire les rapports sous migration/.
Capture les résultats avec le JDK et les dépendances sources avant leur mise à jour.
Présente les changements de migration prévus avant de les appliquer.
```

Saisir `/regressions`. Conserver versions, commandes exactes, données et résultats
de référence. Un test ajouté après migration reste utile, mais le rejouer aussi
sur la version source quand c'est possible établit la comparaison avant/après.

### 5. Appliquer et comparer

Après examen des changements prévus, autoriser le lot et saisir `/apply`.
Travailler sur une branche dédiée. Exécuter ensuite `/regressions` sur la cible,
puis `/validate`, avec des données et assertions équivalentes à la référence.

| Commande | Utilisation |
|---|---|
| `/audit` | Recenser l'existant sans modifier les sources |
| `/compatibility` | Justifier la cible avec des sources officielles correspondant aux versions |
| `/plan` | Définir les lots, risques et critères de validation |
| `/regressions` | Combler les lacunes de couverture et comparer les tests source/cible |
| `/apply` | Réaliser le lot autorisé |
| `/validate` | Établir un Go/No-Go fondé sur les résultats |
| `/status` | Résumer progrès, blocages et prochaines actions |
| `/rollback` | Préparer le retour arrière ; son exécution dépend du périmètre explicitement autorisé |

Ces modèles ne déclarent pas de paramètre `$ARGUMENTS` : communiquer le contexte
dans la conversation. Le titre `# /migration:audit` d'un modèle ne renomme pas
la commande `/audit` dans OpenCode.

<a id="regressions"></a>
## Choisir les tests de régression

Partir des usages réels de la dépendance critique, puis examiner les assertions
existantes. Ajouter uniquement les tests manquants pour un comportement attendu.
Voir le [workflow détaillé](../skills/jvm-spark-migration/references/targeted-regressions.md)
et le [modèle de rapport](../skills/jvm-spark-migration/references/regression-report-template.md).

| Exemple de risque | Contrat à préciser |
|---|---|
| Ordre d'une liste issue d'une requête | L'ordre est-il garanti ? Quel tri et quel départage des égalités ? |
| Sérialisation après changement de bibliothèque | Quels champs, valeurs nulles et formats doivent rester compatibles ? |
| Dates après changement de JDK | Quel instant et quel fuseau sont attendus, notamment au changement d'heure ? |
| Reprise d'un traitement Spark | Quels résultats et garanties sont attendus avec le checkpoint concerné ? |

Sans ordre contractuel, comparer le contenu selon le contrat : ensemble ou
multiensemble selon la présence possible de doublons. Ne pas figer un ordre
observé par hasard. Faire préciser un contrat ambigu avant d'écrire l'assertion.

Pour chaque risque, consigner le test, les versions source/cible, les commandes,
les nombres de tests exécutés ou ignorés, les codes de sortie et les preuves.
Un build réussi avec zéro test sélectionné ne valide pas le comportement.
Un service manquant donne `NOT_RUN`, pas `PASS`. Un risque critique non vérifié
empêche une décision Go.

<a id="speckit"></a>
## Automatiser avec Spec Kit et OpenCode

Le [guide technique Spec Kit](speckit-opencode.md) détaille les paramètres et
limites. Ce parcours fait évoluer **le toolkit lui-même**. Les exemples proposent
une évolution du suivi des preuves de régression : adapter les fichiers d'entrée
à votre besoin avant de lancer la préparation.

### 1. Installer et initialiser

Installer [uv](https://docs.astral.sh/uv/) si nécessaire, puis :

```bash
uv tool install --python 3.12 'specify-cli==1.2.2'
specify version --json
opencode --version

project_dir="$toolkit_dir"
runner="$toolkit_dir/scripts/speckit_opencode.py"
python3 "$runner" --project "$project_dir" --dry-run init
python3 "$runner" --project "$project_dir" init
python3 "$runner" --project "$project_dir" run constitution \
  --input-file "$toolkit_dir/examples/speckit/constitution.md"
```

`init` exige Spec Kit 1.2.2 sur `PATH` et refuse une installation déjà présente.
Il génère `.specify/` et les commandes `speckit.*`. Relire la constitution avant
la suite. Pour une application externe, changer `project_dir` et fournir des
entrées décrivant sa migration ; installer aussi le skill si vous voulez l'utiliser.

### 2. Préparer une fonctionnalité

```bash
python3 "$runner" --project "$project_dir" prepare \
  --feature specs/007-ma-fonctionnalite \
  --spec-file "$toolkit_dir/examples/speckit/specification.md" \
  --plan-file "$toolkit_dir/examples/speckit/plan.md"
```

La séquence `specify → plan → tasks → analyze` s'arrête avant l'implémentation.
Relire `spec.md`, `plan.md`, `tasks.md` et la sortie d'analyse dans les logs.
`prepare` exige une nouvelle fonctionnalité ; utiliser `run` pour reprendre.

### 3. Clarifier et reprendre

Une spécification contenant `[NEEDS CLARIFICATION ...]` bloque les étapes suivantes.
Pour répondre dans OpenCode avec la bonne fonctionnalité sélectionnée :

```bash
cd "$project_dir"
SPECIFY_FEATURE_DIRECTORY=specs/007-ma-fonctionnalite opencode
```

Saisir `/speckit.clarify`, résoudre les questions, puis reprendre dans le terminal :

```bash
python3 "$runner" --project "$project_dir" run plan \
  --feature specs/007-ma-fonctionnalite \
  --input-file "$toolkit_dir/examples/speckit/plan.md"
python3 "$runner" --project "$project_dir" run tasks --feature specs/007-ma-fonctionnalite
python3 "$runner" --project "$project_dir" run analyze --feature specs/007-ma-fonctionnalite
```

### 4. Implémenter et examiner le résultat

Après revue du plan, des tâches et de l'analyse :

```bash
python3 "$runner" --project "$project_dir" run implement --feature specs/007-ma-fonctionnalite
python3 "$runner" --project "$project_dir" run converge --feature specs/007-ma-fonctionnalite
```

`converge` lance la passe de convergence Spec Kit. Examiner le diff, les vrais
résultats des tests et les points restants avant de proposer une PR. Les étapes
peuvent modifier le projet selon les permissions OpenCode configurées. Le script
ne fusionne pas et ne déploie pas.

Les options globales précèdent la sous-commande :

```bash
python3 "$runner" --project "$project_dir" --timeout 1800 --dry-run \
  run analyze --feature specs/007-ma-fonctionnalite
```

`--model provider/model` sélectionne un modèle configuré ; sans cette option,
OpenCode utilise sa configuration. `--dry-run` valide les prérequis et affiche
les arguments, sans simuler les réponses du modèle ni les artefacts ultérieurs.

<a id="rapports"></a>
## Rapports et checkpoints

| Emplacement dans le projet cible | Contenu |
|---|---|
| `.jvm-migration/<harness>.manifest` | Fichiers installés et empreintes pour la maintenance |
| `migration/assessment.md`, `compatibility.md`, `plan.md` | Documents de migration à produire dans la destination convenue |
| `migration/reports/`, `migration/evidence/` | Rapports par lot et preuves des vérifications exécutées |
| `migration/state.json` | Checkpoint optionnel des objectifs et critères |
| `specs/<fonctionnalite>/` | Spécification, plan et tâches Spec Kit |
| `.jvm-migration/speckit-runs/<date>-<id>/` | Rapport JSON et sorties de chaque invocation du wrapper |

Les logs Spec Kit contiennent les entrées et sorties du modèle ; les examiner
avant partage. `RETURNED_REVIEW_REQUIRED` signifie que les commandes sont revenues
et que les fichiers attendus existent. Cela ne prouve pas que les tests passent.
`FAILED` signale une erreur d'orchestration ou de commande.

### Initialiser le checkpoint optionnel

Après avoir convenu de son utilisation et de la destination des rapports :

```bash
mkdir -p "$project_dir/migration"
if [ ! -e "$project_dir/migration/state.json" ]; then
  cp "$toolkit_dir/migration/templates/state.json" "$project_dir/migration/state.json"
fi
git -C "$project_dir" rev-parse HEAD
git -C "$project_dir" branch --show-current
```

Éditer le JSON pour renseigner `repository.head` et `repository.branch` avec
les valeurs constatées. Adapter les objectifs, critères et autorisations au
travail convenu. Le modèle contient des valeurs provisoires et des `NOT_RUN` ;
sa copie ne signifie pas que des vérifications ont eu lieu.

```bash
python3 "$toolkit_dir/scripts/goal_executor.py" --project "$project_dir" status
```

Avant clôture, persister le rapport, renseigner les preuves sous forme de tableaux
de chemins relatifs, enregistrer les vrais résultats des critères et placer
l'objectif en `READY` ou `VALIDATING`. Ses dépendances doivent être terminées,
chaque critère doit être `PASS` avec au moins un critère, et
`authorization.reportWrite` doit refléter l'autorisation reçue. Alors seulement :

```bash
python3 "$toolkit_dir/scripts/goal_executor.py" --project "$project_dir" complete --goal GOAL-001
```

Le validateur contrôle les conditions enregistrées et l'existence des fichiers.
Il n'exécute pas les tests et ne juge pas la qualité des preuves. Après un commit
ou changement de branche, examiner les changements puis réconcilier le checkpoint ;
ne pas remplacer le SHA à l'aveugle pour contourner un blocage. Le wrapper Spec Kit
ne met pas à jour ce checkpoint. Voir [le contrat](../migration/README.md) et
[le validateur](goal-executor.md).

<a id="assistants"></a>
## Claude Code et Codex

Remplacer `--harness opencode` par `--harness claude` ou `--harness codex` dans
l'installation. Claude Code reçoit le skill, les commandes et les agents ; Codex
reçoit le skill sous `.agents/skills/jvm-spark-migration/`.

Lancer l'assistant depuis l'application et lui demander de charger le skill puis
de réaliser l'audit. Consulter les commandes disponibles dans votre version de
Claude Code. Pour Codex, utiliser des demandes en langage naturel : l'installateur
n'y installe pas de slash commands. Le wrapper Spec Kit reste spécifique à OpenCode.

<a id="maintenance"></a>
## Maintenance

Si vous venez du parcours Spec Kit sur le toolkit, redéfinir `project_dir` avec
le chemin de l'application à maintenir. Mettre le checkout du toolkit à la version
souhaitée, puis :

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action update --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action update
```

Pour retirer les fichiers gérés par le manifeste :

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action uninstall --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action uninstall
```

Des fichiers gérés modifiés ou manquants provoquent un refus. Préserver et
réconcilier vos modifications avant de réessayer. Il n'existe pas d'option `--force`.
La maintenance du toolkit ne met pas à jour Spec Kit et ne supprime pas les rapports
ni les spécifications.

<a id="depannage"></a>
## Dépannage

| Symptôme | Action |
|---|---|
| Commandes OpenCode absentes | Relancer depuis la racine cible et vérifier `.opencode/commands/` |
| Skill non chargé | Vérifier son `SKILL.md`, les permissions de skills et demander explicitement son chargement |
| Référence du skill introuvable | Les anciennes références de compatibilité, validation et protocole sont sous `.agents/skills/jvm-spark-migration/references/` dans le checkout du toolkit ; fournir ce chemin à l'assistant |
| `specify` ou `opencode` introuvable | Vérifier l'installation et le `PATH` du terminal |
| Version Spec Kit refusée | Utiliser `specify-cli==1.2.2` pour le wrapper actuel |
| `init` refuse `.specify` existant | Examiner et utiliser l'installation existante ; ne pas réinitialiser par-dessus |
| `prepare` refuse une fonctionnalité existante | Reprendre avec `run <étape>` et le même `--feature` |
| Constitution encore au format modèle | Exécuter `run constitution --input-file ...`, puis examiner son contenu |
| Erreur fournisseur, sortie vide ou délai dépassé | Lire `report.json`, `stdout.jsonl` et `stderr.log` dans le run affiché ; résoudre l'erreur puis reprendre l'étape |
| Interaction requise pendant un run | Résoudre la question dans OpenCode interactif avec le même `SPECIFY_FEATURE_DIRECTORY` |
| Divergence Git du checkpoint | Examiner commits et branche puis réconcilier objectifs et preuves |
| Service ou JDK requis indisponible | Conserver `NOT_RUN` et exécuter la vérification lorsque l'environnement sera disponible |

Pour vérifier localement le toolkit depuis son checkout :

```bash
cd "$toolkit_dir"
python3 -m unittest discover -s tests -p 'test_*.py' -v
bash -n scripts/install.sh tests/install-test.sh
bash tests/install-test.sh
```

Ces tests vérifient les scripts et l'installation. Les tests du wrapper utilisent
un exécutable OpenCode simulé : ils ne valident ni un fournisseur réel ni votre
migration. Les tests applicatifs restent ceux du projet, exécutés sur les
environnements source et cible.
