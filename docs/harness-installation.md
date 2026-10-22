# Installation des assistants

L'installateur configure les instructions du toolkit dans le projet courant ou
globalement pour l'utilisateur.
Installer séparément le CLI de l'assistant et son fournisseur de modèle.
Pour le parcours complet, consulter le [guide d'utilisation](guide-utilisation.md).

## Choisir la portée

Depuis le checkout du toolkit, conserver son chemin absolu :

```bash
toolkit_dir="$PWD"
```

Pour installer **dans le projet courant**, lancer depuis la racine de ce projet :

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope project --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope project
```

`project` est la portée par défaut. Sans `--target`, le répertoire courant est
utilisé, même s'il s'agit d'un sous-dossier : le script ne cherche pas la racine
Git automatiquement. `--target /chemin/projet` reste disponible pour désigner
explicitement un autre projet, comme dans les versions précédentes.

Pour installer **globalement pour votre utilisateur**, depuis n'importe où :

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global
```

Aucun `sudo` n'est nécessaire. `--scope global` et `--target` sont incompatibles.
Le mode global rend les instructions accessibles depuis plusieurs projets ; il
n'installe pas le CLI, ne migre pas les applications et ne globalise ni les rapports,
ni les checkpoints, ni les spécifications Spec Kit.

| Assistant | Racine globale | Contenu |
|---|---|---|
| OpenCode | `${XDG_CONFIG_HOME:-$HOME/.config}/opencode` | `skills/jvm-spark-migration/`, `commands/` |
| Claude Code | `${CLAUDE_CONFIG_DIR:-$HOME/.claude}` | `skills/jvm-spark-migration/`, `commands/`, `agents/` |
| Codex | `$HOME/.agents` | `skills/jvm-spark-migration/` |

Le manifeste global est dans `<racine globale>/.jvm-migration/<assistant>.manifest`.
Les chemins de configuration doivent être absolus ; les ancêtres symboliques sont
refusés. Le dry-run ne crée pas les répertoires globaux absents. Le script ne lit
pas `CODEX_HOME` pour les skills utilisateur, découverts sous `$HOME/.agents/skills`.

Une installation projet et une installation globale ont des manifestes distincts.
La suppression de l'une préserve l'autre. Éviter les copies divergentes d'un même
skill : leur découverte/priorité dépend de l'assistant, et Codex peut afficher
plusieurs skills de même nom. Retirer explicitement l'installation devenue inutile.

Références : [OpenCode skills](https://opencode.ai/docs/skills/),
[OpenCode commands](https://opencode.ai/docs/commands/),
[Claude Code skills](https://code.claude.com/docs/en/skills),
[Codex skills](https://developers.openai.com/codex/skills/).

## Prérequis et installation

Utiliser Bash 4+, `sha256sum`, GNU `find`, `sort` et coreutils. Depuis le checkout
du toolkit, remplacer le chemin cible par un répertoire existant :

```bash
bash scripts/install.sh --harness opencode --target /chemin/vers/application --dry-run
bash scripts/install.sh --harness opencode --target /chemin/vers/application
```

Remplacer `opencode` par `claude` ou `codex` selon l'assistant.

| Assistant | Skill | Commandes | Agents |
|---|---|---|---|
| OpenCode | `.opencode/skills/jvm-spark-migration/` | `.opencode/commands/` | Non installés |
| Claude Code | `.claude/skills/jvm-spark-migration/` | `.claude/commands/` | `.claude/agents/` |
| Codex | `.agents/skills/jvm-spark-migration/` | Non installées | Non installés |

Le manifeste `.jvm-migration/<assistant>.manifest` contient les chemins et
empreintes SHA-256 des fichiers gérés. L'installation ne crée pas le checkpoint
`migration/state.json` et ne modifie pas les sources de l'application.

## Maintenance

Garder la même portée et les mêmes variables de configuration que lors de
l'installation. Pour le global :

```bash
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global --action update --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global --action update
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global --action uninstall --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --scope global --action uninstall
```

Pour un projet explicite (ou omettre `--target` depuis sa racine) :

```bash
bash scripts/install.sh --harness opencode --target /chemin/vers/application --action update --dry-run
bash scripts/install.sh --harness opencode --target /chemin/vers/application --action update
bash scripts/install.sh --harness opencode --target /chemin/vers/application --action uninstall --dry-run
bash scripts/install.sh --harness opencode --target /chemin/vers/application --action uninstall
```

Les conflits sont vérifiés avant écriture. Les fichiers gérés modifiés ou manquants
empêchent la mise à jour ou la suppression : préserver vos changements et résoudre
le conflit. Il n'existe pas d'option `--force`. Utiliser `bash`, pas `sh`.

L'installation n'est pas transactionnelle : une erreur d'entrée/sortie peut laisser
des copies partielles. Les limites concernant les liens symboliques et les
modifications concurrentes sont détaillées dans la [référence installateur](harness-installer-v2.md).
La présence des fichiers ne prouve pas leur découverte par votre version de CLI.
Pour les références du skill non distribuées, voir le
[dépannage](guide-utilisation.md#depannage).
