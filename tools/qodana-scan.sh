#!/bin/sh
# Run optional Kotlin/JVM inspections for a Git revision (HEAD by default).
# Usage: sh tools/qodana-scan.sh [revision]
set -eu

cd "$(git rev-parse --show-toplevel)"
revision=$(git rev-parse --verify --end-of-options "${1:-HEAD}^{commit}")
java_feature=$(git show "$revision:.java-version")
image=$(python3 -c 'import tomllib; print(tomllib.load(open("gradle/libs.versions.toml", "rb"))["versions"]["qodana-jvm-community-image"])')

output="$PWD/.gradle/qodana"
mkdir -p "$output/cache/gradle" "$output/runs"
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

git archive --output="$run/project.tar" "$revision"
tar -xf "$run/project.tar" -C "$run/project"
rm "$run/project.tar"
git -C "$run/project" init -q --template=
git -C "$run/project" add --all
git -C "$run/project" -c user.name='Qodana' -c user.email='qodana@example.test' \
  -c commit.gpgsign=false -c core.hooksPath=/dev/null commit -qm 'Local analysis snapshot'

docker run --rm "eclipse-temurin:${java_feature}-jdk" \
  tar -C /opt/java/openjdk -cf - . > "$run/temurin.tar"
tar -xf "$run/temurin.tar" -C "$run/temurin"
rm "$run/temurin.tar"
printf 'org.gradle.java.installations.paths=/opt/temurin\n' > "$output/cache/gradle/gradle.properties"

docker run --rm \
  --volume "$run/project:/data/project" \
  --volume "$run/results:/data/results" \
  --volume "$output/cache:/data/cache" \
  --volume "$run/temurin:/opt/temurin:ro" \
  "$image" scan --profile-name qodana.recommended --save-report --timeout 900000
