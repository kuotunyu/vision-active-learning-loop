#!/usr/bin/env bash
set -euo pipefail
set -C

base_digest='sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
# Offline stage contract: docker run --network none.
run_id=''
attempt_id=''
image_tag=''
image_digest=''
host_artifact_root=''

while (($#)); do
  case "$1" in
    --run-id) run_id=$2; shift 2 ;;
    --attempt-id) attempt_id=$2; shift 2 ;;
    --image-tag) image_tag=$2; shift 2 ;;
    --image-digest) image_digest=$2; shift 2 ;;
    --host-artifact-root) host_artifact_root=$2; shift 2 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[[ -n "$run_id" && -n "$image_tag" && -n "$image_digest" && -n "$host_artifact_root" ]]
[[ "$attempt_id" == primary || "$attempt_id" == clean-a || "$attempt_id" == clean-b ]]
if [[ -v VAL_DATA_ROOT ]]; then
  echo 'VAL_DATA_ROOT must remain unset' >&2
  exit 2
fi

campaign_root=$(cd "$host_artifact_root" && pwd -P)
attempt_root="$campaign_root/$attempt_id"
mkdir "$attempt_root"
mkdir "$attempt_root/wave0"
mkdir "$attempt_root/wave0/receipts"
mkdir "$attempt_root/wave0/checkpoints"
mkdir "$attempt_root/wave0/model_cache"
mkdir "$attempt_root/wave0/uv_cache"
mkdir "$attempt_root/audit"
worktree=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)

tree_bytes() {
  find "$attempt_root" -type f -printf '%s\n' | awk '{sum += $1} END {print sum + 0}'
}

run_stage() {
  local name=$1 network=$2 receipt=$3
  shift 3
  local log="$attempt_root/audit/$name.log"
  local record="$attempt_root/audit/$name.txt"
  local started finished exit_code receipt_hash
  local -a docker_args=(
    run --rm --gpus all --network "$network"
    --workdir /workspace --entrypoint val
    -e VAL_ARTIFACT_ROOT=/artifacts
    -e "VAL_OBSERVED_BASE_IMAGE_DIGEST=$base_digest"
    -e "VAL_RUNTIME_IMAGE_DIGEST=$image_digest"
    -e PYTHONPATH=/workspace/src
    -e UV_CACHE_DIR=/artifacts/wave0/uv_cache
    -e CUBLAS_WORKSPACE_CONFIG=:4096:8
    -v "$worktree:/workspace:ro"
    -v "$attempt_root:/artifacts:rw"
  )
  if [[ "$network" == none ]]; then
    docker_args+=( -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 )
  fi
  docker_args+=( "$image_tag" "$@" )
  printf 'docker' > "$record"
  printf ' %q' "${docker_args[@]}" >> "$record"
  printf '\n' >> "$record"
  started=$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)
  set +e
  docker "${docker_args[@]}" > "$log" 2>&1
  exit_code=$?
  set -e
  finished=$(date -u +%Y-%m-%dT%H:%M:%S.%NZ)
  receipt_hash='missing'
  if [[ -f "$attempt_root/wave0/receipts/$receipt" ]]; then
    receipt_hash=$(sha256sum "$attempt_root/wave0/receipts/$receipt" | awk '{print $1}')
  fi
  {
    printf 'run_id=%s\n' "$run_id"
    printf 'attempt_id=%s\n' "$attempt_id"
    printf 'stage=%s\n' "$name"
    printf 'exit_code=%s\n' "$exit_code"
    printf 'started_at=%s\n' "$started"
    printf 'finished_at=%s\n' "$finished"
    printf 'image_tag=%s\n' "$image_tag"
    printf 'image_digest=%s\n' "$image_digest"
    printf 'network=%s\n' "$network"
    printf 'val_data_root_unset=true\n'
    printf 'receipt=%s\n' "$receipt"
    printf 'receipt_sha256=%s\n' "$receipt_hash"
    printf 'attempt_disk_bytes=%s\n' "$(tree_bytes)"
    find "$attempt_root/wave0/checkpoints" -type f -exec sha256sum {} \;
  } >> "$record"
  if ((exit_code != 0)); then
    echo "Wave 0 stage $name failed with exit code $exit_code" >&2
    exit "$exit_code"
  fi
  [[ -f "$attempt_root/wave0/receipts/$receipt" ]]
}

docker image inspect "$image_tag" > "$attempt_root/audit/image-inspect.json"

run_stage 01-environment none environment.json \
  environment check --config /workspace/configs/environment/wave0.yaml \
  --run-id "$run_id" --output /artifacts/wave0/receipts/environment.json
run_stage 02-model-assets bridge model-assets.json \
  assets verify --config /workspace/configs/models/pinned-models.yaml \
  --cache-root /artifacts/wave0/model_cache \
  --output /artifacts/wave0/receipts/model-assets.json --run-id "$run_id" --download
run_stage 03-model-contract none model-contract.json \
  probe model-contract --assets /artifacts/wave0/receipts/model-assets.json \
  --environment /artifacts/wave0/receipts/environment.json \
  --fixtures /workspace/fixtures/synthetic/wave0/fixture-manifest.json \
  --run-id "$run_id" --output /artifacts/wave0/receipts/model-contract.json
run_stage 04-feasibility-a none feasibility-a.json \
  probe training-feasibility --model-contract /artifacts/wave0/receipts/model-contract.json \
  --checkpoint-root /artifacts/wave0/checkpoints/feasibility-a \
  --run-id "$run_id" --output /artifacts/wave0/receipts/feasibility-a.json
run_stage 05-feasibility-b none feasibility-b.json \
  probe training-feasibility --model-contract /artifacts/wave0/receipts/model-contract.json \
  --checkpoint-root /artifacts/wave0/checkpoints/feasibility-b \
  --run-id "$run_id" --output /artifacts/wave0/receipts/feasibility-b.json

echo 'WAVE0_A2_ATTEMPT_PASS / WAVE1_NOT_STARTED'
