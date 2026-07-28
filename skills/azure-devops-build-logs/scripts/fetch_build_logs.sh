#!/usr/bin/env bash
set -euo pipefail

ORG="https://dev.azure.com/oec-eng"
PROJECT="terraform-gcp-infra"
BUILD_ID=""
DEFINITION_ID=""
LOG_ID=""
LATEST_LOG=0
ALL_LOGS=0
OUTPUT_DIR="/tmp/azure-devops-build-logs"
TAIL_LINES=0

usage() {
  cat <<'USAGE'
Usage:
  fetch_build_logs.sh --build-id <id> [--log-id <id>|--latest-log|--all-logs]
  fetch_build_logs.sh --definition-id <id> [--log-id <id>|--latest-log|--all-logs]

Options:
  --org <url>             Azure DevOps organization. Default: https://dev.azure.com/oec-eng
  --project <name>        Azure DevOps project. Default: terraform-gcp-infra
  --build-id <id>         Build/run id to inspect.
  --definition-id <id>    Pipeline definition id; script resolves the latest build.
  --log-id <id>           Specific log id to download.
  --latest-log            Download the highest log.id from the build timeline.
  --all-logs              Download every log id present in the build timeline.
  --output-dir <path>     Output directory. Default: /tmp/azure-devops-build-logs
  --tail <n>              Print the last n lines after download. Default: 0.
  -h, --help              Show this help.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --org)
      ORG="${2:?missing value for --org}"
      shift 2
      ;;
    --project)
      PROJECT="${2:?missing value for --project}"
      shift 2
      ;;
    --build-id)
      BUILD_ID="${2:?missing value for --build-id}"
      shift 2
      ;;
    --definition-id|--definitionid)
      DEFINITION_ID="${2:?missing value for --definition-id}"
      shift 2
      ;;
    --log-id|--logid)
      LOG_ID="${2:?missing value for --log-id}"
      shift 2
      ;;
    --latest-log)
      LATEST_LOG=1
      shift
      ;;
    --all-logs)
      ALL_LOGS=1
      shift
      ;;
    --output-dir)
      OUTPUT_DIR="${2:?missing value for --output-dir}"
      shift 2
      ;;
    --tail)
      TAIL_LINES="${2:?missing value for --tail}"
      if ! [[ "$TAIL_LINES" =~ ^[0-9]+$ ]]; then
        echo "--tail must be a non-negative integer." >&2
        exit 2
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 127
  fi
}

require_cmd az
require_cmd jq

if [[ -z "$BUILD_ID" && -z "$DEFINITION_ID" ]]; then
  echo "Provide --build-id or --definition-id." >&2
  usage >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR"

if [[ -z "$BUILD_ID" ]]; then
  echo "Resolving latest build for definitionId=$DEFINITION_ID..."
  BUILD_ID="$(
    az pipelines build list \
      --definition-ids "$DEFINITION_ID" \
      --top 1 \
      --org "$ORG" \
      --project "$PROJECT" \
      --query '[0].id' \
      -o tsv
  )"
  if [[ -z "$BUILD_ID" || "$BUILD_ID" == "None" ]]; then
    echo "No build found for definitionId=$DEFINITION_ID." >&2
    exit 1
  fi
fi

SUMMARY_JSON="$OUTPUT_DIR/build-${BUILD_ID}-summary.json"
TIMELINE_JSON="$OUTPUT_DIR/build-${BUILD_ID}-timeline.json"
TIMELINE_TSV="$OUTPUT_DIR/build-${BUILD_ID}-timeline.tsv"

echo "Fetching build summary: buildId=$BUILD_ID"
az pipelines build show \
  --id "$BUILD_ID" \
  --org "$ORG" \
  --project "$PROJECT" \
  -o json > "$SUMMARY_JSON"

echo "Fetching build timeline via az devops invoke..."
az devops invoke \
  --area build \
  --resource timeline \
  --route-parameters project="$PROJECT" buildId="$BUILD_ID" \
  --org "$ORG" \
  --api-version 7.1 \
  -o json > "$TIMELINE_JSON"

jq -r '
  ["log_id","type","name","state","result","startTime","finishTime"],
  (.records[]
    | select(.log.id != null)
    | [
        (.log.id|tostring),
        (.type // ""),
        (.name // ""),
        (.state // ""),
        (.result // ""),
        (.startTime // ""),
        (.finishTime // "")
      ])
  | @tsv
' "$TIMELINE_JSON" > "$TIMELINE_TSV"

download_log() {
  local log_id="$1"
  local log_json="$OUTPUT_DIR/build-${BUILD_ID}-log-${log_id}.json"
  local log_txt="$OUTPUT_DIR/build-${BUILD_ID}-log-${log_id}.log"

  echo "Fetching logId=$log_id via az devops invoke..." >&2
  az devops invoke \
    --area build \
    --resource logs \
    --route-parameters project="$PROJECT" buildId="$BUILD_ID" logId="$log_id" \
    --org "$ORG" \
    --api-version 7.1 \
    -o json > "$log_json"

  jq -r '
    if type == "object" and (.value | type) == "array" then .value[]
    elif type == "array" then .[]
    elif type == "string" then .
    else tostring
    end
  ' "$log_json" > "$log_txt"

  echo "$log_txt"
}

if [[ "$ALL_LOGS" -eq 1 ]]; then
  LOG_IDS=($(jq -r '.records[] | select(.log.id != null) | .log.id' "$TIMELINE_JSON" | sort -n -u))
  if [[ "${#LOG_IDS[@]}" -eq 0 ]]; then
    echo "No log ids found in timeline." >&2
    exit 1
  fi
  COMBINED_LOG="$OUTPUT_DIR/build-${BUILD_ID}-combined.log"
  : > "$COMBINED_LOG"
  for id in "${LOG_IDS[@]}"; do
    path="$(download_log "$id")"
    {
      echo
      echo "===== logId=$id ====="
      cat "$path"
    } >> "$COMBINED_LOG"
  done
  echo "Summary: $SUMMARY_JSON"
  echo "Timeline: $TIMELINE_TSV"
  echo "Combined log: $COMBINED_LOG"
  exit 0
fi

if [[ -z "$LOG_ID" ]]; then
  if [[ "$LATEST_LOG" -ne 1 ]]; then
    LATEST_LOG=1
  fi
  LOG_ID="$(
    jq -r '
      [.records[] | select(.log.id != null) | .log.id]
      | sort
      | last // empty
    ' "$TIMELINE_JSON"
  )"
  if [[ -z "$LOG_ID" || "$LOG_ID" == "null" ]]; then
    echo "No log id found in timeline." >&2
    exit 1
  fi
fi

LOG_TXT="$(download_log "$LOG_ID")"

BUILD_STATUS="$(jq -r '.status // ""' "$SUMMARY_JSON")"
BUILD_RESULT="$(jq -r '.result // ""' "$SUMMARY_JSON")"
BUILD_NUMBER="$(jq -r '.buildNumber // ""' "$SUMMARY_JSON")"
DEFINITION_NAME="$(jq -r '.definition.name // ""' "$SUMMARY_JSON")"

echo
echo "Build: $BUILD_ID ${BUILD_NUMBER:+($BUILD_NUMBER)}"
echo "Definition: ${DEFINITION_NAME:-n/a}"
echo "Status/result: ${BUILD_STATUS:-n/a}/${BUILD_RESULT:-n/a}"
echo "Summary: $SUMMARY_JSON"
echo "Timeline: $TIMELINE_TSV"
echo "Log: $LOG_TXT"
if [[ "$TAIL_LINES" -gt 0 ]]; then
  echo
  echo "Last $TAIL_LINES log lines:"
  tail -n "$TAIL_LINES" "$LOG_TXT"
else
  echo "Log preview disabled by default. Re-run with --tail N if a sanitized preview is needed."
fi
