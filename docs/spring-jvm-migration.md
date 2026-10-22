# Migrer une application JVM Spring / Spring Boot

Ce parcours complète le [guide général](guide-utilisation.md#migration).
Il s'applique aux applications Spring seules comme aux projets qui combinent
Spring avec d'autres composants. Spark et Scala ne sont requis que si présents.
Le skill conserve son nom `jvm-spark-migration` pour les installations existantes.

## Installer ou mettre à jour

Depuis le checkout du toolkit, définir les chemins et installer les instructions :

```bash
toolkit_dir="$PWD"
project_dir="/chemin/absolu/vers/application-spring"
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir" --dry-run
bash "$toolkit_dir/scripts/install.sh" --harness opencode --target "$project_dir"
```

Pour une installation existante, utiliser `--action update` sur les deux commandes.
Le profil `references/spring-migration.md` est distribué avec le skill aux trois
assistants : OpenCode, Claude Code et Codex. Les mêmes règles de conflits s'appliquent.

```bash
cd "$project_dir"
opencode
```

Dans la conversation :

```text
Charge le skill jvm-spark-migration et son profil references/spring-migration.md.
Je souhaite migrer le JDK de cette application Spring.
Commence par un audit en lecture seule : JDK de build et runtime, versions exactes
Spring Boot/Framework, Security, Data/Hibernate, Cloud, BOM et surcharges,
Maven/Gradle, profils, serveur et image de déploiement.
Distingue une montée de JDK seule d'une montée majeure de Spring.
Propose une cible uniquement après vérification des compatibilités officielles.
N'impose pas de vérifications Spark ou Scala si le projet ne les utilise pas.
```

## Suivre les étapes

| Étape OpenCode | Résultat à examiner |
|---|---|
| `/audit` | Versions exactes, dépendances effectives, configuration, usages et inconnues |
| `/compatibility` | Matrice JDK/build/Boot/Framework/Cloud/serveur et sources officielles versionnées |
| `/plan` | Lots réversibles, risques réels, tests réutilisés et lacunes à combler |
| `/regressions` | Tests manquants autorisés et référence exécutée avant mise à jour |
| `/apply` | Changements du lot autorisé sur une branche dédiée |
| `/regressions`, puis `/validate` | Comparaison source/cible et décision Go/No-Go avec preuves |

Pour Spring sans Boot, examiner directement Framework, la gestion des dépendances
et le conteneur de déploiement. Ne pas supposer l'existence d'un BOM Boot.
Pour Boot, examiner aussi les versions gérées et les surcharges : changer
indépendamment Hibernate ou Security peut sortir de la combinaison attendue.

Une montée de JDK n'impose pas automatiquement une montée majeure de Boot. Si le
JDK cible exige un changement de framework, documenter la combinaison intermédiaire
supportée, ou justifier un lot couplé quand les transitions ne peuvent être séparées.

## Points sensibles

- **Boot 2 vers Boot 3** : consulter le guide officiel. Boot 3 requiert au minimum
  Java 17 et s'appuie sur Framework 6 / Jakarta EE ; vérifier les exigences de la
  version exacte pour le JDK choisi. Ce minimum ne garantit pas tous les JDK futurs.
- **Jakarta** : migrer uniquement les API EE concernées et leurs dépendances.
  Ne pas remplacer globalement `javax.*` : `javax.sql` et `javax.crypto`, par exemple,
  restent des API Java SE. Vérifier aussi les bibliothèques et le serveur de servlet.
- **Security** : préserver les routes autorisées/interdites et les contrats
  d'authentification. Ne pas désactiver CSRF ou des filtres pour faire passer les tests.
- **Hibernate/JPA** : comparer requêtes, pagination, ordre contractuel, transactions,
  chargement et schéma avec une base représentative du dialecte utilisé.
- **Configuration et exploitation** : profils, binding des propriétés, démarrage,
  health/readiness, arrêt propre et métriques utilisées par l'exploitation.

Pour une autre transition majeure, lire son guide spécifique ; ne pas extrapoler
les instructions Boot 2 → 3 à toutes les versions.

## Tests ciblés avant/après

Inspecter les tests existants avant toute addition. Sélectionner uniquement les
risques réellement présents et mal couverts, par exemple :

| Contrat | Vérification possible avec les outils existants |
|---|---|
| Démarrage/configuration | Chargement du contexte avec les profils représentatifs et vérification des propriétés attendues |
| API HTTP | Routes, méthodes, codes, headers, erreurs et validation via les tests MVC/WebFlux du projet |
| JSON | Noms de champs, valeurs nulles, dates et compatibilité des payloads |
| Sécurité | Requêtes acceptées et refusées, authentification, rôles et règles effectives |
| Persistance | Résultats des requêtes, tri explicite, pagination et rollback transactionnel |
| Messages ou batch | Sérialisation, retries, idempotence et reprise si utilisés |

Un simple `contextLoads` ne couvre pas les contrats métier. Une base en mémoire
ne suffit pas à prouver l'absence de régression liée à un dialecte SQL différent.
Utiliser les infrastructures de test déjà présentes ; ne pas imposer un nouveau
framework de tests ou Testcontainers si la couverture existante convient.

Le [rapport de régression](../skills/jvm-spark-migration/references/regression-report-template.md)
doit relier chaque risque à ses assertions et aux exécutions source/cible :
révisions, versions, profils sans secrets, données, commandes, nombres de tests
exécutés/ignorés, codes de sortie et logs. Garder `NOT_RUN` pour toute exécution
indisponible ; une lacune critique empêche Go. Revenir à l'ancien JAR ne restaure
pas nécessairement un schéma ou des messages modifiés : prévoir leur récupération.

## Utiliser Spec Kit

Le [wrapper OpenCode + Spec Kit](speckit-opencode.md) accepte vos propres fichiers
`--spec-file` et `--plan-file`. Décrire dans la spécification les comportements
Spring à préserver et les critères attendus ; dans le plan, demander l'inspection
des versions et du profil Spring avant tout choix de cible. Installer le skill
dans l'application et sélectionner son répertoire avec `--project`.
Les exemples existants sous `examples/speckit/` concernent une évolution du toolkit :
les adapter pour une migration applicative. Le wrapper n'ajoute pas automatiquement
des tests Spring et ne valide pas une migration sans exécutions applicatives.

## Références

Le [profil distribué](../skills/jvm-spark-migration/references/spring-migration.md)
contient les sources officielles Boot, Framework, Security et Cloud. Utiliser les
sélecteurs de version et consigner la page exacte consultée dans la matrice de
compatibilité. Aucun choix de cible n'est figé dans ce guide.
