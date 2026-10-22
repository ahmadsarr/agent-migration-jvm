# Installation des assistants

L'installateur configure les instructions du toolkit dans un projet existant.
Installer séparément le CLI de l'assistant et son fournisseur de modèle.
Pour le parcours complet, consulter le [guide d'utilisation](guide-utilisation.md).

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
