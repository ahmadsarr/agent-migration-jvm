# Versions du toolkit

`VERSION` est la source du numéro du toolkit au format `MAJOR.MINOR.PATCH`.
La première version préparée est `0.1.0` : une version initiale avant stabilisation,
qui ne constitue pas une certification de migrations applicatives.
Ce numéro est distinct du JDK, de Spring Boot et de Spec Kit (actuellement 1.2.2
pour le wrapper). Il ne change aucune version des applications cibles.

## Consulter la version

Depuis le checkout du toolkit :

```bash
bash scripts/install.sh --version
python3 scripts/speckit_opencode.py --version
```

Pour connaître la version installée dans un projet ou globalement :

```bash
bash scripts/install.sh --harness opencode --target /chemin/application --action status
bash scripts/install.sh --harness opencode --scope global --action status
```

Remplacer `opencode` par `claude` ou `codex`. Le statut indique la version du
checkout source, la version installée, la portée et l'emplacement. Il ne modifie
aucun fichier. Une installation absente ou présentant des conflits retourne un
code non nul. Un conflit invalide la confiance dans la version affichée.

L'installation copie `VERSION` vers `skills/jvm-spark-migration/TOOLKIT_VERSION`
sous la racine de l'assistant. Ce fichier est géré par le manifeste SHA-256,
comme les autres fichiers : une modification locale bloque la maintenance.
Les versions projet et globale restent indépendantes. Le numéro seul ne garantit
pas l'intégrité d'une installation ; les empreintes du manifeste décrivent ses fichiers.

## Installations existantes et mises à jour

Une installation créée avant le versionnement indique `Installed version: UNKNOWN`.
Le statut n'invente pas une version et n'ajoute pas de fichier. La mise à jour
avec le nouvel installateur ajoute le marqueur si les contrôles habituels passent :

```bash
bash scripts/install.sh --harness opencode --target /chemin/application --action update --dry-run
bash scripts/install.sh --harness opencode --target /chemin/application --action update
```

Pour le global, remplacer `--target ...` par `--scope global`. La désinstallation
retire aussi le marqueur. Ne pas éditer celui-ci pour simuler une mise à jour.
Le script utilise le checkout depuis lequel il est exécuté ; il ne télécharge pas
une version et ne compare pas les numéros pour empêcher un retour à une version antérieure.

## Rapports

Chaque nouveau `report.json` produit par `speckit_opencode.py` contient
`toolkit_version`, lu dans le checkout qui exécute le script. Cette valeur identifie
le wrapper utilisé ; elle ne prouve pas que les skills installés sont de la même
version. Utiliser `--action status` dans la portée choisie pour le vérifier.
Les anciens rapports ne sont pas réécrits. Le checkpoint `migration/state.json`
conserve son format actuel ; les rapports applicatifs restent produits par l'assistant.

## Préparer et publier une version

Le fichier `CHANGELOG.md` décrit les changements. Pour chaque version, mettre à jour
`VERSION`, documenter les évolutions et leurs effets sur les installations, puis
valider localement les tests Python et le cycle de l'installateur.

- PATCH : corrections compatibles.
- MINOR : fonctionnalités supplémentaires ; avant 1.0, annoncer explicitement
  toute incompatibilité dans le changelog.
- MAJOR : changements incompatibles après stabilisation en 1.0.

Après fusion du commit validé, publier un tag `v<version>` sur ce commit et une
release GitHub avec ses notes. Ne pas déplacer un tag publié. Les utilisateurs
peuvent ensuite sélectionner ce tag dans un checkout propre avant installation :

```bash
# Exemple de convention : utiliser uniquement un tag effectivement publié.
git fetch --tags origin
git switch --detach v0.1.0
bash scripts/install.sh --version
```

**Le tag et la release `v0.1.0` ne sont pas publiés par cette évolution.** La PR
prépare leur numérotation et leur traçabilité ; la publication est une étape
séparée sur le commit fusionné. Un checkout de développement portant le même
numéro peut contenir des modifications : conserver aussi sa révision Git dans
les preuves si une reproduction exacte est nécessaire.
