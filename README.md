# Agent Migration JVM

Toolkit for planning and validating migrations from Java 11 to a compatible target JDK for Java, Spring/Spring Boot, Scala and Apache Spark applications.

## Guide d'utilisation

**Commencer ici : [guide complet en français](docs/guide-utilisation.md).**
La documentation est versionnée avec le code, comme un wiki dans le dépôt.

| Votre objectif | Documentation |
|---|---|
| Migrer une application JVM avec OpenCode | [Parcours migration](docs/guide-utilisation.md#migration) |
| Migrer une application Spring / Spring Boot | [Parcours Spring](docs/spring-jvm-migration.md) |
| Développer une évolution avec Spec Kit | [Parcours Spec Kit](docs/guide-utilisation.md#speckit) |
| Installer pour OpenCode, Claude Code ou Codex | [Installation et maintenance](docs/harness-installation.md) |
| Protéger les comportements après une mise à jour critique | [Tests de régression](docs/guide-utilisation.md#regressions) |
| Comprendre les fichiers et statuts | [Rapports et checkpoints](docs/guide-utilisation.md#rapports) |
| Reprendre après une erreur | [Dépannage](docs/guide-utilisation.md#depannage) |

Le toolkit fournit des instructions, des modèles et des scripts d'orchestration.
L'assistant travaille dans votre application avec ses outils de build et de test.
Spec Kit structure une fonctionnalité ; le validateur de checkpoints contrôle les
preuves enregistrées. Aucun de ces éléments ne suffit à déclarer une migration réussie.

## Version du toolkit

La version est centralisée dans [`VERSION`](VERSION). Consulter le
[guide des versions](docs/versioning.md) et le [changelog](CHANGELOG.md).

```bash
bash scripts/install.sh --version
bash scripts/install.sh --harness opencode --target /chemin/application --action status
bash scripts/install.sh --harness opencode --scope global --action status
```

Les installations anciennes affichent une version inconnue jusqu'à leur mise à
jour. La première version `0.1.0` est préparée ; son tag et sa release ne sont pas
encore publiés.

## Workflow
1. Audit existing runtime, dependencies, Spark, Scala and build tooling.
2. Determine a supported target JDK from verified compatibility evidence.
3. Plan small reversible changes and identify behavioral risks in critical dependencies.
4. Reuse existing tests, add only approved missing regression tests, and capture the Java 11 baseline.
5. Apply only approved migration changes.
6. Compare baseline/target behavior and validate Spark streaming recovery, performance and deployment where relevant.

Canonical skill: `skills/jvm-spark-migration/SKILL.md` (mirrored for Codex and Claude Code). All copies share the goal execution and mandatory reporting contract. See `commands/` for generic templates and `.claude/commands/` for Claude-specific commands.

Pour contribuer au skill, modifier uniquement `skills/jvm-spark-migration/`, puis :

```bash
python3 scripts/sync_skills.py
python3 scripts/sync_skills.py --check
```

Le check CI compare les miroirs Codex/Claude avec la source et échoue en cas de
dérive. Voir [la génération des miroirs](docs/skill-mirrors.md).

Command files are prompt templates; slash-command registration depends on the coding assistant.

## Use with OpenCode

To automate the Spec Kit workflow through OpenCode, use
[`scripts/speckit_opencode.py`](scripts/speckit_opencode.py). It initializes
Spec Kit, prepares specifications, plans and tasks, and runs implementation on
explicit invocation. See the [step-by-step guide](docs/speckit-opencode.md)
for installation, examples, retries and execution reports.

### Prerequisites

- Install [OpenCode](https://opencode.ai/docs/) and configure a model provider.
- Use Bash 4+ with `sha256sum`, GNU `find`, `sort` and coreutils. Linux or WSL is
  the simplest setup for the current installer; macOS needs compatible GNU tools
  and a recent Bash on `PATH`.
- Have an existing application checkout to migrate. Its Java 11 toolchain and
  Maven/Gradle/SBT setup are needed for baseline execution; the supported target
  JDK is selected after the compatibility assessment.

The toolkit installer installs project-local or user-global instructions and commands. OpenCode,
JDKs, build tools and application dependencies are installed separately.

### Installation globale ou projet courant

Depuis le checkout du toolkit, définir `toolkit_dir="$PWD"`. Puis choisir :

```bash
# Dans le terminal situé à la racine du projet :
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope project

# Pour tous les projets du compte utilisateur :
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global
```

Ajouter `--dry-run` pour prévisualiser. `project` est le défaut ; sans `--target`,
le script utilise le répertoire courant. `--target` reste compatible avec les
anciens appels mais ne se combine pas avec `global`. Remplacer `opencode` par
`claude` ou `codex` au besoin. Voir les [emplacements et la maintenance par portée](docs/harness-installation.md).

### 1. Install the toolkit into the application

Keep the toolkit checkout separate from the application checkout. From a terminal:

```bash
git clone https://github.com/ahmadsarr/agent-migration-jvm.git
cd agent-migration-jvm

toolkit_dir="$PWD"
project_dir="/absolute/path/to/your-application"

bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir"
```

Replace `project_dir` with an existing directory. Preview the installation before
running the second command. If this project already has a toolkit installation,
use `--action update` instead; see the maintenance commands below.

Installed files include:

```text
your-application/
  .opencode/
    skills/jvm-spark-migration/
      SKILL.md
      references/targeted-regressions.md
      references/regression-report-template.md
    commands/
      audit.md
      compatibility.md
      plan.md
      regressions.md
      apply.md
      validate.md
      status.md
      rollback.md
  .jvm-migration/opencode.manifest
```

The manifest tracks installed files for update/uninstall. The installer does not
initialize `migration/state.json` or copy the checkpoint executor into the application.

### 2. Start OpenCode in the application

```bash
cd "$project_dir"
opencode
```

In OpenCode, ask it to load the skill and establish the scope, for example:

```text
Charge le skill jvm-spark-migration pour ce projet.
Commence par un audit en lecture seule et identifie les informations manquantes.
Ne choisis pas encore de JDK cible et ne modifie pas les sources.
Présente d'abord les résultats dans la conversation.
```

OpenCode discovers project skills under `.opencode/skills/` and loads them on
demand. See the official [skill documentation](https://opencode.ai/docs/skills/).

Type `/` to inspect the available commands. Names come from the installed file
names: `audit.md` defines `/audit`. The `# /migration:audit` headings inside generic
templates do not create a `/migration:audit` command. See OpenCode's
[custom command documentation](https://opencode.ai/docs/commands/).

### 3. Follow the migration workflow

Run these commands individually **inside OpenCode**, reviewing each result before
proceeding. Supply the selected batch, expected behavior and permissions in the
conversation; these generic templates do not declare `$ARGUMENTS` placeholders.

| Command | Expected work |
|---|---|
| `/audit` | Inventory the actual JDK, Scala, Spark, build and runtime configuration; report unknowns. |
| `/compatibility` | Check exact versions against official sources and propose a supported target JDK. |
| `/plan` | Define small reversible batches, critical behavioral risks, existing coverage and missing tests. |
| `/regressions` | Reuse adequate tests, add approved missing tests and capture the source-version baseline; rerun after the approved migration to compare target behavior. |
| `/apply` | Apply only the explicitly approved batch on a dedicated branch. |
| `/validate` | Compare baseline/target behavior and record evidence-backed Go/No-Go. |
| `/status` | Summarize migration artifacts, remaining checks and the next goal. |
| `/rollback` | Prepare or perform only the explicitly authorized recovery action. |

After reviewing the plan, an example scoped instruction is:

```text
Pour le lot 1, réutilise les tests qui couvrent déjà les risques identifiés.
Je t'autorise à ajouter les tests manquants dans les fichiers convenus,
à exécuter les tests locaux convenus et à écrire les rapports dans migration/.
Capture les résultats avec Java 11 et les dépendances actuelles avant la mise à jour.
Présente le diff de migration du lot 1 avant de l'appliquer.
```

Then use `/regressions`. After reviewing and authorizing the migration diff, use
`/apply`, followed by `/regressions` and `/validate` on the target environment.
Unavailable environments or unexecuted tests remain NOT_RUN. These commands are
instructions to the assistant; they do not automatically prove migration success.

### Reports and checkpoint state

With an authorized report destination, ask the assistant to persist assessment,
compatibility, plan and regression reports plus execution evidence. The proposed
layout and checkpoint initialization are described in
[migration/README.md](migration/README.md); the regression report template is
bundled in the installed skill's `references/` directory.

The optional checkpoint CLI is run from the toolkit checkout:

```bash
# Only after migration/state.json has been initialized and reconciled with Git.
python3 "$toolkit_dir/scripts/goal_executor.py" --project "$project_dir" status
```

It requires Python 3.9+ and Git. It validates recorded state; it does not execute
application tests. See [the executor guide](docs/goal-executor.md) for completion gates.

### Update or remove the installation

Use the same absolute `toolkit_dir` and `project_dir` values as above. First update
the toolkit checkout to the version you intend to install, then run:

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action update --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action update

# When you want to remove the installed toolkit files:
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --action uninstall
```

Updates and removal refuse locally modified or missing managed files. Preserve
your changes and resolve the reported conflict before retrying; there is no
`--force` option. Use `bash`, not `sh`, for the current installer.

### Troubleshooting and current limits

- If commands are absent, restart OpenCode from the application root and check
  `.opencode/commands/`. If the skill is absent, check its `SKILL.md` and OpenCode's
  skill permissions. You can also ask the assistant to read that file directly.
- The installed skill includes its compatibility, validation, reporting and
  orchestration references for all three assistants. Update older installations
  with `--action update` to receive them. Keep the toolkit checkout accessible
  for checkpoint templates, schemas and execution scripts, which are separate.
- Installer file distribution has been checked locally. Discovery and command
  execution in a real OpenCode session still need validation against your installed
  version; no end-to-end migration is claimed by installing the toolkit.

## Targeted regression tests
Use the `regressions` command template for a selected migration batch. The
[targeted regression workflow](skills/jvm-spark-migration/references/targeted-regressions.md)
connects actual library/JDK impacts to existing coverage, missing tests and
before/after execution evidence. The coding assistant performs this work in the
target application using its existing test framework and authorized scope.
The toolkit supplies instructions and a report template; it does not automatically
generate or run tests without the coding assistant and a target project.
