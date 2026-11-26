#!/bin/sh
# Run optional Kotlin/JVM inspections for a Git revision (HEAD by default).
# Usage: sh tools/qodana-scan.sh [revision]
set -eu

cd "$(git rev-parse --show-toplevel)"
revision=$(git rev-parse --verify --end-of-options "${1:-HEAD}^{commit}")
java_feature=$(git show "$revision:.java-version")
image=$(python3 -c 'import tomllib; print(tomllib.load(open("gradle/libs.versions.toml", "rb"))["versions"]["qodana-jvm-community-image"])')

# Qodana loads installed plugins from its cache even when the revision has no plugin declaration.
if ! plugin_config=$(git rev-parse --verify --end-of-options "$revision:qodana.yaml" 2>/dev/null); then
  plugin_config=no-config
fi

output="$PWD/.gradle/qodana"
gradle_cache="$output/cache/gradle"
plugin_cache="$output/plugin-cache/$plugin_config"
mkdir -p "$gradle_cache" "$output/runs" "$plugin_cache"
lock="$output/cache.lock"
if ! mkdir "$lock"; then
  printf '%s\n' 'The local Qodana cache is in use.' >&2
  exit 1
fi
trap 'rmdir "$lock"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

run=$(mktemp -d "$output/runs/$revision.XXXXXX")
trap 'rm -rf "$run/temurin"; rmdir "$lock"' EXIT
mkdir "$run/project" "$run/results" "$run/temurin"
printf '%s\n' "$revision" > "$run/revision"
printf 'Qodana report directory: %s\n' "$run/results"

git archive --output="$run/project.tar" "$revision" \
  -- . ':(top,exclude,literal).idea/inspectionProfiles/Project_Default.xml'
tar -xf "$run/project.tar" -C "$run/project"
rm "$run/project.tar"

entry_points_path=.qodana/profiles/spring-beans.xml
entry_points_config=no-entry-points
if [ -f "$run/project/$entry_points_path" ]; then
  project_idea="$run/project/.idea"
  if [ -L "$project_idea" ] || [ -e "$project_idea/misc.xml" ] || [ -L "$project_idea/misc.xml" ]; then
    printf '%s\n' 'Cannot install Qodana entry points over archived .idea settings.' >&2
    exit 1
  fi
  entry_points_config=$(git rev-parse --verify --end-of-options "$revision:$entry_points_path")
  mkdir -p "$project_idea"
  git cat-file blob "$entry_points_config" > "$project_idea/misc.xml"
fi

# Qodana restores .idea settings from its analysis cache before reading the project.
analysis_cache="$output/analysis-cache/without-editor-profile/$entry_points_config"
mkdir -p "$analysis_cache"

git -C "$run/project" init -q --template=
git -C "$run/project" add --all
git -C "$run/project" -c user.name='Qodana' -c user.email='qodana@example.test' \
  -c commit.gpgsign=false -c core.hooksPath=/dev/null commit -qm 'Local analysis snapshot'

docker run --rm "eclipse-temurin:${java_feature}-jdk" \
  tar -C /opt/java/openjdk -cf - . > "$run/temurin.tar"
tar -xf "$run/temurin.tar" -C "$run/temurin"
rm "$run/temurin.tar"
printf 'org.gradle.java.installations.paths=/opt/temurin\n' > "$gradle_cache/gradle.properties"

docker run --rm \
  --volume "$run/project:/data/project" \
  --volume "$run/results:/data/results" \
  --volume "$analysis_cache:/data/cache" \
  --volume "$gradle_cache:/data/cache/gradle" \
  --volume "$plugin_cache:/data/cache/plugins" \
  --volume "$run/temurin:/opt/temurin:ro" \
  "$image" scan --profile-name qodana.recommended --save-report --timeout 900000
