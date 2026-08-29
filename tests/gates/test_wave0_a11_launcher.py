"""PowerShell adapter tests for the Wave 0 A11 two-phase launcher."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest

from vision_active_learning_loop.gates import statistical_replay

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "run_wave0_a11.ps1"
_DOCKERFILE = _ROOT / "docker" / "wave0.Dockerfile"
_SOURCE = "1" * 40
_SPEC = "b59b0d4407b98b460f6166ea7288ba6021dc7a78"
_PLAN = "2" * 40
_BRANCH = "codex/wave0-model-contract"
_OWNER = "OWNER-A11-TEST"
_BASE = "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
_GPU = "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63"
_HISTORICAL_FILES_SHA256 = (
    "e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95"
)
_HISTORICAL_IMAGES_SHA256 = (
    "9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f"
)
_FAILED_RUN_ID = "wave0-a11-calibration-20260828T045848083Z-b9917463"
_FAILED_VALIDATION_ID = "wave0-a11-validation-20260828T045848091Z-084431a4"
_FAILED_RUN_SHA256 = "fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b"
_FAILED_OWNER = "OWNER-A11-RUNTIME-20260828-01"
_FAILED_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "2622e402e4f5-20260828T045848083Z-b9917463"
)
_FAILED_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "2622e402e4f5-20260828T045848091Z-084431a4"
)
_FAILED_IMAGE_ID = (
    "sha256:52b62e99d65269649d1e75e7397e9cab" "7d20cc5fe0e5dc46d661b1ec6625b0d5"
)
_TIMEOUT_RUN_ID = "wave0-a11-calibration-20260828T114911289Z-fe8b7000"
_TIMEOUT_VALIDATION_ID = "wave0-a11-validation-20260828T114911296Z-3107aff0"
_TIMEOUT_OWNER = "steven001"
_TIMEOUT_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "1445a90b799b-20260828T114911289Z-fe8b7000"
)
_TIMEOUT_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "1445a90b799b-20260828T114911296Z-3107aff0"
)
_TIMEOUT_RUN_SHA256 = "8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b"
_TIMEOUT_FILES = [
    {
        "path": "audit/00-identity.json",
        "size": 2873,
        "sha256": "df1b6f37bfd9f7bce399f3a8b481bba564b5cacdd397ca82723100802b4bcec3",
    },
    {
        "path": "audit/01-gpu-preflight.json",
        "size": 125,
        "sha256": "de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7",
    },
    {
        "path": "audit/10-build.json",
        "size": 1234,
        "sha256": "d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66",
    },
    {
        "path": "audit/10-build.stderr.log",
        "size": 865210,
        "sha256": "50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e",
    },
    {
        "path": "audit/10-build.stdout.log",
        "size": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    },
]
_STREAM_RUN_ID = "wave0-a11-calibration-20260828T172921151Z-a0f55fa1"
_STREAM_VALIDATION_ID = "wave0-a11-validation-20260828T172921161Z-70928997"
_STREAM_OWNER = "steven002"
_STREAM_SOURCE = "ff5cfac5820415662e608886f1a10d7892f3ee00"
_STREAM_RUN_SHA256 = "628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2"
_STREAM_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "ff5cfac58204-20260828T172921151Z-a0f55fa1"
)
_STREAM_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "ff5cfac58204-20260828T172921161Z-70928997"
)
_STREAM_IMAGE_ID = (
    "sha256:0a92de665d56dc4c4dc859cc3723444c" "b4b6c06e04308ee574f93befd4da7efd"
)
_STREAM_RELEASE_SHA256 = (
    "72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93"
)
_STREAM_RELEASED_SHA256 = (
    "a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f"
)
_AGGREGATE_RUN_ID = "wave0-a11-calibration-20260829T050706309Z-f5a0129e"
_AGGREGATE_VALIDATION_ID = "wave0-a11-validation-20260829T050706319Z-c6652f48"
_AGGREGATE_OWNER = "steven003"
_AGGREGATE_SOURCE = "77f8eecb3b8c0f471a4e980269187ac02a3b9ebc"
_AGGREGATE_RUN_SHA256 = (
    "f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717"
)
_AGGREGATE_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "77f8eecb3b8c-20260829T050706309Z-f5a0129e"
)
_AGGREGATE_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "77f8eecb3b8c-20260829T050706319Z-c6652f48"
)
_AGGREGATE_IMAGE_ID = (
    "sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e"
)
_AGGREGATE_RELEASE_SHA256 = (
    "aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1"
)
_AGGREGATE_RELEASED_SHA256 = (
    "b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c"
)
_AGGREGATE_REPLICA_DIRECTORIES = [
    f"wave0/checkpoints/calibration-{index:02d}" for index in range(12)
]
_AGGREGATE_CHECKPOINT_FILES = [
    f"wave0/checkpoints/calibration-{index:02d}/step-000001.pt" for index in range(12)
]
_AGGREGATE_DIRECTORIES = [
    "audit",
    "wave0",
    "wave0/checkpoints",
    *_AGGREGATE_REPLICA_DIRECTORIES,
    "wave0/model_cache",
    "wave0/model_cache/snapshots",
    "wave0/model_cache/snapshots/facebook--dinov2-small",
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees"
    ),
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd",
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees"
    ),
    "wave0/receipts",
]
_AGGREGATE_KEY_FILES = [
    {
        "path": "audit/00-identity.json",
        "size": 2873,
        "sha256": "dce0706a572cdb5e72a8b28aad61750ee799e0eae7164ae1b5c6a0c22f1ffe4c",
    },
    {
        "path": "audit/10-build.json",
        "size": 1234,
        "sha256": "c173d63a7428792c503a90ef095e1e8055c7ba8d7d112b54ea5a318fa1675eab",
    },
    {
        "path": "audit/11-image-inspect.json",
        "size": 682,
        "sha256": "c355d995173db7b7600ad1dc25774f28e76f620300252f165288797c931b8b81",
    },
    {
        "path": "audit/20-cache-preflight.json",
        "size": 1900,
        "sha256": "0c67229f0731b1e573f84a1ca3b97fb8aa2e51e4157e66c644133e2037c00273",
    },
    {
        "path": "audit/30-environment.json",
        "size": 1995,
        "sha256": "343602c0ad150e9b6642a31d3f2304e816ae8819b706d7774371625ed7fe753c",
    },
    {
        "path": "audit/31-model-assets.json",
        "size": 2051,
        "sha256": "e734f83f4f9149ea002982c6a48997445d71ba24b2c9424519f025dd63bbe851",
    },
    {
        "path": "audit/32-model-contract.json",
        "size": 2232,
        "sha256": "db0bb5710a3c6cd37a68f8142d43d2e2633254eca936be00c0faceefee6cd50c",
    },
    {
        "path": "audit/60-historical-preservation.json",
        "size": 301,
        "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d",
    },
    {
        "path": "audit/70-phase-manifest.json",
        "size": 9990,
        "sha256": "82122edec3b647c39946bdba6ebfa3c74d36065a084632e8d45c38b31eaaf97a",
    },
    {
        "path": "audit/71-aggregate-gate.json",
        "size": 1287,
        "sha256": "5772642484357bdfa4b7132bdbea974092c823e1207c57b60f7aec31ce7f22f3",
    },
    {
        "path": "audit/71-aggregate-gate.stderr.log",
        "size": 31,
        "sha256": "a336516b29c7b7fd395d6b2008409a5d8018b5d9c5616831d369cbd15078a812",
    },
    {
        "path": "audit/78-failure-diagnostic.json",
        "size": 855,
        "sha256": "40f1163d031fc68555363980b57821f87b103fdffd0e33880f0941361ae42338",
    },
    {
        "path": "audit/79-historical-preservation-final.json",
        "size": 301,
        "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d",
    },
    {
        "path": "audit/80-campaign-result.json",
        "size": 762,
        "sha256": "b4f2c8fa42384ae4791071b828f2cf0fccc9e50f9e2e69e928a8b9a583b2047e",
    },
    {
        "path": "audit/81-campaign-file-manifest.json",
        "size": 35243,
        "sha256": "02f7a06d64969ed4ebe2bb1a575ba7308279cee5b3f3ae51663fceb676cc4eec",
    },
    {
        "path": "audit/82-campaign-closure.json",
        "size": 660,
        "sha256": "1f65ea6261fabb007be1f15a457e2c9ff71925251c5b3af568e061890556e219",
    },
    {
        "path": "wave0/receipts/model-contract.json",
        "size": 9623,
        "sha256": "5589eb3e64fe9727212e3467f9e3ca6979e008b31e69e5a8ace0e0919607de9d",
    },
]
_STREAM_DIRECTORIES = [
    "audit",
    "wave0",
    "wave0/checkpoints",
    "wave0/model_cache",
    "wave0/model_cache/snapshots",
    "wave0/model_cache/snapshots/facebook--dinov2-small",
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download"
    ),
    (
        "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees"
    ),
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd",
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download"
    ),
    (
        "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/"
        "cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees"
    ),
    "wave0/receipts",
]
_STREAM_KEY_FILES = [
    {
        "path": "audit/00-identity.json",
        "size": 2873,
        "sha256": "e9c0743ef1b2311aac15b51e4208ff204ad7766581d1a440206bc2903d989461",
    },
    {
        "path": "audit/10-build.json",
        "size": 1234,
        "sha256": "2ea371296b5eedf28074a8fb966b1fe58a985629f966c89a348c8bc4ab00b4ab",
    },
    {
        "path": "audit/11-image-inspect.json",
        "size": 682,
        "sha256": "98e6a4b0f547c95ebd00d21caeec620283543906d839a24eabb67adc6945fffc",
    },
    {
        "path": "audit/20-cache-preflight.json",
        "size": 1900,
        "sha256": "9827ccd8ea4d9f3625e26db1caecda276ac1a452f0cb4dad409eed2d9eeb7236",
    },
    {
        "path": "audit/30-environment.json",
        "size": 1995,
        "sha256": "5523fce88357798387b5934baf32f311150f148ed95871f396539ab1682ef656",
    },
    {
        "path": "audit/31-model-assets.json",
        "size": 2051,
        "sha256": "9e9e0e88a94b217d26e96741dfc34db499b72f579460a1465a5a988f2cf7ba66",
    },
    {
        "path": "audit/32-model-contract.json",
        "size": 1910,
        "sha256": "4f2e6992aa40d9df1a0322565a6bdc2484f45fe6163eb5203e8efe911d3a85f8",
    },
    {
        "path": "audit/32-model-contract.stderr.log",
        "size": 1362,
        "sha256": "05a5801f0f54bdc7d8a5d6494f46b5b5d08df990d6137fdae012f753d96d79ce",
    },
    {
        "path": "audit/32-model-contract.stdout.log",
        "size": 5,
        "sha256": "c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431",
    },
    {
        "path": "audit/78-failure-diagnostic.json",
        "size": 853,
        "sha256": "f50f883e74594752d9c4e6e4b857814c9072f0bfc0d75d0dcd229d2081b12676",
    },
    {
        "path": "audit/79-historical-preservation-final.json",
        "size": 301,
        "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d",
    },
    {
        "path": "audit/80-campaign-result.json",
        "size": 764,
        "sha256": "1787120f4635a02ba14e6b08d390b896ca03e855efc22cdf710983bf94dd8bab",
    },
    {
        "path": "audit/81-campaign-file-manifest.json",
        "size": 16740,
        "sha256": "ab28d20479a0b44a82bcb9c555f867c0c879a2da0cc0c117d2c4c8667749adf3",
    },
    {
        "path": "audit/82-campaign-closure.json",
        "size": 660,
        "sha256": "75267ce8cc36bc25a6c7e985c4b836038241706477656211fe1328dd102bf76a",
    },
    {
        "path": "wave0/receipts/model-contract.json",
        "size": 9623,
        "sha256": "307c95414578af6c6a90dc742fe359a5b985d2d6bd2e76e9228caf1475de4eaa",
    },
]


def _registered_paths(artifact_root: str, run_ids: list[str]) -> list[str]:
    root = Path(artifact_root)
    values: list[str] = []
    for run_id in run_ids:
        campaign = root / "a11-runs" / run_id
        values.extend(
            [
                str(campaign),
                str(campaign / "wave0" / "model_cache"),
                str(campaign / "audit" / "active-lease.json"),
                str(root / "leases" / f"{run_id}.released"),
                str(root / "leases" / f"{run_id}.release.json"),
                str(campaign / "audit"),
                str(campaign / "wave0" / "receipts"),
                str(campaign / "wave0" / "checkpoints"),
            ]
        )
    return [str(Path(value)) for value in values]


def _prior_attempts() -> dict[str, object]:
    artifact_root = "D:/vision-active-learning-loop-artifacts/wave0"
    failed_run_ids = [_FAILED_RUN_ID, _FAILED_VALIDATION_ID]
    timeout_run_ids = [_TIMEOUT_RUN_ID, _TIMEOUT_VALIDATION_ID]
    stream_run_ids = [_STREAM_RUN_ID, _STREAM_VALIDATION_ID]
    aggregate_run_ids = [_AGGREGATE_RUN_ID, _AGGREGATE_VALIDATION_ID]
    return {
        "run_names": [
            _FAILED_RUN_ID,
            _TIMEOUT_RUN_ID,
            _STREAM_RUN_ID,
            _AGGREGATE_RUN_ID,
        ],
        "image_tags": [
            _FAILED_IMAGE_TAG,
            _AGGREGATE_IMAGE_TAG,
            _STREAM_IMAGE_TAG,
        ],
        "lease_names": [
            f"{_FAILED_RUN_ID}.release.json",
            f"{_FAILED_RUN_ID}.released",
            f"{_STREAM_RUN_ID}.release.json",
            f"{_STREAM_RUN_ID}.released",
            f"{_AGGREGATE_RUN_ID}.release.json",
            f"{_AGGREGATE_RUN_ID}.released",
        ],
        "authorization_evidence": [
            {
                "run_id": _FAILED_RUN_ID,
                "path": "audit/00-identity.json",
                "owner_authorization_id": _FAILED_OWNER,
            },
            {
                "run_id": _TIMEOUT_RUN_ID,
                "path": "audit/00-identity.json",
                "owner_authorization_id": _TIMEOUT_OWNER,
            },
            {
                "run_id": _STREAM_RUN_ID,
                "path": "audit/00-identity.json",
                "owner_authorization_id": _STREAM_OWNER,
            },
            {
                "run_id": _AGGREGATE_RUN_ID,
                "path": "audit/00-identity.json",
                "owner_authorization_id": _AGGREGATE_OWNER,
            },
        ],
        "attempts": [
            {
                "state": "launcher-stage-failure",
                "run_id": _FAILED_RUN_ID,
                "source_commit": "2622e402e4f536b94326ac34f9b20c90b513002b",
                "registered_run_ids": failed_run_ids,
                "registered_image_tags": [_FAILED_IMAGE_TAG, _FAILED_VALIDATION_TAG],
                "registered_paths": _registered_paths(artifact_root, failed_run_ids),
                "owner_authorization_id": _FAILED_OWNER,
                "run_file_count": 48,
                "run_inventory_sha256": _FAILED_RUN_SHA256,
                "historical_preservation_sha256": (
                    "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"
                ),
                "released_lease_sha256": (
                    "146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322"
                ),
                "release_record_sha256": (
                    "35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060"
                ),
                "closure_paths_present": [],
                "image_tag": _FAILED_IMAGE_TAG,
                "image_id": _FAILED_IMAGE_ID,
                "links_absent": True,
            },
            {
                "state": "image-build-timeout",
                "run_id": _TIMEOUT_RUN_ID,
                "source_commit": "1445a90b799b6306d6c1f7abc94b4a201afe5dc6",
                "registered_run_ids": timeout_run_ids,
                "registered_image_tags": [_TIMEOUT_IMAGE_TAG, _TIMEOUT_VALIDATION_TAG],
                "registered_paths": _registered_paths(artifact_root, timeout_run_ids),
                "owner_authorization_id": _TIMEOUT_OWNER,
                "run_file_count": 5,
                "run_inventory_sha256": _TIMEOUT_RUN_SHA256,
                "file_records": _TIMEOUT_FILES,
                "directory_names": [
                    "audit",
                    "wave0",
                    "wave0/checkpoints",
                    "wave0/model_cache",
                    "wave0/receipts",
                ],
                "image_tags_present": [],
                "lease_paths_present": [],
                "validation_present": False,
                "payload_file_paths_present": [],
                "closure_paths_present": [],
                "latest_write_utc": "2026-08-28T12:17:12.8122776Z",
                "links_absent": True,
            },
            {
                "state": "foundation-stream-contract-failure",
                "run_id": _STREAM_RUN_ID,
                "source_commit": _STREAM_SOURCE,
                "specification_commit": _SPEC,
                "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
                "registered_run_ids": stream_run_ids,
                "registered_image_tags": [
                    _STREAM_IMAGE_TAG,
                    _STREAM_VALIDATION_TAG,
                ],
                "registered_paths": _registered_paths(artifact_root, stream_run_ids),
                "owner_authorization_id": _STREAM_OWNER,
                "run_file_count": 60,
                "run_inventory_sha256": _STREAM_RUN_SHA256,
                "directory_names": _STREAM_DIRECTORIES,
                "key_file_records": _STREAM_KEY_FILES,
                "image_tag": _STREAM_IMAGE_TAG,
                "image_id": _STREAM_IMAGE_ID,
                "release_record_sha256": _STREAM_RELEASE_SHA256,
                "released_lease_sha256": _STREAM_RELEASED_SHA256,
                "validation_present": False,
                "replica_directory_names_present": [],
                "checkpoint_file_paths_present": [],
                "closure_paths_present": [
                    "78-failure-diagnostic.json",
                    "79-historical-preservation-final.json",
                    "80-campaign-result.json",
                    "81-campaign-file-manifest.json",
                    "82-campaign-closure.json",
                ],
                "latest_write_utc": "2026-08-28T18:10:34.6753199Z",
                "links_absent": True,
            },
            {
                "state": "aggregate-cache-inventory-contract-failure",
                "run_id": _AGGREGATE_RUN_ID,
                "source_commit": _AGGREGATE_SOURCE,
                "specification_commit": _SPEC,
                "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
                "registered_run_ids": aggregate_run_ids,
                "registered_image_tags": [
                    _AGGREGATE_IMAGE_TAG,
                    _AGGREGATE_VALIDATION_TAG,
                ],
                "registered_paths": _registered_paths(artifact_root, aggregate_run_ids),
                "owner_authorization_id": _AGGREGATE_OWNER,
                "run_file_count": 137,
                "run_inventory_sha256": _AGGREGATE_RUN_SHA256,
                "directory_names": _AGGREGATE_DIRECTORIES,
                "key_file_records": _AGGREGATE_KEY_FILES,
                "image_tag": _AGGREGATE_IMAGE_TAG,
                "image_id": _AGGREGATE_IMAGE_ID,
                "release_record_sha256": _AGGREGATE_RELEASE_SHA256,
                "released_lease_sha256": _AGGREGATE_RELEASED_SHA256,
                "validation_present": False,
                "replica_directory_names_present": _AGGREGATE_REPLICA_DIRECTORIES,
                "checkpoint_file_paths_present": _AGGREGATE_CHECKPOINT_FILES,
                "success_receipt_present": False,
                "closure_paths_present": [
                    "78-failure-diagnostic.json",
                    "79-historical-preservation-final.json",
                    "80-campaign-result.json",
                    "81-campaign-file-manifest.json",
                    "82-campaign-closure.json",
                ],
                "latest_write_utc": "2026-08-29T06:13:25.1659510Z",
                "links_absent": True,
            },
        ],
        "links_absent": True,
    }


def _ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _invoke_functions(
    names: tuple[str, ...], body: str, *, shell: str = "pwsh"
) -> subprocess.CompletedProcess[str]:
    if not _SCRIPT.is_file():
        raise AssertionError("production A11 launcher script is missing")
    requested = ",".join(_ps(name) for name in names)
    script = f"""
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {_ps(str(_SCRIPT))}, [ref]$Tokens, [ref]$Errors
)
if ($Errors.Count -ne 0) {{ throw ($Errors | ForEach-Object Message) -join '; ' }}
foreach ($FunctionName in @({requested})) {{
    $Matches = @($Ast.FindAll({{
        param($Node)
        $Node -is [Management.Automation.Language.FunctionDefinitionAst] -and
            $Node.Name -eq $FunctionName
    }}, $true))
    if ($Matches.Count -ne 1) {{ throw "function AST mismatch: $FunctionName" }}
    Invoke-Expression $Matches[0].Extent.Text
}}
{body}
"""
    return subprocess.run(
        [shell, "-NoProfile", "-NonInteractive", "-Command", script],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _file_record(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": path.resolve().as_posix(),
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _stage_receipt(
    run_id: str, *, status: str = "PASS", errors: list[str] | None = None
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "metadata": {"run_id": run_id},
        "normative": {
            "status": status,
            "errors": [] if errors is None else errors,
        },
    }


def _model_load_function_names(*names: str) -> tuple[str, ...]:
    source = _SCRIPT.read_text(encoding="utf-8")
    helper = "New-A11ModelLoadPresentationArguments"
    if f"function {helper}" in source:
        return (helper, *names)
    return names


def _run_foundation_stage(
    tmp_path: Path,
    *,
    name: str,
    stdout: str,
    expected_stdout: str,
    receipt_name: str,
    receipt: dict[str, object] | None,
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    receipt_path = receipts / receipt_name
    if receipt is not None:
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(campaign / 'wave0' / 'model_cache'))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{
        ExitCode=0; Stdout={_ps(stdout)}; Stderr={_ps(stderr)}
    }}
}}
Invoke-A11DockerStage -Identity $Identity -Name {_ps(name)} `
    -Command @('probe') -ExpectedStdout {_ps(expected_stdout)} `
    -ReceiptPath {_ps(str(receipt_path))} | ConvertTo-Json -Depth 8 -Compress
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Write-A11ProcessAudit",
            "Get-A11VerifiedStageReceipt",
            "Invoke-A11DockerStage",
        ),
        body,
    )


def _run_foundation_model_load_presentation(
    tmp_path: Path, *, residual_stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    cache = campaign / "wave0" / "model_cache"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    cache.mkdir(parents=True)
    for name in ("environment.json", "model-assets.json", "model-contract.json"):
        (receipts / name).write_text(
            json.dumps(_stage_receipt("wave0-a11-calibration-test")),
            encoding="utf-8",
        )
    presentation_stderr = (
        "`rLoading weights: 100%`n"
        "[transformers] RTDetrForObjectDetection LOAD REPORT`n"
    )
    body = f"""
$script:ObservedArguments = [Collections.Generic.List[object]]::new()
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(cache))}; run_id='wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64); audit_records=[ordered]@{{}}
    foundation_receipts=[ordered]@{{}}
}}
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $FlatArguments = @($ArgumentList)
    [void]$script:ObservedArguments.Add($FlatArguments)
    $IsEnvironment = $FlatArguments -ccontains 'environment'
    $IsModelContract = $FlatArguments -ccontains 'model-contract'
    $HasProgress = ($FlatArguments -join "`n").Contains(
        'HF_HUB_DISABLE_PROGRESS_BARS=1'
    )
    $HasVerbosity = ($FlatArguments -join "`n").Contains(
        'TRANSFORMERS_VERBOSITY=error'
    )
    $ObservedStderr = if ($IsModelContract) {{
        if (-not [string]::IsNullOrEmpty({_ps(residual_stderr)})) {{
            {_ps(residual_stderr)}
        }} elseif ($HasProgress -and $HasVerbosity) {{
            ''
        }} else {{
            "{presentation_stderr}"
        }}
    }} else {{
        ''
    }}
    $ObservedStdout = if ($IsEnvironment) {{ '' }} else {{ "PASS`n" }}
    return [pscustomobject]@{{
        ExitCode=0; Stdout=$ObservedStdout; Stderr=$ObservedStderr
    }}
}}
Invoke-A11Foundation -Identity $Identity
$script:ObservedArguments | ConvertTo-Json -Depth 8 -Compress
"""
    return _invoke_functions(
        _model_load_function_names(
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "Write-A11ProcessAudit",
            "Invoke-A11DockerStage",
            "Invoke-A11Foundation",
        ),
        body,
    )


def _run_untrusted_receipt_case(
    tmp_path: Path,
    *,
    defect: str,
    receipt: dict[str, object] | None,
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipt_root = campaign / "wave0" / "receipts"
    outside = tmp_path / "outside"
    audit.mkdir(parents=True)
    receipt_root.mkdir(parents=True)
    outside.mkdir()
    junction_setup = ""
    if defect == "outside":
        receipt_path = outside / "environment.json"
        write_path = receipt_path
    elif defect == "junction":
        target = outside / "linked"
        target.mkdir()
        receipt_path = campaign / "wave0" / "linked" / "environment.json"
        write_path = target / "environment.json"
        junction_setup = (
            f"New-Item -ItemType Junction -Path {_ps(str(receipt_path.parent))} "
            f"-Target {_ps(str(target))} | Out-Null"
        )
    else:
        receipt_path = receipt_root / "environment.json"
        write_path = receipt_path
    if receipt is not None:
        write_path.write_text(json.dumps(receipt), encoding="utf-8")
    body = f"""
{junction_setup}
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(campaign / 'wave0' / 'model_cache'))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
}}
Invoke-A11DockerStage -Identity $Identity -Name '30-environment' `
    -Command @('environment','check') -ExpectedStdout '' `
    -ReceiptPath {_ps(str(receipt_path))} | Out-Null
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Write-A11ProcessAudit",
            "Get-A11VerifiedStageReceipt",
            "Invoke-A11DockerStage",
        ),
        body,
    )


def _run_cache_stream_contract(
    tmp_path: Path, stdout: str
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    cache = campaign / "wave0" / "model_cache"
    audit.mkdir(parents=True)
    cache.mkdir(parents=True)
    (cache / "config.json").write_text("cache", encoding="utf-8")
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(cache))}; run_id='wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64); audit_records=[ordered]@{{}}
    cache_inventory_sha256=$null
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{ ExitCode=0; Stdout={_ps(stdout)}; Stderr='' }}
}}
Invoke-A11CachePreflight -Identity $Identity -Worktree 'D:/repo' |
    ConvertTo-Json -Depth 8 -Compress
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11JsonSha256",
            "New-A11CachePreflightArguments",
            "Get-A11CacheInventorySha256",
            "Invoke-A11CachePreflight",
        ),
        body,
    )


def _run_replica_stream_contract(
    tmp_path: Path,
    stdout: str,
    *,
    stderr: str = "",
    presentation_aware: bool = False,
    emit_arguments: bool = False,
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    cache = campaign / "wave0" / "model_cache"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    cache.mkdir(parents=True)
    model_contract = receipts / "model-contract.json"
    model_contract.write_text(
        json.dumps(_stage_receipt("wave0-a11-calibration-test")),
        encoding="utf-8",
    )
    model_record = _file_record(model_contract)
    replica_receipt = receipts / "calibration-00.json"
    checkpoint = campaign / "wave0" / "checkpoints" / "calibration-00" / "step.pt"
    cid = audit / "calibration-00.cid"
    presentation_stderr = (
        "`rLoading weights: 100%`n"
        "[transformers] RTDetrForObjectDetection LOAD REPORT`n"
    )
    stderr_logic = (
        f"""
    $FlatArguments = @($ArgumentList)
    $HasProgress = ($FlatArguments -join "`n").Contains(
        'HF_HUB_DISABLE_PROGRESS_BARS=1'
    )
    $HasVerbosity = ($FlatArguments -join "`n").Contains(
        'TRANSFORMERS_VERBOSITY=error'
    )
    $ObservedStderr = if ($HasProgress -and $HasVerbosity) {{
        {_ps(stderr)}
    }} else {{
        "{presentation_stderr}"
    }}
"""
        if presentation_aware
        else f"$ObservedStderr = {_ps(stderr)}"
    )
    output_arguments = (
        "$script:ObservedArguments | ConvertTo-Json -Compress" if emit_arguments else ""
    )
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(cache))}; run_id='wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64)
    replica_records=[Collections.Generic.List[object]]::new()
    foundation_receipts=[ordered]@{{
        model_contract=({_ps(json.dumps(model_record))} | ConvertFrom-Json)
    }}
}}
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $script:ObservedArguments = @($ArgumentList)
    {stderr_logic}
    [IO.Directory]::CreateDirectory({_ps(str(checkpoint.parent))}) | Out-Null
    [IO.File]::WriteAllText({_ps(str(checkpoint))}, 'checkpoint')
    [IO.File]::WriteAllText(
        {_ps(str(replica_receipt))},
        '{{"metadata":{{"timestamp":"2026-08-28T00:00:00Z"}}}}'
    )
    [IO.File]::WriteAllText({_ps(str(cid))}, ('a' * 64))
    return [pscustomobject]@{{
        ExitCode=0; Stdout={_ps(stdout)}; Stderr=$ObservedStderr
    }}
}}
Invoke-A11Replica -Identity $Identity -ReplicaId 'calibration-00'
{output_arguments}
"""
    return _invoke_functions(
        _model_load_function_names(
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "New-A11ReplicaValArguments",
            "New-A11ReplicaArguments",
            "Invoke-A11Replica",
        ),
        body,
    )


def _preflight() -> dict[str, object]:
    return {
        "worktree_path": "D:/repo/.worktrees/a11",
        "git_dir": "D:/repo/.git/worktrees/a11",
        "common_dir": "D:/repo/.git",
        "linked_worktree": True,
        "branch": _BRANCH,
        "head": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "plan_parent_is_spec": True,
        "linked_status": "",
        "canonical_status": "",
        "val_data_root_present": False,
        "docker_context": "desktop-linux",
        "docker_os": "linux",
        "docker_server_version": "29.6.1",
        "gpu_rows": [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 0,
            }
        ],
        "project_containers": [],
        "active_leases": [],
        "prior_a11_attempts": _prior_attempts(),
        "historical_file_count": 64306,
        "historical_image_count": 21,
        "historical_file_inventory_sha256": _HISTORICAL_FILES_SHA256,
        "historical_image_inventory_sha256": _HISTORICAL_IMAGES_SHA256,
        "historical_preserved": True,
    }


def _preflight_body(evidence: dict[str, object], *, owner: str = _OWNER) -> str:
    return f"""
$Result = Test-A11ReadOnlyPreflight `
    -EvidenceJson {_ps(json.dumps(evidence))} `
    -ExpectedSourceCommit {_ps(_SOURCE)} `
    -ExpectedSpecCommit {_ps(_SPEC)} `
    -ExpectedPlanCommit {_ps(_PLAN)} `
    -ExpectedBranch {_ps(_BRANCH)} `
    -OwnerAuthorizationId {_ps(owner)}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def _run_prior_attempt_inventory(
    tmp_path: Path, defect: str = ""
) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path, Path, Path]:
    extended_tmp = Path("\\\\?\\" + str(tmp_path.resolve()))
    artifact = extended_tmp / "artifacts"
    a11_root = artifact / "a11-runs"
    expected_run1 = a11_root / _FAILED_RUN_ID
    expected_run2 = a11_root / _TIMEOUT_RUN_ID
    expected_run3 = a11_root / _STREAM_RUN_ID
    expected_run4 = a11_root / _AGGREGATE_RUN_ID
    outside_run1 = extended_tmp / "outside-run1"
    outside_run2 = extended_tmp / "outside-run2"
    outside_run3 = extended_tmp / "outside-run3"
    outside_run4 = extended_tmp / "outside-run4"
    run1_root = outside_run1 if defect == "run1-link" else expected_run1
    run2_root = outside_run2 if defect == "run2-link" else expected_run2
    run3_root = outside_run3 if defect == "run3-link" else expected_run3
    run4_root = outside_run4 if defect == "run4-link" else expected_run4
    expected_leases = artifact / "leases"
    outside_leases = extended_tmp / "outside-leases"
    lease_root = outside_leases if defect == "lease-link" else expected_leases
    (run1_root / "audit").mkdir(parents=True)
    (run2_root / "audit").mkdir(parents=True)
    (run3_root / "audit").mkdir(parents=True)
    (run4_root / "audit").mkdir(parents=True)
    for relative in ("wave0/checkpoints", "wave0/model_cache", "wave0/receipts"):
        (run2_root / relative).mkdir(parents=True)
    for relative in _STREAM_DIRECTORIES:
        (run3_root / relative).mkdir(parents=True, exist_ok=True)
    for relative in _AGGREGATE_DIRECTORIES:
        (run4_root / relative).mkdir(parents=True, exist_ok=True)
    lease_root.mkdir(parents=True)
    lease_lock = artifact / "leases" / f"{_GPU}.json"

    def identity(
        current_id: str,
        current_tag: str,
        peer_id: str,
        peer_tag: str,
        source: str,
        owner: str,
    ) -> dict[str, object]:
        def record(run_id: str, image_tag: str, phase: str) -> dict[str, str]:
            campaign = a11_root / run_id
            return {
                "phase": phase,
                "run_id": run_id,
                "image_tag": image_tag,
                "campaign_root": str(campaign),
                "cache_root": str(campaign / "wave0" / "model_cache"),
                "lease_id": f"{run_id}-lease",
                "lease_lock_path": str(lease_lock),
                "lease_path": str(campaign / "audit" / "active-lease.json"),
                "source_commit": source,
                "specification_commit": _SPEC,
                "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
                "owner_authorization_id": owner,
            }

        return {
            "current": record(current_id, current_tag, "calibration"),
            "preregistered_peer": record(peer_id, peer_tag, "validation"),
        }

    (run1_root / "audit" / "00-identity.json").write_text(
        json.dumps(
            identity(
                _FAILED_RUN_ID,
                _FAILED_IMAGE_TAG,
                _FAILED_VALIDATION_ID,
                _FAILED_VALIDATION_TAG,
                "2622e402e4f536b94326ac34f9b20c90b513002b",
                _FAILED_OWNER,
            )
        ),
        encoding="utf-8",
    )
    (run1_root / "audit" / "79-historical-preservation-final.json").write_text(
        "history", encoding="utf-8"
    )
    (run1_root / "payload.bin").write_bytes(b"payload")
    timeout_identity = run2_root / "audit" / "00-identity.json"
    timeout_identity.write_text(
        json.dumps(
            identity(
                _TIMEOUT_RUN_ID,
                _TIMEOUT_IMAGE_TAG,
                _TIMEOUT_VALIDATION_ID,
                _TIMEOUT_VALIDATION_TAG,
                "1445a90b799b6306d6c1f7abc94b4a201afe5dc6",
                _TIMEOUT_OWNER,
            )
        ),
        encoding="utf-8",
    )
    for name, content in (
        ("01-gpu-preflight.json", "gpu"),
        ("10-build.json", "build"),
        ("10-build.stderr.log", "timeout"),
        ("10-build.stdout.log", ""),
    ):
        (run2_root / "audit" / name).write_text(content, encoding="utf-8")
    (run3_root / "audit" / "00-identity.json").write_text(
        json.dumps(
            identity(
                _STREAM_RUN_ID,
                _STREAM_IMAGE_TAG,
                _STREAM_VALIDATION_ID,
                _STREAM_VALIDATION_TAG,
                _STREAM_SOURCE,
                _STREAM_OWNER,
            )
        ),
        encoding="utf-8",
    )
    (run4_root / "audit" / "00-identity.json").write_text(
        json.dumps(
            identity(
                _AGGREGATE_RUN_ID,
                _AGGREGATE_IMAGE_TAG,
                _AGGREGATE_VALIDATION_ID,
                _AGGREGATE_VALIDATION_TAG,
                _AGGREGATE_SOURCE,
                _AGGREGATE_OWNER,
            )
        ),
        encoding="utf-8",
    )
    for record in _STREAM_KEY_FILES[1:]:
        path = run3_root / str(record["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(record["path"]), encoding="utf-8")
    filler_root = run3_root / _STREAM_DIRECTORIES[-2]
    for index in range(45):
        (filler_root / f"filler-{index:02d}.bin").write_bytes(
            f"filler-{index:02d}".encode()
        )
    for record in _AGGREGATE_KEY_FILES[1:]:
        path = run4_root / str(record["path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(str(record["path"]), encoding="utf-8")
    for relative in _AGGREGATE_CHECKPOINT_FILES:
        (run4_root / relative).write_bytes(relative.encode())
    for index in range(12):
        receipt = run4_root / "wave0" / "receipts" / f"calibration-{index:02d}.json"
        receipt.write_text(f"calibration-{index:02d}", encoding="utf-8")
    aggregate_filler_root = (
        run4_root / "wave0/model_cache/snapshots/facebook--dinov2-small/"
        "ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees"
    )
    for index in range(96):
        (aggregate_filler_root / f"filler-{index:02d}.bin").write_bytes(
            f"aggregate-filler-{index:02d}".encode()
        )
    (lease_root / f"{_FAILED_RUN_ID}.released").write_text("released", encoding="utf-8")
    (lease_root / f"{_FAILED_RUN_ID}.release.json").write_text(
        "release", encoding="utf-8"
    )
    (lease_root / f"{_STREAM_RUN_ID}.released").write_text(
        "stream-released", encoding="utf-8"
    )
    (lease_root / f"{_STREAM_RUN_ID}.release.json").write_text(
        "stream-release", encoding="utf-8"
    )
    (lease_root / f"{_AGGREGATE_RUN_ID}.released").write_text(
        "aggregate-released", encoding="utf-8"
    )
    (lease_root / f"{_AGGREGATE_RUN_ID}.release.json").write_text(
        "aggregate-release", encoding="utf-8"
    )
    junctions = []
    if defect == "run1-link":
        a11_root.mkdir(parents=True, exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_run1))} "
            f"-Target {_ps(str(outside_run1))} | Out-Null"
        )
    if defect == "run2-link":
        a11_root.mkdir(parents=True, exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_run2))} "
            f"-Target {_ps(str(outside_run2))} | Out-Null"
        )
    if defect == "run3-link":
        a11_root.mkdir(parents=True, exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_run3))} "
            f"-Target {_ps(str(outside_run3))} | Out-Null"
        )
    if defect == "run4-link":
        a11_root.mkdir(parents=True, exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_run4))} "
            f"-Target {_ps(str(outside_run4))} | Out-Null"
        )
    if defect == "lease-link":
        artifact.mkdir(exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_leases))} "
            f"-Target {_ps(str(outside_leases))} | Out-Null"
        )
    if defect == "extra-run":
        (a11_root / "wave0-a11-calibration-extra").mkdir()
    if defect == "timeout-payload":
        (run2_root / "wave0" / "receipts" / "payload.json").write_text(
            "payload", encoding="utf-8"
        )
    if defect == "timeout-validation":
        (a11_root / _TIMEOUT_VALIDATION_ID).mkdir()
    if defect == "timeout-release":
        (lease_root / f"{_TIMEOUT_RUN_ID}.released").write_text(
            "released", encoding="utf-8"
        )
    if defect == "stream-missing-closure":
        (run3_root / "audit" / "82-campaign-closure.json").unlink()
    if defect == "stream-extra-directory":
        (run3_root / "unexpected").mkdir()
    if defect == "stream-validation":
        (a11_root / _STREAM_VALIDATION_ID).mkdir()
    if defect == "stream-replica":
        (run3_root / "wave0" / "replica-00").mkdir()
    if defect == "stream-checkpoint":
        (run3_root / "wave0" / "checkpoints" / "unexpected.bin").write_bytes(b"x")
    if defect == "stream-release-missing":
        (lease_root / f"{_STREAM_RUN_ID}.released").unlink()
    if defect == "aggregate-missing-closure":
        (run4_root / "audit" / "82-campaign-closure.json").unlink()
    if defect == "aggregate-extra-directory":
        (run4_root / "unexpected").mkdir()
    if defect == "aggregate-validation":
        (a11_root / _AGGREGATE_VALIDATION_ID).mkdir()
    if defect == "aggregate-missing-replica":
        checkpoint = run4_root / _AGGREGATE_CHECKPOINT_FILES[-1]
        checkpoint.unlink()
        checkpoint.parent.rmdir()
    if defect == "aggregate-missing-checkpoint":
        (run4_root / _AGGREGATE_CHECKPOINT_FILES[-1]).unlink()
    if defect == "aggregate-extra-replica":
        (run4_root / "wave0/replica-99").mkdir()
    if defect == "aggregate-extra-checkpoint":
        (run4_root / "wave0/checkpoints/calibration-00/unexpected.bin").write_bytes(
            b"x"
        )
    if defect == "aggregate-success-receipt":
        (run4_root / "wave0/receipts/statistical-replay-calibration.json").write_text(
            "unexpected", encoding="utf-8"
        )
    if defect == "aggregate-release-missing":
        (lease_root / f"{_AGGREGATE_RUN_ID}.released").unlink()
    native = (
        "return [pscustomobject]@{ExitCode=125;Stdout='';Stderr='daemon unavailable'}"
        if defect == "docker-failure"
        else f"""
if ($ArgumentList[1] -ceq 'ls') {{
    return [pscustomobject]@{{
        ExitCode=0;Stdout={_ps(_FAILED_IMAGE_TAG + chr(10) + _AGGREGATE_IMAGE_TAG + chr(10) + _STREAM_IMAGE_TAG + chr(10) + (_TIMEOUT_IMAGE_TAG + chr(10) if defect == 'unexpected-image' else ''))};Stderr=''
    }}
}}
$RequestedTag = [string]$ArgumentList[-1]
$ImageId = if ($RequestedTag -ceq {_ps(_FAILED_IMAGE_TAG)}) {{
    {_ps(_FAILED_IMAGE_ID)}
}} elseif ($RequestedTag -ceq {_ps(_STREAM_IMAGE_TAG)}) {{
    {_ps(_STREAM_IMAGE_ID)}
}} elseif ($RequestedTag -ceq {_ps(_AGGREGATE_IMAGE_TAG)}) {{
    {_ps(_AGGREGATE_IMAGE_ID)}
}} else {{
    throw "unexpected image inspect tag: $RequestedTag"
}}
$Labels = if ($RequestedTag -cin @({_ps(_STREAM_IMAGE_TAG)}, {_ps(_AGGREGATE_IMAGE_TAG)})) {{
    $LabelSource = if ($RequestedTag -ceq {_ps(_STREAM_IMAGE_TAG)}) {{
        {_ps(_STREAM_SOURCE)}
    }} else {{
        {_ps('0' * 40 if defect == 'aggregate-image-label-drift' else _AGGREGATE_SOURCE)}
    }}
    $LabelRunId = if ($RequestedTag -ceq {_ps(_STREAM_IMAGE_TAG)}) {{
        {_ps(_STREAM_RUN_ID)}
    }} else {{
        {_ps(_AGGREGATE_RUN_ID)}
    }}
    [ordered]@{{
        'org.opencontainers.image.revision' = $LabelSource
        'org.opencontainers.image.val.run_id' = $LabelRunId
        'org.opencontainers.image.val.spec_commit' = {_ps(_SPEC)}
        'org.opencontainers.image.val.plan_commit' = '7dbd3a7576ea76beccfc64f748c4e495259ea89b'
        'org.opencontainers.image.base.digest' = {_ps(_BASE)}
    }}
}} else {{
    [ordered]@{{}}
}}
return [pscustomobject]@{{
    ExitCode=0
    Stdout=(@(@{{Id=$ImageId;Config=@{{Labels=$Labels}}}}) |
        ConvertTo-Json -Depth 6 -Compress)
    Stderr=''
}}
"""
    )
    body = f"""
{chr(10).join(junctions)}
function Invoke-A11Native {{ param($FilePath,$ArgumentList) {native} }}
Get-A11PriorAttemptInventory -ArtifactRoot {_ps(str(artifact))} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11JsonSha256",
            "Test-A11PathEntryPresent",
            "Get-A11RegisteredAttemptPaths",
            "Get-A11PriorAttemptInventory",
        ),
        body,
    )
    return completed, run1_root, run2_root, run3_root, run4_root, lease_root


def _run_project_container_inventory(
    *,
    failure: str = "",
    project_tag: bool = True,
    repo_tags_json: str | None = None,
    shell: str = "pwsh",
) -> subprocess.CompletedProcess[str]:
    container_id = "0123456789ab"
    image_id = "sha256:" + "a" * 64
    repo_tags = (
        ["vision-active-learning-loop:preserved"]
        if project_tag
        else ["unrelated:latest"]
    )
    tag_payload = json.dumps(repo_tags) if repo_tags_json is None else repo_tags_json
    body = f"""
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    if ($ArgumentList[0] -ceq 'ps') {{
        if ({_ps(failure)} -ceq 'list') {{
            return [pscustomobject]@{{ExitCode=125;Stdout='';Stderr='list failed'}}
        }}
        return [pscustomobject]@{{
            ExitCode=0;Stdout={_ps(f'{container_id}|display-image' + chr(10))};Stderr=''
        }}
    }}
    if ($ArgumentList[0] -ceq 'inspect') {{
        if ({_ps(failure)} -ceq 'inspect') {{
            return [pscustomobject]@{{ExitCode=1;Stdout='';Stderr='inspect failed'}}
        }}
        return [pscustomobject]@{{ExitCode=0;Stdout={_ps(image_id + chr(10))};Stderr=''}}
    }}
    if ({_ps(failure)} -ceq 'image-inspect') {{
        return [pscustomobject]@{{ExitCode=1;Stdout='';Stderr='image inspect failed'}}
    }}
    return [pscustomobject]@{{
        ExitCode=0;Stdout={_ps(tag_payload + chr(10))};Stderr=''
    }}
}}
$Inventory = @(Get-A11ProjectContainerInventory)
[ordered]@{{values=$Inventory}} | ConvertTo-Json -Compress
"""
    return _invoke_functions(("Get-A11ProjectContainerInventory",), body, shell=shell)


def _phase_destination_identities(tmp_path: Path) -> list[dict[str, str]]:
    lease_lock = tmp_path / "leases" / f"{_GPU}.json"
    return [
        {
            "phase": "calibration",
            "run_id": "wave0-a11-calibration-20260828T010101001Z-aaaaaaaa",
            "image_tag": "vision-active-learning-loop:wave0-a11-calibration-a",
            "campaign_root": str(tmp_path / "calibration"),
            "cache_root": str(tmp_path / "calibration" / "wave0" / "model_cache"),
            "lease_id": ("wave0-a11-calibration-lease-20260828T010101001Z-aaaaaaaa"),
            "lease_path": str(tmp_path / "calibration" / "audit" / "active-lease.json"),
            "lease_lock_path": str(lease_lock),
            "owner_authorization_id": _OWNER,
        },
        {
            "phase": "validation",
            "run_id": "wave0-a11-validation-20260828T010101002Z-bbbbbbbb",
            "image_tag": "vision-active-learning-loop:wave0-a11-validation-b",
            "campaign_root": str(tmp_path / "validation"),
            "cache_root": str(tmp_path / "validation" / "wave0" / "model_cache"),
            "lease_id": ("wave0-a11-validation-lease-20260828T010101002Z-bbbbbbbb"),
            "lease_path": str(tmp_path / "validation" / "audit" / "active-lease.json"),
            "lease_lock_path": str(lease_lock),
            "owner_authorization_id": _OWNER,
        },
    ]


def _run_phase_destination_gate(
    identities: list[dict[str, str]],
    *,
    exit_code: int = 0,
    stdout: str = "",
    stderr: str = "",
    setup: str = "",
    present_only: str | None = None,
    owner: str = _OWNER,
    capture_counts: bool = False,
) -> subprocess.CompletedProcess[str]:
    boundary = (
        ""
        if present_only is None
        else f"""
function Test-A11PathEntryPresent {{
    param($Path)
    return [IO.Path]::GetFullPath($Path) -ceq `
        [IO.Path]::GetFullPath({_ps(present_only)})
}}
"""
    )
    counters = (
        """
$script:PathChecks = 0
$script:DockerCalls = 0
function Test-A11PathEntryPresent {
    param($Path)
    $script:PathChecks++
    return $false
}
"""
        if capture_counts
        else ""
    )
    invoke = (
        """
$Failure = $null
try {
    Test-A11PhaseDestinationsAbsent `
        -Identities $Identities -PriorAttempts $PriorAttempts `
        -OwnerAuthorizationId $OwnerAuthorizationId | Out-Null
} catch { $Failure = $_.Exception.Message }
[ordered]@{
    path_checks=$script:PathChecks
    docker_calls=$script:DockerCalls
    failure=$Failure
} | ConvertTo-Json -Compress
if ($null -ne $Failure) { throw $Failure }
"""
        if capture_counts
        else """
Test-A11PhaseDestinationsAbsent `
    -Identities $Identities -PriorAttempts $PriorAttempts `
    -OwnerAuthorizationId $OwnerAuthorizationId | Out-Null
"""
    )
    docker_counter = "$script:DockerCalls++" if capture_counts else ""
    body = f"""
{setup}
{boundary}
{counters}
function Invoke-A11Native {{
    {docker_counter}
    return [pscustomobject]@{{
        ExitCode={exit_code}; Stdout={_ps(stdout)}; Stderr={_ps(stderr)}
    }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
$PriorAttempts = {_ps(json.dumps(_prior_attempts()["attempts"]))} | ConvertFrom-Json
$OwnerAuthorizationId = {_ps(owner)}
{invoke}
"""
    return _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )


def _run_initialize_phase(
    tmp_path: Path,
    *,
    parent_kind: str = "directory",
    child_exists: bool = False,
) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path]:
    artifact = tmp_path / "artifacts"
    parent = artifact / "a11-runs"
    target = tmp_path / "junction-target"
    junction_setup = ""
    if parent_kind == "directory":
        (parent / "prior").mkdir(parents=True)
        sentinel = parent / "prior" / "sentinel.bin"
    elif parent_kind == "file":
        artifact.mkdir(parents=True)
        sentinel = parent
    elif parent_kind == "junction":
        artifact.mkdir(parents=True)
        (target / "prior").mkdir(parents=True)
        sentinel = target / "prior" / "sentinel.bin"
        junction_setup = (
            f"New-Item -ItemType Junction -Path {_ps(str(parent))} "
            f"-Target {_ps(str(target))} | Out-Null"
        )
    else:
        raise AssertionError(f"unsupported parent kind: {parent_kind}")
    sentinel.write_bytes(b"immutable-prior")

    new_root = parent / "wave0-a11-calibration-20260828T010101001Z-aaaaaaaa"
    peer_root = parent / "wave0-a11-validation-20260828T010101002Z-bbbbbbbb"
    if child_exists:
        new_root.mkdir(parents=True)
        sentinel = new_root / "sentinel.bin"
        sentinel.write_bytes(b"immutable-child")
    body = f"""
{junction_setup}
function nvidia-smi {{
    $FlatArgs = @($args | ForEach-Object {{ $_ }})
    if (($FlatArgs -join ' ') -like '*--query-gpu=name uuid driver_version*') {{
        return 'NVIDIA GeForce RTX 4090, {_GPU}, 591.86'
    }}
    return ''
}}
$Identity = New-A11PhaseIdentity `
    -Phase calibration -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(artifact))} `
    -TimestampToken '20260828T010101001Z' -Nonce 'aaaaaaaa'
$Peer = New-A11PhaseIdentity `
    -Phase validation -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(artifact))} `
    -TimestampToken '20260828T010101002Z' -Nonce 'bbbbbbbb'
Initialize-A11Phase -Identity $Identity -Peer $Peer | Out-Null
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "ConvertTo-A11GpuRows",
            "New-A11PhaseIdentity",
            "Initialize-A11Phase",
        ),
        body,
    )
    return completed, new_root, peer_root, sentinel


def test_launcher_has_exact_parameters_and_required_functions() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")
    expected_parameters = (
        "ExpectedSourceCommit",
        "ExpectedSpecCommit",
        "ExpectedPlanCommit",
        "ExpectedBranch",
        "OwnerAuthorizationId",
    )
    parameter_section = source[source.index("param(") : source.index(")\n\n")]
    for name in expected_parameters:
        assert parameter_section.count(f"${name}") == 1
    for name in (
        "Resolve-A11Worktree",
        "Get-A11ActiveLeasePaths",
        "Get-A11ProjectContainerInventory",
        "Test-A11ReadOnlyPreflight",
        "Confirm-A11ProtectedGit",
        "New-A11PhaseIdentity",
        "Get-A11PriorAttemptInventory",
        "Get-A11RegisteredAttemptPaths",
        "Test-A11PathEntryPresent",
        "Test-A11PhaseDestinationsAbsent",
        "New-A11BuildArguments",
        "New-A11ModelLoadPresentationArguments",
        "Invoke-A11CachePreflight",
        "Get-A11VerifiedStageReceipt",
        "Assert-A11FileRecordUnchanged",
        "New-A11ReplicaValArguments",
        "New-A11Lease",
        "Invoke-A11Replica",
        "New-A11GateArguments",
        "Invoke-A11Gate",
        "Confirm-A11CalibrationReceipt",
        "Release-A11Lease",
        "Confirm-A11Release",
        "Close-A11Phase",
        "Test-A11CrossPhaseIdentity",
        "Get-A11SingleCampaignResult",
        "Invoke-A11Campaign",
    ):
        assert source.count(f"function {name}") == 1
    assert source.count("ConvertTo-A11GpuRows") == 3
    assert (
        source.count("--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory")
        == 2
    )
    assert source.count("'CUBLAS_WORKSPACE_CONFIG=:4096:8'") == 2
    assert "OwnerAuthorizationId =" not in source
    assert "gate wave1" not in source.lower()


def test_write_a11_new_text_is_true_no_clobber_and_preserves_empty_bytes(
    tmp_path: Path,
) -> None:
    output = tmp_path / "audit.log"
    body = f"""
Write-A11NewText -Path {_ps(str(output))} -Text ''
try {{
    Write-A11NewText -Path {_ps(str(output))} -Text 'replacement'
    throw 'second write unexpectedly succeeded'
}} catch [System.IO.IOException] {{}}
[IO.File]::ReadAllBytes({_ps(str(output))}).Length
"""
    completed = _invoke_functions(("Write-A11NewText",), body)

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "0"
    assert output.read_bytes() == b""


@pytest.mark.parametrize(
    ("name", "stdout", "receipt_name"),
    [
        ("30-environment", "", "environment.json"),
        ("31-model-assets", "PASS\n", "model-assets.json"),
        ("32-model-contract", "PASS\n", "model-contract.json"),
    ],
)
def test_foundation_stages_enforce_registered_stream_and_receipt_contracts(
    tmp_path: Path, name: str, stdout: str, receipt_name: str
) -> None:
    completed = _run_foundation_stage(
        tmp_path,
        name=name,
        stdout=stdout,
        expected_stdout=stdout,
        receipt_name=receipt_name,
        receipt=_stage_receipt("wave0-a11-calibration-test"),
    )

    assert completed.returncode == 0, completed.stderr
    receipt_path = tmp_path / "campaign" / "wave0" / "receipts" / receipt_name
    expected_record = _file_record(receipt_path)
    assert json.loads(completed.stdout) == expected_record
    audit_path = tmp_path / "campaign" / "audit" / f"{name}.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["receipt"] == expected_record


def _assert_model_load_presentation_arguments(arguments: list[str]) -> None:
    expected_pairs = [
        ("-e", "HF_HUB_DISABLE_PROGRESS_BARS=1"),
        ("-e", "TRANSFORMERS_VERBOSITY=error"),
    ]
    pair_indexes: list[int] = []
    for pair in expected_pairs:
        indexes = [
            index
            for index in range(len(arguments) - 1)
            if tuple(arguments[index : index + 2]) == pair
        ]
        assert len(indexes) == 1
        pair_indexes.append(indexes[0])
    image_index = next(
        index for index, value in enumerate(arguments) if value == "sha256:" + "a" * 64
    )
    assert pair_indexes == sorted(pair_indexes)
    assert pair_indexes[-1] < image_index


def test_model_load_presentation_is_scoped_to_foundation_model_contract(
    tmp_path: Path,
) -> None:
    completed = _run_foundation_model_load_presentation(tmp_path)

    assert completed.returncode == 0, completed.stderr
    calls = json.loads(completed.stdout)
    assert len(calls) == 3
    environment = next(call for call in calls if "environment" in call)
    assets = next(call for call in calls if "assets" in call)
    model_contract = next(call for call in calls if "model-contract" in call)
    for call in (environment, assets):
        assert "HF_HUB_DISABLE_PROGRESS_BARS=1" not in call
        assert "TRANSFORMERS_VERBOSITY=error" not in call
    _assert_model_load_presentation_arguments(model_contract)


def test_replica_model_load_presentation_is_exact_and_before_image(
    tmp_path: Path,
) -> None:
    completed = _run_replica_stream_contract(
        tmp_path,
        "PASS\n",
        presentation_aware=True,
        emit_arguments=True,
    )

    assert completed.returncode == 0, completed.stderr
    _assert_model_load_presentation_arguments(json.loads(completed.stdout))


@pytest.mark.parametrize("component", ["foundation_model_contract", "replica"])
def test_model_load_residual_stderr_remains_fatal(
    tmp_path: Path, component: str
) -> None:
    if component == "foundation_model_contract":
        completed = _run_foundation_model_load_presentation(
            tmp_path, residual_stderr="unexpected diagnostic"
        )
    else:
        completed = _run_replica_stream_contract(
            tmp_path,
            "PASS\n",
            stderr="unexpected diagnostic",
            presentation_aware=True,
        )

    assert completed.returncode != 0
    assert completed.stderr


def test_model_load_presentation_control_surface_is_closed() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")
    helper_name = "New-A11ModelLoadPresentationArguments"
    helper_start = source.index(f"function {helper_name}")
    helper_end = source.index("\nfunction ", helper_start + 1)
    helper = source[helper_start:helper_end]
    assert helper.count("HF_HUB_DISABLE_PROGRESS_BARS=1") == 1
    assert helper.count("TRANSFORMERS_VERBOSITY=error") == 1
    assert source.count(helper_name) == 3
    for forbidden in (
        "HF_HUB_VERBOSITY",
        "TRANSFORMERS_NO_ADVISORY_WARNINGS",
        "--env-file",
        "stderr allowlist",
    ):
        assert forbidden not in helper
    assert "$Result.Stderr -ceq ''" in source
    assert "-not [string]::IsNullOrEmpty($Result.Stderr)" in source


def test_process_audit_omits_receipt_when_no_receipt_is_bound(
    tmp_path: Path,
) -> None:
    audit = tmp_path / "audit"
    audit.mkdir()
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(tmp_path))}
}}
$Result = [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
Write-A11ProcessAudit -Identity $Identity -Name '10-build' `
    -Argv @('docker','build') -Result $Result | Out-Null
Get-Content -Raw -LiteralPath {_ps(str(audit / '10-build.json'))}
"""
    completed = _invoke_functions(
        ("Write-A11NewText", "Get-A11FileRecord", "Write-A11ProcessAudit"),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    document = json.loads(completed.stdout)
    assert "receipt" not in document


def test_environment_rejects_noncanonical_pass_stdout(tmp_path: Path) -> None:
    completed = _run_foundation_stage(
        tmp_path,
        name="30-environment",
        stdout="PASS\n",
        expected_stdout="",
        receipt_name="environment.json",
        receipt=_stage_receipt("wave0-a11-calibration-test"),
    )

    assert completed.returncode != 0
    assert "A11 stage failed: 30-environment" in completed.stderr


@pytest.mark.parametrize(
    "defect", ["missing", "junction", "outside", "wrong-run", "fail", "errors"]
)
def test_foundation_stage_rejects_untrusted_receipt(
    tmp_path: Path, defect: str
) -> None:
    receipt = {
        "missing": None,
        "wrong-run": _stage_receipt("wrong-run"),
        "fail": _stage_receipt("wave0-a11-calibration-test", status="FAIL"),
        "errors": _stage_receipt("wave0-a11-calibration-test", errors=["injected"]),
    }.get(defect, _stage_receipt("wave0-a11-calibration-test"))

    completed = _run_untrusted_receipt_case(tmp_path, defect=defect, receipt=receipt)

    assert completed.returncode != 0
    assert completed.stderr


def test_foundation_rehashes_environment_and_assets_before_model_contract(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    environment = receipts / "environment.json"
    assets = receipts / "model-assets.json"
    model_contract = receipts / "model-contract.json"
    for path in (environment, assets, model_contract):
        path.write_text(
            json.dumps(_stage_receipt("wave0-a11-calibration-test")),
            encoding="utf-8",
        )
    body = f"""
$script:Calls = 0
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(campaign / 'wave0' / 'model_cache'))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}; foundation_receipts=[ordered]@{{}}
}}
function Invoke-A11Native {{
    $script:Calls++
    if ($script:Calls -eq 2) {{
        [IO.File]::AppendAllText({_ps(str(environment))}, ' ')
    }}
    $Stdout = if ($script:Calls -eq 1) {{ '' }} else {{ "PASS`n" }}
    return [pscustomobject]@{{ ExitCode=0; Stdout=$Stdout; Stderr='' }}
}}
try {{
    Invoke-A11Foundation -Identity $Identity
    throw 'foundation unexpectedly succeeded'
}} catch {{
    [ordered]@{{ calls=$script:Calls; error=$_.Exception.Message }} |
        ConvertTo-Json -Compress
}}
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "Write-A11ProcessAudit",
            "Invoke-A11DockerStage",
            "Invoke-A11Foundation",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["calls"] == 2
    assert "changed" in result["error"]


def test_replica_rehashes_model_contract_before_native_launch(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    model_contract = receipts / "model-contract.json"
    original = _stage_receipt("wave0-a11-calibration-test")
    model_contract.write_text(json.dumps(original), encoding="utf-8")
    expected = _file_record(model_contract)
    model_contract.write_text(
        json.dumps({**original, "mutated": True}), encoding="utf-8"
    )
    body = f"""
$script:Calls = 0
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(campaign / 'wave0' / 'model_cache'))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    replica_records=[Collections.Generic.List[object]]::new()
    foundation_receipts=[ordered]@{{
        model_contract=({_ps(json.dumps(expected))} | ConvertFrom-Json)
    }}
}}
function Invoke-A11Native {{
    $script:Calls++
    return [pscustomobject]@{{ ExitCode=0; Stdout="PASS`n"; Stderr='' }}
}}
try {{
    Invoke-A11Replica -Identity $Identity -ReplicaId 'calibration-00'
    throw 'replica unexpectedly succeeded'
}} catch {{
    [ordered]@{{ calls=$script:Calls; error=$_.Exception.Message }} |
        ConvertTo-Json -Compress
}}
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "New-A11ReplicaValArguments",
            "New-A11ReplicaArguments",
            "Invoke-A11Replica",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "calls": 0,
        "error": f"A11 verified receipt changed before use: {model_contract}",
    }


def test_dependent_use_rejects_identical_receipt_through_new_junction(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    receipts = campaign / "wave0" / "receipts"
    outside = tmp_path / "outside"
    receipts.mkdir(parents=True)
    outside.mkdir()
    receipt = receipts / "model-contract.json"
    content = json.dumps(_stage_receipt("wave0-a11-calibration-test"))
    receipt.write_text(content, encoding="utf-8")
    expected = _file_record(receipt)
    receipt.unlink()
    receipts.rmdir()
    (outside / "model-contract.json").write_text(content, encoding="utf-8")
    body = f"""
New-Item -ItemType Junction -Path {_ps(str(receipts))} `
    -Target {_ps(str(outside))} | Out-Null
$Identity = [pscustomobject]@{{
    campaign_root={_ps(str(campaign))}; run_id='wave0-a11-calibration-test'
}}
$Expected = {_ps(json.dumps(expected))} | ConvertFrom-Json
try {{
    Assert-A11FileRecordUnchanged -Identity $Identity `
        -Expected $Expected -Path {_ps(str(receipt))} | Out-Null
    throw 'junction unexpectedly accepted'
}} catch {{
    $_.Exception.Message
}}
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    assert "link" in completed.stdout.lower()


@pytest.mark.parametrize("component", ["cache", "replica"])
@pytest.mark.parametrize(
    ("stdout", "accepted"),
    [
        ("PASS\n", True),
        ("", False),
        ("PASS", False),
        ("PASS\r\n", False),
        ("PASS\nextra\n", False),
    ],
)
def test_cache_preflight_and_replica_keep_exact_pass_stream_contracts(
    tmp_path: Path, component: str, stdout: str, accepted: bool
) -> None:
    run = (
        _run_cache_stream_contract
        if component == "cache"
        else _run_replica_stream_contract
    )
    completed = run(tmp_path, stdout)

    if accepted:
        assert completed.returncode == 0, completed.stderr
    else:
        assert completed.returncode != 0
        assert completed.stderr


def test_read_only_preflight_accepts_exact_four_attempt_evidence() -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(_preflight())
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["head"] == _SOURCE


def test_four_prior_attempts_keep_distinct_closed_state_schemas() -> None:
    attempts = _prior_attempts()["attempts"]
    assert [attempt["state"] for attempt in attempts] == [
        "launcher-stage-failure",
        "image-build-timeout",
        "foundation-stream-contract-failure",
        "aggregate-cache-inventory-contract-failure",
    ]
    assert set(attempts[0]) == {
        "state",
        "run_id",
        "source_commit",
        "registered_run_ids",
        "registered_image_tags",
        "registered_paths",
        "owner_authorization_id",
        "run_file_count",
        "run_inventory_sha256",
        "historical_preservation_sha256",
        "released_lease_sha256",
        "release_record_sha256",
        "closure_paths_present",
        "image_tag",
        "image_id",
        "links_absent",
    }
    assert set(attempts[1]) == {
        "state",
        "run_id",
        "source_commit",
        "registered_run_ids",
        "registered_image_tags",
        "registered_paths",
        "owner_authorization_id",
        "run_file_count",
        "run_inventory_sha256",
        "file_records",
        "directory_names",
        "image_tags_present",
        "lease_paths_present",
        "validation_present",
        "payload_file_paths_present",
        "closure_paths_present",
        "latest_write_utc",
        "links_absent",
    }
    assert set(attempts[2]) == {
        "state",
        "run_id",
        "source_commit",
        "specification_commit",
        "plan_commit",
        "registered_run_ids",
        "registered_image_tags",
        "registered_paths",
        "owner_authorization_id",
        "run_file_count",
        "run_inventory_sha256",
        "directory_names",
        "key_file_records",
        "image_tag",
        "image_id",
        "release_record_sha256",
        "released_lease_sha256",
        "validation_present",
        "replica_directory_names_present",
        "checkpoint_file_paths_present",
        "closure_paths_present",
        "latest_write_utc",
        "links_absent",
    }
    assert set(attempts[3]) == {
        "state",
        "run_id",
        "source_commit",
        "specification_commit",
        "plan_commit",
        "registered_run_ids",
        "registered_image_tags",
        "registered_paths",
        "owner_authorization_id",
        "run_file_count",
        "run_inventory_sha256",
        "directory_names",
        "key_file_records",
        "image_tag",
        "image_id",
        "release_record_sha256",
        "released_lease_sha256",
        "validation_present",
        "replica_directory_names_present",
        "checkpoint_file_paths_present",
        "success_receipt_present",
        "closure_paths_present",
        "latest_write_utc",
        "links_absent",
    }


@pytest.mark.parametrize(
    "owner", [_FAILED_OWNER, _TIMEOUT_OWNER, _STREAM_OWNER, _AGGREGATE_OWNER]
)
def test_read_only_preflight_rejects_each_consumed_authorization(owner: str) -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",),
        _preflight_body(_preflight(), owner=owner),
    )

    assert completed.returncode != 0
    assert "prior owner authorization" in completed.stderr


_PRIOR_MUTATIONS = [
    (("run_names",), []),
    (("image_tags",), []),
    (("lease_names",), []),
    (("authorization_evidence", 1, "owner_authorization_id"), _FAILED_OWNER),
    (("authorization_evidence", 2, "owner_authorization_id"), _TIMEOUT_OWNER),
    (("authorization_evidence", 3, "owner_authorization_id"), _STREAM_OWNER),
    (("links_absent",), False),
    (("attempts", 0, "state"), "image-build-timeout"),
    (("attempts", 0, "source_commit"), "0" * 40),
    (("attempts", 0, "registered_paths"), []),
    (("attempts", 0, "run_file_count"), 47),
    (("attempts", 0, "run_inventory_sha256"), "0" * 64),
    (("attempts", 0, "historical_preservation_sha256"), "0" * 64),
    (("attempts", 0, "released_lease_sha256"), "0" * 64),
    (("attempts", 0, "release_record_sha256"), "0" * 64),
    (("attempts", 0, "closure_paths_present"), ["80-campaign-result.json"]),
    (("attempts", 0, "image_id"), "sha256:" + "0" * 64),
    (("attempts", 1, "state"), "launcher-stage-failure"),
    (("attempts", 1, "source_commit"), "0" * 40),
    (("attempts", 1, "registered_paths"), []),
    (("attempts", 1, "owner_authorization_id"), _FAILED_OWNER),
    (("attempts", 1, "run_file_count"), 4),
    (("attempts", 1, "run_inventory_sha256"), "0" * 64),
    (("attempts", 1, "file_records", 3, "size"), 865209),
    (("attempts", 1, "file_records", 3, "sha256"), "0" * 64),
    (("attempts", 1, "directory_names"), ["audit"]),
    (("attempts", 1, "image_tags_present"), [_TIMEOUT_IMAGE_TAG]),
    (("attempts", 1, "lease_paths_present"), ["active-lease.json"]),
    (("attempts", 1, "validation_present"), True),
    (("attempts", 1, "payload_file_paths_present"), ["wave0/receipts/x.json"]),
    (("attempts", 1, "closure_paths_present"), ["78-failure-diagnostic.json"]),
    (("attempts", 1, "links_absent"), False),
    (("attempts", 2, "state"), "image-build-timeout"),
    (("attempts", 2, "run_id"), _STREAM_VALIDATION_ID),
    (("attempts", 2, "source_commit"), "0" * 40),
    (("attempts", 2, "specification_commit"), "0" * 40),
    (("attempts", 2, "plan_commit"), "0" * 40),
    (("attempts", 2, "registered_run_ids"), [_STREAM_RUN_ID]),
    (("attempts", 2, "registered_image_tags"), [_STREAM_IMAGE_TAG]),
    (("attempts", 2, "registered_paths"), []),
    (("attempts", 2, "owner_authorization_id"), _TIMEOUT_OWNER),
    (("attempts", 2, "run_file_count"), 59),
    (("attempts", 2, "run_inventory_sha256"), "0" * 64),
    (("attempts", 2, "directory_names"), ["audit"]),
    (("attempts", 2, "key_file_records", 8, "size"), 4),
    (("attempts", 2, "key_file_records", 8, "sha256"), "0" * 64),
    (("attempts", 2, "image_tag"), _STREAM_VALIDATION_TAG),
    (("attempts", 2, "image_id"), "sha256:" + "0" * 64),
    (("attempts", 2, "release_record_sha256"), "0" * 64),
    (("attempts", 2, "released_lease_sha256"), "0" * 64),
    (("attempts", 2, "validation_present"), True),
    (("attempts", 2, "replica_directory_names_present"), ["replica-00"]),
    (("attempts", 2, "checkpoint_file_paths_present"), ["unexpected.bin"]),
    (("attempts", 2, "closure_paths_present"), []),
    (("attempts", 2, "latest_write_utc"), "not-a-time"),
    (("attempts", 2, "links_absent"), False),
    (("attempts", 3, "state"), "foundation-stream-contract-failure"),
    (("attempts", 3, "run_id"), _AGGREGATE_VALIDATION_ID),
    (("attempts", 3, "source_commit"), "0" * 40),
    (("attempts", 3, "specification_commit"), "0" * 40),
    (("attempts", 3, "plan_commit"), "0" * 40),
    (("attempts", 3, "registered_run_ids"), [_AGGREGATE_RUN_ID]),
    (("attempts", 3, "registered_image_tags"), [_AGGREGATE_IMAGE_TAG]),
    (("attempts", 3, "registered_paths"), []),
    (("attempts", 3, "owner_authorization_id"), _STREAM_OWNER),
    (("attempts", 3, "run_file_count"), 136),
    (("attempts", 3, "run_inventory_sha256"), "0" * 64),
    (("attempts", 3, "directory_names"), ["audit"]),
    (("attempts", 3, "key_file_records", 10, "sha256"), "0" * 64),
    (("attempts", 3, "image_tag"), _AGGREGATE_VALIDATION_TAG),
    (("attempts", 3, "image_id"), "sha256:" + "0" * 64),
    (("attempts", 3, "release_record_sha256"), "0" * 64),
    (("attempts", 3, "released_lease_sha256"), "0" * 64),
    (("attempts", 3, "validation_present"), True),
    (("attempts", 3, "replica_directory_names_present"), []),
    (("attempts", 3, "checkpoint_file_paths_present"), []),
    (("attempts", 3, "success_receipt_present"), True),
    (("attempts", 3, "closure_paths_present"), []),
    (("attempts", 3, "latest_write_utc"), "not-a-time"),
    (("attempts", 3, "links_absent"), False),
]


@pytest.mark.parametrize(
    ("path", "value"),
    _PRIOR_MUTATIONS,
)
def test_read_only_preflight_rejects_prior_a11_drift(
    path: tuple[object, ...], value: object
) -> None:
    evidence = copy.deepcopy(_preflight())
    target: object = evidence["prior_a11_attempts"]
    for key in path[:-1]:
        target = target[key]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert "prior A11" in completed.stderr


@pytest.mark.parametrize(
    "mutation",
    [
        "swap-attempts",
        "third-run",
        "second-image",
        "third-lease",
        "move-timeout-owner",
        "move-stream-owner",
        "delete-timeout-record",
        "delete-stream-key-record",
        "substitute-attempt-record",
        "substitute-stream-record",
    ],
)
def test_read_only_preflight_rejects_prior_a11_structural_drift(
    mutation: str,
) -> None:
    evidence = copy.deepcopy(_preflight())
    prior = evidence["prior_a11_attempts"]
    if mutation == "swap-attempts":
        prior["attempts"].reverse()
    elif mutation == "third-run":
        prior["run_names"].append("wave0-a11-calibration-extra")
    elif mutation == "second-image":
        prior["image_tags"].append(_TIMEOUT_IMAGE_TAG)
    elif mutation == "third-lease":
        prior["lease_names"].append(f"{_TIMEOUT_RUN_ID}.released")
    elif mutation == "move-timeout-owner":
        prior["authorization_evidence"][0]["owner_authorization_id"] = _TIMEOUT_OWNER
        prior["authorization_evidence"][1]["owner_authorization_id"] = _FAILED_OWNER
    elif mutation == "move-stream-owner":
        prior["authorization_evidence"][1]["owner_authorization_id"] = _STREAM_OWNER
        prior["authorization_evidence"][2]["owner_authorization_id"] = _TIMEOUT_OWNER
    elif mutation == "delete-timeout-record":
        del prior["attempts"][1]["file_records"][2]
    elif mutation == "delete-stream-key-record":
        del prior["attempts"][2]["key_file_records"][8]
    elif mutation == "substitute-attempt-record":
        prior["attempts"][1] = copy.deepcopy(prior["attempts"][0])
    else:
        prior["attempts"][2] = copy.deepcopy(prior["attempts"][1])

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert "prior A11" in completed.stderr


def test_gpu_inventory_ignores_wddm_na_rows_but_counts_numeric_cuda() -> None:
    body = f"""
$Rows = ConvertTo-A11GpuRows `
    -GpuCsv 'NVIDIA GeForce RTX 4090, {_GPU}' `
    -ComputeCsv @'
{_GPU}, 1096, Desktop Window Manager, [N/A]
{_GPU}, 4321, python.exe, 2048
'@
$Rows | ConvertTo-Json -Depth 4 -Compress
"""
    completed = _invoke_functions(("ConvertTo-A11GpuRows",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "name": "NVIDIA GeForce RTX 4090",
        "uuid": _GPU,
        "compute_process_count": 1,
    }


def test_gpu_inventory_rejects_unknown_memory_state() -> None:
    body = f"""
ConvertTo-A11GpuRows `
    -GpuCsv 'NVIDIA GeForce RTX 4090, {_GPU}' `
    -ComputeCsv '{_GPU}, 1096, Desktop Window Manager, unknown'
"""
    completed = _invoke_functions(("ConvertTo-A11GpuRows",), body)

    assert completed.returncode != 0
    assert "memory state" in completed.stderr


def test_active_lease_inventory_excludes_release_evidence(tmp_path: Path) -> None:
    active = tmp_path / f"{_GPU}.json"
    release = tmp_path / f"{_GPU}.json.release.json"
    released = tmp_path / f"{_GPU}.json.released"
    for path in (active, release, released):
        path.write_text("{}", encoding="utf-8")
    body = f"""
Get-A11ActiveLeasePaths -LeaseRoot {_ps(str(tmp_path))} |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("Get-A11ActiveLeasePaths",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == active.resolve().as_posix()

    active.unlink()
    without_active = _invoke_functions(("Get-A11ActiveLeasePaths",), body)
    assert without_active.returncode == 0, without_active.stderr
    assert without_active.stdout.strip() == ""


def test_prior_attempt_inventory_returns_closed_sorted_evidence(
    tmp_path: Path,
) -> None:
    (
        completed,
        run1_root,
        run2_root,
        run3_root,
        run4_root,
        lease_root,
    ) = _run_prior_attempt_inventory(tmp_path)

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)
    records_by_root = []
    for root in (run1_root, run2_root, run3_root, run4_root):
        records = []
        for path in sorted(root.rglob("*")):
            if path.is_file():
                content = path.read_bytes()
                records.append(
                    {
                        "path": path.relative_to(root).as_posix(),
                        "size": len(content),
                        "sha256": hashlib.sha256(content).hexdigest(),
                    }
                )
        records_by_root.append(records)
    attempts = evidence["attempts"]
    assert set(evidence) == {
        "run_names",
        "image_tags",
        "lease_names",
        "authorization_evidence",
        "attempts",
        "links_absent",
    }
    assert evidence["run_names"] == [
        _FAILED_RUN_ID,
        _TIMEOUT_RUN_ID,
        _STREAM_RUN_ID,
        _AGGREGATE_RUN_ID,
    ]
    assert evidence["image_tags"] == [
        _FAILED_IMAGE_TAG,
        _AGGREGATE_IMAGE_TAG,
        _STREAM_IMAGE_TAG,
    ]
    assert evidence["lease_names"] == sorted(path.name for path in lease_root.iterdir())
    assert evidence["authorization_evidence"] == [
        {
            "run_id": _FAILED_RUN_ID,
            "path": "audit/00-identity.json",
            "owner_authorization_id": _FAILED_OWNER,
        },
        {
            "run_id": _TIMEOUT_RUN_ID,
            "path": "audit/00-identity.json",
            "owner_authorization_id": _TIMEOUT_OWNER,
        },
        {
            "run_id": _STREAM_RUN_ID,
            "path": "audit/00-identity.json",
            "owner_authorization_id": _STREAM_OWNER,
        },
        {
            "run_id": _AGGREGATE_RUN_ID,
            "path": "audit/00-identity.json",
            "owner_authorization_id": _AGGREGATE_OWNER,
        },
    ]
    assert [attempt["state"] for attempt in attempts] == [
        "launcher-stage-failure",
        "image-build-timeout",
        "foundation-stream-contract-failure",
        "aggregate-cache-inventory-contract-failure",
    ]
    for attempt, records in zip(attempts, records_by_root, strict=True):
        assert attempt["run_file_count"] == len(records)
        assert (
            attempt["run_inventory_sha256"]
            == hashlib.sha256(
                json.dumps(records, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
        )
    assert attempts[0]["registered_run_ids"] == [
        _FAILED_RUN_ID,
        _FAILED_VALIDATION_ID,
    ]
    assert attempts[0]["registered_image_tags"] == [
        _FAILED_IMAGE_TAG,
        _FAILED_VALIDATION_TAG,
    ]
    assert attempts[0]["registered_paths"] == _registered_paths(
        str(run1_root.parents[1]), [_FAILED_RUN_ID, _FAILED_VALIDATION_ID]
    )
    assert (
        attempts[0]["historical_preservation_sha256"]
        == hashlib.sha256(b"history").hexdigest()
    )
    assert (
        attempts[0]["released_lease_sha256"] == hashlib.sha256(b"released").hexdigest()
    )
    assert (
        attempts[0]["release_record_sha256"] == hashlib.sha256(b"release").hexdigest()
    )
    assert attempts[0]["closure_paths_present"] == []
    assert attempts[0]["image_tag"] == _FAILED_IMAGE_TAG
    assert attempts[0]["image_id"] == _FAILED_IMAGE_ID
    assert attempts[1]["registered_run_ids"] == [
        _TIMEOUT_RUN_ID,
        _TIMEOUT_VALIDATION_ID,
    ]
    assert attempts[1]["registered_image_tags"] == [
        _TIMEOUT_IMAGE_TAG,
        _TIMEOUT_VALIDATION_TAG,
    ]
    assert attempts[1]["registered_paths"] == _registered_paths(
        str(run2_root.parents[1]), [_TIMEOUT_RUN_ID, _TIMEOUT_VALIDATION_ID]
    )
    assert attempts[1]["file_records"] == records_by_root[1]
    assert attempts[1]["directory_names"] == [
        "audit",
        "wave0",
        "wave0/checkpoints",
        "wave0/model_cache",
        "wave0/receipts",
    ]
    assert attempts[1]["image_tags_present"] == []
    assert attempts[1]["lease_paths_present"] == []
    assert attempts[1]["validation_present"] is False
    assert attempts[1]["payload_file_paths_present"] == []
    assert attempts[1]["closure_paths_present"] == []
    assert (
        datetime.fromisoformat(attempts[1]["latest_write_utc"])
        .utcoffset()
        .total_seconds()
        == 0
    )
    assert attempts[2]["registered_run_ids"] == [
        _STREAM_RUN_ID,
        _STREAM_VALIDATION_ID,
    ]
    assert attempts[2]["registered_image_tags"] == [
        _STREAM_IMAGE_TAG,
        _STREAM_VALIDATION_TAG,
    ]
    assert attempts[2]["registered_paths"] == _registered_paths(
        str(run3_root.parents[1]), [_STREAM_RUN_ID, _STREAM_VALIDATION_ID]
    )
    stream_records = {record["path"]: record for record in records_by_root[2]}
    assert attempts[2]["key_file_records"] == [
        stream_records[record["path"]] for record in _STREAM_KEY_FILES
    ]
    assert attempts[2]["directory_names"] == _STREAM_DIRECTORIES
    assert attempts[2]["image_tag"] == _STREAM_IMAGE_TAG
    assert attempts[2]["image_id"] == _STREAM_IMAGE_ID
    assert (
        attempts[2]["release_record_sha256"]
        == hashlib.sha256(b"stream-release").hexdigest()
    )
    assert (
        attempts[2]["released_lease_sha256"]
        == hashlib.sha256(b"stream-released").hexdigest()
    )
    assert attempts[2]["validation_present"] is False
    assert attempts[2]["replica_directory_names_present"] == []
    assert attempts[2]["checkpoint_file_paths_present"] == []
    assert attempts[2]["closure_paths_present"] == [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ]
    assert (
        datetime.fromisoformat(attempts[2]["latest_write_utc"])
        .utcoffset()
        .total_seconds()
        == 0
    )
    assert attempts[3]["registered_run_ids"] == [
        _AGGREGATE_RUN_ID,
        _AGGREGATE_VALIDATION_ID,
    ]
    assert attempts[3]["registered_image_tags"] == [
        _AGGREGATE_IMAGE_TAG,
        _AGGREGATE_VALIDATION_TAG,
    ]
    assert attempts[3]["registered_paths"] == _registered_paths(
        str(run4_root.parents[1]), [_AGGREGATE_RUN_ID, _AGGREGATE_VALIDATION_ID]
    )
    aggregate_records = {record["path"]: record for record in records_by_root[3]}
    assert attempts[3]["key_file_records"] == [
        aggregate_records[record["path"]] for record in _AGGREGATE_KEY_FILES
    ]
    assert attempts[3]["directory_names"] == _AGGREGATE_DIRECTORIES
    assert attempts[3]["image_tag"] == _AGGREGATE_IMAGE_TAG
    assert attempts[3]["image_id"] == _AGGREGATE_IMAGE_ID
    assert (
        attempts[3]["release_record_sha256"]
        == hashlib.sha256(b"aggregate-release").hexdigest()
    )
    assert (
        attempts[3]["released_lease_sha256"]
        == hashlib.sha256(b"aggregate-released").hexdigest()
    )
    assert attempts[3]["validation_present"] is False
    assert (
        attempts[3]["replica_directory_names_present"] == _AGGREGATE_REPLICA_DIRECTORIES
    )
    assert attempts[3]["checkpoint_file_paths_present"] == _AGGREGATE_CHECKPOINT_FILES
    assert attempts[3]["success_receipt_present"] is False
    assert attempts[3]["closure_paths_present"] == [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ]
    assert (
        datetime.fromisoformat(attempts[3]["latest_write_utc"])
        .utcoffset()
        .total_seconds()
        == 0
    )
    assert evidence["links_absent"] is True


@pytest.mark.parametrize(
    "defect",
    [
        "run1-link",
        "run2-link",
        "run3-link",
        "run4-link",
        "lease-link",
        "extra-run",
        "timeout-payload",
        "timeout-validation",
        "timeout-release",
        "unexpected-image",
        "stream-missing-closure",
        "stream-extra-directory",
        "stream-validation",
        "stream-replica",
        "stream-checkpoint",
        "stream-release-missing",
        "aggregate-missing-closure",
        "aggregate-extra-directory",
        "aggregate-validation",
        "aggregate-missing-replica",
        "aggregate-missing-checkpoint",
        "aggregate-extra-replica",
        "aggregate-extra-checkpoint",
        "aggregate-image-label-drift",
        "aggregate-success-receipt",
        "aggregate-release-missing",
        "docker-failure",
    ],
)
def test_prior_attempt_inventory_rejects_links_or_docker_failure(
    tmp_path: Path, defect: str
) -> None:
    completed, _, _, _, _, _ = _run_prior_attempt_inventory(tmp_path, defect)

    assert completed.returncode != 0
    assert completed.stderr


def test_launcher_preflight_inventories_all_container_states() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")

    assert source.count("'ps', '--all', '--format', '{{.ID}}|{{.Image}}'") == 1
    assert "& docker ps" not in source


def test_project_container_inventory_detects_stopped_project_container() -> None:
    completed = _run_project_container_inventory()

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["values"] == ["0123456789ab|sha256:" + "a" * 64]


def test_project_container_inventory_ignores_unrelated_container() -> None:
    completed = _run_project_container_inventory(project_tag=False)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["values"] == []


@pytest.mark.parametrize("repo_tags_json", ["null", "[]"])
def test_project_container_inventory_accepts_exact_empty_tag_shapes(
    repo_tags_json: str,
) -> None:
    completed = _run_project_container_inventory(repo_tags_json=repo_tags_json)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["values"] == []


@pytest.mark.parametrize(
    "repo_tags_json",
    ["{}", '""', '"scalar"', "42", "[null]", '[""]', "[", "[{}]"],
)
def test_project_container_inventory_rejects_malformed_tag_shapes(
    repo_tags_json: str,
) -> None:
    completed = _run_project_container_inventory(repo_tags_json=repo_tags_json)

    assert completed.returncode != 0
    assert "container inventory failed" in completed.stderr


@pytest.mark.parametrize(
    ("repo_tags_json", "expected", "accepted"),
    [
        ("[]", [], True),
        (json.dumps(["unrelated:latest"]), [], True),
        (
            json.dumps(["vision-active-learning-loop:preserved"]),
            ["0123456789ab|sha256:" + "a" * 64],
            True,
        ),
        ("[null]", None, False),
    ],
)
def test_project_container_inventory_keeps_tag_shape_contract_on_windows_powershell(
    repo_tags_json: str, expected: list[str] | None, accepted: bool
) -> None:
    completed = _run_project_container_inventory(
        repo_tags_json=repo_tags_json, shell="powershell"
    )

    if accepted:
        assert completed.returncode == 0, completed.stderr
        assert json.loads(completed.stdout)["values"] == expected
    else:
        assert completed.returncode != 0
        assert "container inventory failed" in completed.stderr


@pytest.mark.parametrize("failure", ["list", "inspect", "image-inspect"])
def test_project_container_inventory_fails_closed_on_native_errors(
    failure: str,
) -> None:
    completed = _run_project_container_inventory(failure=failure)

    assert completed.returncode != 0
    assert "container inventory failed" in completed.stderr


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("linked_worktree", False),
        ("branch", "main"),
        ("head", "f" * 40),
        ("plan_parent_is_spec", False),
        ("linked_status", " M file"),
        ("canonical_status", "?? other"),
        ("val_data_root_present", True),
        ("docker_context", "default"),
        ("docker_os", "windows"),
        ("docker_server_version", ""),
        ("project_containers", ["running"]),
        ("active_leases", ["active.json"]),
        ("historical_file_count", 64305),
        ("historical_image_count", 20),
        ("historical_file_inventory_sha256", "0" * 64),
        ("historical_image_inventory_sha256", "0" * 64),
        ("historical_preserved", False),
    ],
)
def test_read_only_preflight_rejects_identity_contention_or_drift(
    field: str, value: object
) -> None:
    evidence = _preflight()
    evidence[field] = value

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert completed.stderr


@pytest.mark.parametrize(
    "gpu_rows",
    [
        [],
        [
            {
                "name": "NVIDIA GeForce RTX 3090",
                "uuid": _GPU,
                "compute_process_count": 0,
            }
        ],
        [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 1,
            }
        ],
        [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 0,
            },
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": "GPU-other",
                "compute_process_count": 0,
            },
        ],
    ],
)
def test_read_only_preflight_requires_one_idle_registered_rtx4090(
    gpu_rows: list[dict[str, object]],
) -> None:
    evidence = _preflight()
    evidence["gpu_rows"] = gpu_rows
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0


def test_phase_identities_are_preregistered_and_fully_distinct(tmp_path: Path) -> None:
    body = f"""
$Calibration = New-A11PhaseIdentity `
    -Phase calibration -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(tmp_path))} `
    -TimestampToken '20260828T010101001Z' -Nonce 'aaaaaaaa'
$Validation = New-A11PhaseIdentity `
    -Phase validation -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(tmp_path))} `
    -TimestampToken '20260828T010101002Z' -Nonce 'bbbbbbbb'
@{{ calibration = $Calibration; validation = $Validation }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("New-A11PhaseIdentity",), body)

    assert completed.returncode == 0, completed.stderr
    identities = json.loads(completed.stdout)
    calibration = identities["calibration"]
    validation = identities["validation"]
    for name in (
        "run_id",
        "image_tag",
        "campaign_root",
        "cache_root",
        "lease_id",
        "lease_path",
    ):
        assert calibration[name] != validation[name]
    assert calibration["lease_lock_path"] == validation["lease_lock_path"]
    assert calibration["cache_root"].endswith("wave0\\model_cache")
    assert calibration["source_commit"] == validation["source_commit"] == _SOURCE
    assert calibration["owner_authorization_id"] == _OWNER


def test_phase_destination_gate_accepts_two_fresh_identities(
    tmp_path: Path,
) -> None:
    completed = _run_phase_destination_gate(_phase_destination_identities(tmp_path))

    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize(
    ("phase_index", "field", "preserved_value"),
    [
        (0, "run_id", _FAILED_RUN_ID),
        (1, "run_id", _FAILED_VALIDATION_ID),
        (0, "run_id", _TIMEOUT_RUN_ID),
        (1, "run_id", _TIMEOUT_VALIDATION_ID),
        (0, "run_id", _STREAM_RUN_ID),
        (1, "run_id", _STREAM_VALIDATION_ID),
        (0, "run_id", _AGGREGATE_RUN_ID),
        (1, "run_id", _AGGREGATE_VALIDATION_ID),
        (0, "image_tag", _FAILED_IMAGE_TAG),
        (1, "image_tag", _TIMEOUT_VALIDATION_TAG),
        (0, "image_tag", _STREAM_IMAGE_TAG),
        (1, "image_tag", _STREAM_VALIDATION_TAG),
        (0, "image_tag", _AGGREGATE_IMAGE_TAG),
        (1, "image_tag", _AGGREGATE_VALIDATION_TAG),
    ],
)
def test_phase_destination_gate_rejects_any_preserved_runtime_identity(
    tmp_path: Path, phase_index: int, field: str, preserved_value: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    identities[phase_index][field] = preserved_value
    completed = _run_phase_destination_gate(identities, capture_counts=True)

    assert completed.returncode != 0
    assert "preserved" in completed.stderr
    counters = json.loads(completed.stdout)
    assert counters["path_checks"] == 0
    assert counters["docker_calls"] == 0


@pytest.mark.parametrize("attempt_index", [1, 2, 3])
@pytest.mark.parametrize("path_index", range(8))
def test_phase_destination_gate_rejects_each_preserved_path_even_when_absent(
    tmp_path: Path, path_index: int, attempt_index: int
) -> None:
    identities = _phase_destination_identities(tmp_path)
    attempt = _prior_attempts()["attempts"][attempt_index]
    preserved = attempt["registered_paths"][8:]
    target = Path(preserved[path_index])
    if path_index == 0:
        identities[1]["campaign_root"] = str(target)
    elif path_index == 1:
        identities[1]["cache_root"] = str(target)
    elif path_index == 2:
        identities[1]["lease_path"] = str(target)
    else:
        identities[1]["run_id"] = attempt["registered_run_ids"][1]
    completed = _run_phase_destination_gate(identities, capture_counts=True)

    assert completed.returncode != 0
    assert "preserved" in completed.stderr
    counters = json.loads(completed.stdout)
    assert counters["path_checks"] == 0
    assert counters["docker_calls"] == 0


@pytest.mark.parametrize(
    ("owner", "identity_owner"),
    [
        (_FAILED_OWNER, _FAILED_OWNER),
        (_TIMEOUT_OWNER, _TIMEOUT_OWNER),
        (_STREAM_OWNER, _STREAM_OWNER),
        (_AGGREGATE_OWNER, _AGGREGATE_OWNER),
        (_OWNER, "OWNER-A11-DIFFERENT"),
    ],
)
def test_phase_destination_gate_rejects_consumed_or_mismatched_owner(
    tmp_path: Path, owner: str, identity_owner: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    for identity in identities:
        identity["owner_authorization_id"] = identity_owner
    completed = _run_phase_destination_gate(
        identities, owner=owner, capture_counts=True
    )

    assert completed.returncode != 0
    assert "owner authorization" in completed.stderr
    counters = json.loads(completed.stdout)
    assert counters["path_checks"] == 0
    assert counters["docker_calls"] == 0


@pytest.mark.parametrize(
    "field",
    ["run_id", "image_tag", "campaign_root", "cache_root", "lease_id", "lease_path"],
)
def test_phase_destination_gate_rejects_cross_phase_identity_reuse(
    tmp_path: Path, field: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    identities[1][field] = identities[0][field]

    completed = _run_phase_destination_gate(identities)

    assert completed.returncode != 0
    assert field in completed.stderr


@pytest.mark.parametrize(
    "collision",
    [
        "calibration-root",
        "validation-root",
        "calibration-cache-root",
        "validation-lease-path",
        "lease-lock",
        "calibration-released",
        "validation-release-record",
    ],
)
def test_phase_destination_gate_rejects_exact_path_collision(
    tmp_path: Path, collision: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    paths = {
        "calibration-root": Path(identities[0]["campaign_root"]),
        "validation-root": Path(identities[1]["campaign_root"]),
        "calibration-cache-root": Path(identities[0]["cache_root"]),
        "validation-lease-path": Path(identities[1]["lease_path"]),
        "lease-lock": Path(identities[0]["lease_lock_path"]),
        "calibration-released": (
            Path(identities[0]["lease_lock_path"]).parent
            / f"{identities[0]['run_id']}.released"
        ),
        "validation-release-record": (
            Path(identities[1]["lease_lock_path"]).parent
            / f"{identities[1]['run_id']}.release.json"
        ),
    }
    path = paths[collision]
    target_specific = collision in {"calibration-cache-root", "validation-lease-path"}
    if not target_specific:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.mkdir() if collision.endswith("root") else path.write_text(
            "occupied", encoding="utf-8"
        )

    completed = _run_phase_destination_gate(
        identities, present_only=str(path) if target_specific else None
    )

    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr
    assert str(path) in completed.stderr


@pytest.mark.parametrize("reused_token", ["timestamp", "nonce"])
def test_phase_destination_gate_rejects_timestamp_or_nonce_reuse(
    tmp_path: Path, reused_token: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    if reused_token == "timestamp":
        identities[1]["run_id"] = "wave0-a11-validation-20260828T010101001Z-bbbbbbbb"
    else:
        identities[1]["run_id"] = "wave0-a11-validation-20260828T010101002Z-aaaaaaaa"

    completed = _run_phase_destination_gate(identities)

    assert completed.returncode != 0
    assert "timestamp or nonce is reused" in completed.stderr


def test_phase_destination_gate_queries_each_exact_phase_image_tag(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    body = f"""
$script:RequestedTags = [Collections.Generic.List[string]]::new()
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $Reference = @($ArgumentList | Where-Object {{ $_ -like 'reference=*' }})
    if ($Reference.Count -ne 1) {{ throw 'unexpected Docker image query' }}
    [void]$script:RequestedTags.Add($Reference[0].Substring(10))
    return [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
$PriorAttempts = {_ps(json.dumps(_prior_attempts()["attempts"]))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent `
    -Identities $Identities -PriorAttempts $PriorAttempts `
    -OwnerAuthorizationId {_ps(_OWNER)} | Out-Null
$script:RequestedTags | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [
        identities[0]["image_tag"],
        identities[1]["image_tag"],
    ]


def test_phase_destination_gate_rejects_validation_only_image_collision(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    validation_tag = identities[1]["image_tag"]
    body = f"""
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $Reference = @($ArgumentList | Where-Object {{ $_ -like 'reference=*' }})[0]
    $Tag = $Reference.Substring(10)
    $Stdout = if ($Tag -ceq {_ps(validation_tag)}) {{ "$Tag`n" }} else {{ '' }}
    return [pscustomobject]@{{ ExitCode=0; Stdout=$Stdout; Stderr='' }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
$PriorAttempts = {_ps(json.dumps(_prior_attempts()["attempts"]))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent `
    -Identities $Identities -PriorAttempts $PriorAttempts `
    -OwnerAuthorizationId {_ps(_OWNER)} | Out-Null
"""
    completed = _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )

    assert completed.returncode != 0
    assert validation_tag in completed.stderr


@pytest.mark.parametrize(
    ("exit_code", "stdout", "stderr", "accepted"),
    [
        (0, "requested-tag\n", "", False),
        (125, "", "daemon unavailable", False),
        (0, "", "warning", False),
        (0, "", "", True),
    ],
)
def test_phase_destination_gate_distinguishes_image_collision_from_docker_failure(
    tmp_path: Path,
    exit_code: int,
    stdout: str,
    stderr: str,
    accepted: bool,
) -> None:
    completed = _run_phase_destination_gate(
        _phase_destination_identities(tmp_path),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )

    assert (completed.returncode == 0) is accepted
    if not accepted:
        assert completed.stderr


@pytest.mark.parametrize("destination_kind", ["file", "directory"])
def test_phase_destination_gate_rejects_dangling_reparse_point(
    tmp_path: Path, destination_kind: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    if destination_kind == "file":
        destination = Path(identities[0]["lease_lock_path"])
        target = tmp_path / "file-target.bin"
        target.write_bytes(b"target")
        item_type = "SymbolicLink"
    else:
        destination = Path(identities[0]["campaign_root"])
        target = tmp_path / "directory-target"
        target.mkdir()
        item_type = "Junction"
    destination.parent.mkdir(parents=True, exist_ok=True)
    moved_target = target.with_name(f"{target.name}-moved")
    setup = f"""
New-Item -ItemType {item_type} -Path {_ps(str(destination))} `
    -Target {_ps(str(target))} | Out-Null
Move-Item -LiteralPath {_ps(str(target))} -Destination {_ps(str(moved_target))}
"""

    completed = _run_phase_destination_gate(identities, setup=setup)

    if destination_kind == "file" and (
        "Administrator privilege required" in completed.stderr
    ):
        pytest.skip("creating a Windows file symlink requires unavailable privilege")
    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr


def test_phase_destination_gate_does_not_trust_test_path_false_negative(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    destination = Path(identities[0]["lease_lock_path"])
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"occupied")
    setup = "function Test-Path { return $false }"

    completed = _run_phase_destination_gate(identities, setup=setup)

    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr


def test_initialize_calibration_accepts_existing_parent_and_preserves_prior(
    tmp_path: Path,
) -> None:
    completed, new_root, peer_root, sentinel = _run_initialize_phase(tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert sentinel.read_bytes() == b"immutable-prior"
    assert new_root.is_dir()
    assert sorted(path.name for path in new_root.iterdir()) == ["audit", "wave0"]
    assert not peer_root.exists()


@pytest.mark.parametrize("parent_kind", ["file", "junction"])
def test_initialize_rejects_linked_or_non_directory_campaign_parent(
    tmp_path: Path, parent_kind: str
) -> None:
    completed, _new_root, _peer_root, sentinel = _run_initialize_phase(
        tmp_path, parent_kind=parent_kind
    )

    assert completed.returncode != 0
    assert "campaign parent is not a non-link directory" in completed.stderr
    assert sentinel.read_bytes() == b"immutable-prior"


def test_initialize_keeps_exact_campaign_child_no_clobber(tmp_path: Path) -> None:
    completed, _new_root, peer_root, sentinel = _run_initialize_phase(
        tmp_path, child_exists=True
    )

    assert completed.returncode != 0
    assert sentinel.read_bytes() == b"immutable-child"
    assert not peer_root.exists()


def test_build_arguments_have_exact_independent_labels() -> None:
    body = f"""
$Identity = [pscustomobject]@{{
    run_id = 'wave0-a11-calibration-20260828T010101001Z-aaaaaaaa'
    image_tag = 'vision-active-learning-loop:wave0-a11-calibration-test'
    source_commit = {_ps(_SOURCE)}
    specification_commit = {_ps(_SPEC)}
    plan_commit = {_ps(_PLAN)}
}}
New-A11BuildArguments -Identity $Identity -BaseDigest {_ps(_BASE)} |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11BuildArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:6] == [
        "build",
        "--no-cache",
        "--progress",
        "plain",
        "--file",
        "docker/wave0.Dockerfile",
    ]
    labels = [
        arguments[index + 1]
        for index, value in enumerate(arguments)
        if value == "--label"
    ]
    assert len(labels) == 5
    assert all(" " not in label for label in labels)
    assert arguments[-3:] == [
        "--tag",
        "vision-active-learning-loop:wave0-a11-calibration-test",
        ".",
    ]


def test_wave0_dockerfile_has_exact_bounded_uv_timeouts() -> None:
    source = _DOCKERFILE.read_text(encoding="utf-8")
    timeout_lines = [
        line.strip() for line in source.splitlines() if "UV_HTTP_TIMEOUT" in line
    ]
    assert timeout_lines == [
        "RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev --no-install-project",
        "RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev",
    ]
    assert "ENV UV_HTTP_TIMEOUT" not in source
    assert "ARG UV_HTTP_TIMEOUT" not in source
    assert source.count("uv sync --frozen --no-dev") == 2
    lowered = source.lower()
    assert "--retry" not in lowered
    assert "--index-url" not in lowered
    assert "--extra-index-url" not in lowered


def test_cache_preflight_arguments_are_networked_cpu_only() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    cache_root = 'D:/a11/calibration/wave0/model_cache'; image_id = 'sha256:' + ('a' * 64)
    run_id = 'wave0-a11-calibration-test'
}
New-A11CachePreflightArguments -Identity $Identity -Worktree 'D:/repo' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11CachePreflightArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:3] == ["run", "--rm", "--network"]
    assert arguments[3] == "bridge"
    assert "--gpus" not in arguments
    assert "--download" in arguments
    assert "VAL_ARTIFACT_ROOT=/a11/calibration" in arguments
    assert "/a11/calibration/wave0/model_cache" in arguments


def test_cache_inventory_digest_matches_python_canonical_json(tmp_path: Path) -> None:
    cache = tmp_path / "model_cache"
    detector = cache / "snapshots" / "PekingU--rtdetr_r18vd" / "weights.bin"
    backbone = cache / "snapshots" / "facebook--dinov2-small" / "weights.bin"
    detector.parent.mkdir(parents=True)
    backbone.parent.mkdir(parents=True)
    metadata_parent = cache / "snapshot" / ".cache" / "huggingface" / "download"
    metadata_parent.mkdir(parents=True)
    detector.write_bytes(b"detector")
    backbone.write_bytes(b"backbone")
    (metadata_parent / "config.json.metadata").write_text(
        "a" * 40 + "\n" + "b" * 64 + "\n123.5\n", encoding="utf-8"
    )
    expected = "bfa3752e03d3df309b2fb38d7317739e4f996cddfdb27c6dc198e3beec072c5d"
    assert statistical_replay._model_cache_inventory_sha256(cache) == expected
    body = f"""
Get-A11CacheInventorySha256 -CacheRoot {_ps(str(cache))}
"""
    completed = _invoke_functions(("Get-A11CacheInventorySha256",), body)

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == expected

    (metadata_parent / "config.json.metadata").write_text(
        "a" * 40 + "\n" + "b" * 64 + "\n999.25\n", encoding="utf-8"
    )
    changed_timestamp = _invoke_functions(("Get-A11CacheInventorySha256",), body)
    assert changed_timestamp.returncode == 0, changed_timestamp.stderr
    assert changed_timestamp.stdout.strip() == expected


def test_cache_inventory_digest_uses_unicode_scalar_order_in_both_languages(
    tmp_path: Path,
) -> None:
    cache = tmp_path / "model_cache"
    cache.mkdir()
    (cache / "\ue000.bin").write_bytes(b"bmp")
    (cache / "\U00010000.bin").write_bytes(b"supplementary")
    expected = "f1f51de651cc5680c2662dbf1f86a9c8879ee6af36b85d3655e71e6bdc6d4542"

    assert statistical_replay._model_cache_inventory_sha256(cache) == expected
    completed = _invoke_functions(
        ("Get-A11CacheInventorySha256",),
        f"Get-A11CacheInventorySha256 -CacheRoot {_ps(str(cache))}",
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == expected


def test_cache_inventory_digest_normalizes_equivalent_root_spellings(
    tmp_path: Path,
) -> None:
    cache = tmp_path / "model_cache"
    cache.mkdir()
    (cache / "weights.bin").write_bytes(b"weights")
    expected = statistical_replay._model_cache_inventory_sha256(cache)
    body = f"""
@(
    Get-A11CacheInventorySha256 -CacheRoot {_ps(str(cache))}
    Get-A11CacheInventorySha256 -CacheRoot {_ps(str(cache) + chr(92))}
    Push-Location {_ps(str(cache.parent))}
    try {{ Get-A11CacheInventorySha256 -CacheRoot 'model_cache' }}
    finally {{ Pop-Location }}
) | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("Get-A11CacheInventorySha256",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [expected, expected, expected]


def test_replica_arguments_are_fresh_offline_gpu_processes() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    cache_root = 'D:/a11/calibration/wave0/model_cache'; image_id = 'sha256:' + ('a' * 64)
    run_id = 'wave0-a11-calibration-test'
}
New-A11ReplicaArguments -Identity $Identity -Worktree 'D:/repo' `
    -ReplicaId 'calibration-00' `
    -ModelContractPath 'D:/a11/calibration/wave0/receipts/model-contract.json' `
    -ReceiptPath 'D:/a11/calibration/wave0/receipts/calibration-00.json' `
    -CheckpointRoot 'D:/a11/calibration/wave0/checkpoints/calibration-00' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        _model_load_function_names(
            "New-A11ReplicaValArguments", "New-A11ReplicaArguments"
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:7] == [
        "run",
        "--rm",
        "--gpus",
        "all",
        "--network",
        "none",
        "--workdir",
    ]
    assert "HF_HUB_OFFLINE=1" in arguments
    assert "TRANSFORMERS_OFFLINE=1" in arguments
    assert (
        "D:/a11/calibration/wave0/model_cache:/a11/calibration/wave0/model_cache:ro"
        in arguments
    )
    assert "D:/a11/calibration:/a11/calibration:rw" in arguments
    assert "sha256:" + "a" * 64 in arguments
    assert arguments.count("training-feasibility") == 1
    assert arguments[arguments.index("--cidfile") + 1].endswith("calibration-00.cid")


def test_replica_val_arguments_are_the_exact_container_argv() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    run_id = 'wave0-a11-calibration-test'
}
New-A11ReplicaValArguments -Identity $Identity -ReplicaId 'calibration-00' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11ReplicaValArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments == [
        "probe",
        "training-feasibility",
        "--model-contract",
        "/a11/calibration/wave0/receipts/model-contract.json",
        "--checkpoint-root",
        "/a11/calibration/wave0/checkpoints/calibration-00",
        "--run-id",
        "wave0-a11-calibration-test",
        "--output",
        "/a11/calibration/wave0/receipts/calibration-00.json",
    ]


def test_validation_gate_mount_precedes_image_and_preserves_command_order() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'validation'; campaign_root = 'D:/a11/validation'
    image_id = 'sha256:' + ('b' * 64)
}
New-A11GateArguments -Identity $Identity -Worktree 'D:/repo' `
    -CalibrationRoot 'D:/a11/calibration' | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11GateArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    image_index = arguments.index("sha256:" + "b" * 64)
    assert arguments.index("D:/a11/calibration:/a11/calibration:ro") < image_index
    assert arguments[image_index + 1 : image_index + 4] == [
        "gate",
        "statistical-replay",
        "validate",
    ]
    assert arguments[arguments.index("--phase-root") + 1] == "/a11/validation"
    assert (
        arguments[arguments.index("--calibration-receipt") + 1]
        == "/a11/calibration/wave0/receipts/statistical-replay-calibration.json"
    )


def test_gpu_lease_is_atomic_and_release_is_run_scoped(tmp_path: Path) -> None:
    lease_root = tmp_path / "leases"
    lease_root.mkdir()
    lease_path = lease_root / f"{_GPU}.json"
    released_path = lease_root / "wave0-a11-calibration-test.released"
    release_record = lease_root / "wave0-a11-calibration-test.release.json"
    body = f"""
$Identity = [pscustomobject]@{{
    phase = 'calibration'; run_id = 'wave0-a11-calibration-test'
    source_commit = {_ps(_SOURCE)}; image_id = 'sha256:' + ('a' * 64)
    image_tag = 'vision-active-learning-loop:wave0-a11-calibration-test'
    campaign_root = 'D:/a11/calibration'; cache_root = 'D:/a11/calibration/cache'
    lease_id = 'wave0-a11-calibration-lease-test'
}}
$Lease = New-A11Lease -Identity $Identity -GpuUuid {_ps(_GPU)} `
    -LeasePath {_ps(str(lease_path))}
$Release = Release-A11Lease -Identity $Identity `
    -ActivePath {_ps(str(lease_path))} `
    -ReleasedPath {_ps(str(released_path))} `
    -RecordPath {_ps(str(release_record))}
@{{ lease = $Lease; release = $Release }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "New-A11Lease",
            "Release-A11Lease",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    assert not lease_path.exists()
    assert released_path.is_file()
    release = json.loads(release_record.read_text(encoding="utf-8"))
    assert release["original_lease_sha256"]
    assert release["run_id"] == "wave0-a11-calibration-test"


def _identity(phase: str) -> dict[str, object]:
    marker = "a" if phase == "calibration" else "b"
    return {
        "static": {
            "source": _SOURCE,
            "spec": _SPEC,
            "plan": _PLAN,
            "base": _BASE,
            "model": "model",
            "gpu": _GPU,
        },
        "runtime": {
            "run_id": f"wave0-a11-{phase}-{marker}",
            "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-{marker}",
            "image_id": "sha256:" + marker * 64,
            "campaign_root": f"D:/a11/{phase}",
            "cache_root": f"D:/a11/{phase}/cache",
            "lease_id": f"wave0-a11-{phase}-lease",
            "lease_path": f"D:/leases/{phase}.json",
            "container_ids": [marker * 64],
            "receipt_paths": [f"D:/a11/{phase}/receipt.json"],
            "receipt_hashes": [marker * 64],
            "checkpoint_paths": [f"D:/a11/{phase}/checkpoint.pt"],
            "checkpoint_hashes": [(marker.upper().lower()) * 64],
            "timestamps": [f"2026-08-28T0{1 if phase == 'calibration' else 2}:00:00Z"],
            "audit_paths": [f"D:/a11/{phase}/audit.json"],
        },
    }


def test_cross_phase_identity_accepts_equal_static_and_disjoint_runtime() -> None:
    body = f"""
$Calibration = {_ps(json.dumps(_identity('calibration')))} | ConvertFrom-Json
$Validation = {_ps(json.dumps(_identity('validation')))} | ConvertFrom-Json
Test-A11CrossPhaseIdentity -Calibration $Calibration -Validation $Validation |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Test-A11CrossPhaseIdentity",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_calibration_receipt_is_rehashed_and_identity_checked_before_validation(
    tmp_path: Path,
) -> None:
    receipt = tmp_path / "wave0" / "receipts" / "statistical-replay-calibration.json"
    receipt.parent.mkdir(parents=True)
    document = {
        "receipt_type": "statistical-replay-calibration",
        "schema_version": 1,
        "normative": {
            "phase": "calibration",
            "status": "RECORDED",
            "errors": [],
            "terminal": (
                "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / " "WAVE1_FORBIDDEN"
            ),
            "threshold_inventory_sha256": "a" * 64,
        },
        "metadata": {
            "run_id": "wave0-a11-calibration-test",
            "source_commit": _SOURCE,
            "specification_commit": _SPEC,
            "plan_commit": _PLAN,
            "image_tag": "vision-active-learning-loop:wave0-a11-calibration-test",
            "image_id": "sha256:" + "b" * 64,
            "owner_authorization_id": _OWNER,
        },
    }
    receipt.write_text(json.dumps(document), encoding="utf-8")
    receipt_size = receipt.stat().st_size
    receipt_sha256 = hashlib.sha256(receipt.read_bytes()).hexdigest()
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; run_id='wave0-a11-calibration-test'
    campaign_root={_ps(str(tmp_path))}; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag='vision-active-learning-loop:wave0-a11-calibration-test'
    image_id='sha256:' + ('b' * 64); owner_authorization_id={_ps(_OWNER)}
    aggregate_receipt=[pscustomobject]@{{
        path={_ps(receipt.resolve().as_posix())}; size={receipt_size}
        sha256={_ps(receipt_sha256)}
    }}
}}
Confirm-A11CalibrationReceipt -Identity $Identity `
    -OwnerAuthorizationId {_ps(_OWNER)} | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        ("Get-A11FileRecord", "Confirm-A11CalibrationReceipt"), body
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) is True

    receipt.write_text(json.dumps({**document, "tampered": True}), encoding="utf-8")
    tampered = _invoke_functions(
        ("Get-A11FileRecord", "Confirm-A11CalibrationReceipt"), body
    )
    assert tampered.returncode != 0
    assert "changed" in tampered.stderr


def _run_close_a11_phase(
    tmp_path: Path,
    *,
    terminal: str,
    failure: str,
    aggregate_errors: list[str],
) -> tuple[subprocess.CompletedProcess[str], Path]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    audit.mkdir(parents=True)
    if aggregate_errors:
        receipt = (
            campaign / "wave0" / "receipts" / "statistical-replay-calibration.json"
        )
        receipt.parent.mkdir(parents=True)
        receipt.write_text(
            json.dumps({"normative": {"errors": aggregate_errors}}),
            encoding="utf-8",
        )
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; run_id='wave0-a11-calibration-test'
    campaign_root={_ps(str(campaign))}; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag='vision-active-learning-loop:wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64); owner_authorization_id={_ps(_OWNER)}
    lease_acquired=$false; current_stage='foundation'; terminal=$null
}}
function Get-A11HistoricalArtifactInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(64306)
        sha256={_ps(_HISTORICAL_FILES_SHA256)}
    }}
}}
function Get-A11HistoricalImageInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(21)
        sha256={_ps(_HISTORICAL_IMAGES_SHA256)}
    }}
}}
$script:Writes = [Collections.Generic.List[string]]::new()
$script:ProductionWrite = (Get-Command Write-A11NewText).ScriptBlock
function Write-A11NewText {{
    param([string]$Path, [AllowEmptyString()][string]$Text)
    [void]$script:Writes.Add([IO.Path]::GetFileName($Path))
    & $script:ProductionWrite -Path $Path -Text $Text
}}
$Closure = Close-A11Phase -Identity $Identity `
    -Terminal {_ps(terminal)} `
    -Failure {_ps(failure)}
[ordered]@{{ writes=$script:Writes; closure=$Closure }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        ("Write-A11NewText", "Get-A11FileRecord", "Close-A11Phase"), body
    )
    return completed, audit


@pytest.mark.parametrize(
    ("terminal", "failure", "aggregate_errors", "expected"),
    [
        (
            "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN",
            "",
            [],
            [],
        ),
        (
            "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN",
            "injected:build",
            [],
            ["injected:build"],
        ),
        (
            "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN",
            "",
            ["first", "second"],
            ["first", "second"],
        ),
    ],
)
def test_close_a11_phase_keeps_typed_error_cardinality_under_strictmode(
    tmp_path: Path,
    terminal: str,
    failure: str,
    aggregate_errors: list[str],
    expected: list[str],
) -> None:
    completed, audit = _run_close_a11_phase(
        tmp_path,
        terminal=terminal,
        failure=failure,
        aggregate_errors=aggregate_errors,
    )

    assert completed.returncode == 0, completed.stderr
    diagnostic = audit / "78-failure-diagnostic.json"
    if expected:
        assert json.loads(diagnostic.read_text(encoding="utf-8"))["errors"] == expected
    else:
        assert not diagnostic.exists()
        result = json.loads(
            (audit / "80-campaign-result.json").read_text(encoding="utf-8")
        )
        assert result["failure"] == ""


def test_close_a11_phase_publishes_complete_bound_failure_chain(
    tmp_path: Path,
) -> None:
    completed, audit = _run_close_a11_phase(
        tmp_path,
        terminal="WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN",
        failure="injected:foundation",
        aggregate_errors=[],
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    names = [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ]
    assert output["writes"] == names
    assert sorted(path.name for path in audit.glob("*.json")) == names
    diagnostic = json.loads((audit / names[0]).read_text(encoding="utf-8"))
    result = json.loads((audit / names[2]).read_text(encoding="utf-8"))
    manifest = json.loads((audit / names[3]).read_text(encoding="utf-8"))
    closure = json.loads((audit / names[4]).read_text(encoding="utf-8"))
    assert diagnostic["failed_stage"] == "foundation"
    assert diagnostic["errors"] == ["injected:foundation"]
    assert result["failure_diagnostic"] == _file_record(audit / names[0])
    assert result["historical_preservation"] == _file_record(audit / names[1])
    assert closure == output["closure"]
    assert closure["result"] == _file_record(audit / names[2])
    assert closure["manifest"] == _file_record(audit / names[3])
    manifest_paths = {record["path"] for record in manifest["files"]}
    expected_manifest_paths = {
        (audit / name).resolve().as_posix() for name in names[:3]
    }
    assert manifest_paths == expected_manifest_paths
    for record in manifest["files"]:
        assert record == _file_record(Path(record["path"]))


@pytest.mark.parametrize(
    "reuse", ["static", "run_id", "container_ids", "receipt_hashes"]
)
def test_cross_phase_identity_rejects_static_drift_or_runtime_reuse(reuse: str) -> None:
    calibration = _identity("calibration")
    validation = _identity("validation")
    if reuse == "static":
        validation["static"]["gpu"] = "GPU-other"
    else:
        validation["runtime"][reuse] = calibration["runtime"][reuse]
    body = f"""
$Calibration = {_ps(json.dumps(calibration))} | ConvertFrom-Json
$Validation = {_ps(json.dumps(validation))} | ConvertFrom-Json
Test-A11CrossPhaseIdentity -Calibration $Calibration -Validation $Validation |
    Out-Null
"""
    completed = _invoke_functions(("Test-A11CrossPhaseIdentity",), body)

    assert completed.returncode != 0


def test_campaign_orders_both_phases_and_never_retries() -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ [void]$script:Events.Add('preflight'); return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{
    [void]$script:Events.Add('destinations')
    return $true
}}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    [void]$script:Events.Add("identity:$Phase")
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
        specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
        image_tag="tag-$Phase"; image_id="sha256:$Phase"
        campaign_root="root-$Phase"; cache_root="cache-$Phase"
        cache_inventory_sha256='cache'; gpu_driver='driver'
        lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
        lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
        current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{ param($Identity,$Peer); [void]$script:Events.Add("init:$($Identity.phase)") }}
function Invoke-A11Build {{ param($Identity); [void]$script:Events.Add("build:$($Identity.phase)") }}
function Invoke-A11CachePreflight {{ param($Identity); [void]$script:Events.Add("cache:$($Identity.phase)") }}
function Confirm-A11CalibrationReceipt {{ [void]$script:Events.Add('calibration-precheck') }}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true; [void]$script:Events.Add("lease:$($Identity.phase)"); return @{{}} }}
function Invoke-A11Foundation {{ param($Identity); [void]$script:Events.Add("foundation:$($Identity.phase)") }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); [void]$script:Events.Add("replica:$($Identity.phase):$ReplicaId") }}
function Invoke-A11Gate {{
    param($Identity)
    [void]$script:Events.Add("gate:$($Identity.phase)")
    if ($Identity.phase -eq 'calibration') {{ return {_ps('WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN')} }}
    return {_ps('WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED')}
}}
function Assert-A11AggregateReceipt {{ param($Identity); [void]$script:Events.Add("verify:$($Identity.phase)") }}
function Release-A11Lease {{ param($Identity); $Identity.lease_acquired=$false; $Identity.release=@{{ok=$true}}; [void]$script:Events.Add("release:$($Identity.phase)") }}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ [void]$script:Events.Add('cross-phase') }}
$Result = Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)}
[ordered]@{{events=$script:Events;result=$Result}} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    events = output["events"]
    assert events[:6] == [
        "preflight",
        "identity:calibration",
        "identity:validation",
        "destinations",
        "init:calibration",
        "build:calibration",
    ]
    for phase in ("calibration", "validation"):
        replicas = [event for event in events if event.startswith(f"replica:{phase}:")]
        assert replicas == [
            f"replica:{phase}:{phase}-{index:02d}" for index in range(12)
        ]
        assert events.index(f"cache:{phase}") < events.index(f"lease:{phase}")
        assert events.index(f"lease:{phase}") < events.index(replicas[0])
        assert events.index(replicas[-1]) < events.index(f"gate:{phase}")
        assert events.index(f"gate:{phase}") < events.index(f"release:{phase}")
    assert events.index("release:calibration") < events.index("init:validation")
    cross_indexes = [
        index for index, event in enumerate(events) if event == "cross-phase"
    ]
    assert len(cross_indexes) == 2
    assert (
        events.index("cache:validation")
        < events.index("calibration-precheck")
        < cross_indexes[0]
    )
    assert (
        events.index("calibration-precheck")
        < cross_indexes[0]
        < events.index("lease:validation")
    )
    assert (
        events.index("release:validation")
        < cross_indexes[1]
        < events.index("close:validation")
    )
    assert events.count("gate:calibration") == events.count("gate:validation") == 1
    assert events[-1] == "close:validation"
    assert output["result"]["terminal"] == (
        "WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED"
    )


def test_campaign_destination_failure_precedes_initialization_and_writes_nothing(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "initialize-called"
    docker_marker = tmp_path / "docker-called"
    campaign_root = tmp_path / "campaign"
    validation_root = tmp_path / "validation"
    body = f"""
$Prior = {_ps(json.dumps(_prior_attempts()))} | ConvertFrom-Json
function Resolve-A11Worktree {{ return @{{ prior_a11_attempts=$Prior }} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function New-A11PhaseIdentity {{
    param($Phase)
    $Calibration = $Phase -ceq 'calibration'
    return [pscustomobject]@{{
        phase=$Phase
        run_id=if($Calibration){{{_ps(_FAILED_RUN_ID)}}}else{{'wave0-a11-validation-20260828T010101002Z-bbbbbbbb'}}
        image_tag=if($Calibration){{'fresh-calibration'}}else{{'fresh-validation'}}
        campaign_root=if($Calibration){{{_ps(str(campaign_root))}}}else{{{_ps(str(validation_root))}}}
        cache_root=if($Calibration){{{_ps(str(campaign_root / 'wave0' / 'model_cache'))}}}else{{{_ps(str(validation_root / 'wave0' / 'model_cache'))}}}
        lease_id="lease-$Phase"
        lease_path=if($Calibration){{{_ps(str(campaign_root / 'audit' / 'active-lease.json'))}}}else{{{_ps(str(validation_root / 'audit' / 'active-lease.json'))}}}
        lease_lock_path={_ps(str(tmp_path / 'leases' / f'{_GPU}.json'))}
        owner_authorization_id={_ps(_OWNER)}
        current_stage='preregistered'
    }}
}}
function Invoke-A11Native {{
    [IO.File]::WriteAllText({_ps(str(docker_marker))}, 'called')
    return [pscustomobject]@{{ExitCode=0;Stdout='';Stderr=''}}
}}
function Confirm-A11ProtectedGit {{ return $true }}
function Initialize-A11Phase {{
    [IO.File]::WriteAllText({_ps(str(marker))}, 'called')
    [IO.Directory]::CreateDirectory({_ps(str(campaign_root))}) | Out-Null
    throw 'injected:initialize'
}}
function Close-A11Phase {{}}
Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} `
    {_ps(_BRANCH)} {_ps(_OWNER)} | Out-Null
"""
    completed = _invoke_functions(
        (
            "Test-A11PathEntryPresent",
            "Test-A11PhaseDestinationsAbsent",
            "Invoke-A11Campaign",
        ),
        body,
    )

    assert completed.returncode != 0
    assert "preserved run identity" in completed.stderr
    assert completed.stderr.count("Exception:") == 1
    assert not marker.exists()
    assert not docker_marker.exists()
    assert not campaign_root.exists()
    assert not validation_root.exists()


def test_campaign_build_failure_publishes_one_complete_closure_and_stops(
    tmp_path: Path,
) -> None:
    calibration = tmp_path / "calibration"
    validation = tmp_path / "validation"
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    $Root = if ($Phase -ceq 'calibration') {{
        {_ps(str(calibration))}
    }} else {{
        {_ps(str(validation))}
    }}
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; campaign_root=$Root
        source_commit={_ps(_SOURCE)}; specification_commit={_ps(_SPEC)}
        plan_commit={_ps(_PLAN)}; image_tag="tag-$Phase"
        image_id='sha256:' + ('a' * 64); owner_authorization_id={_ps(_OWNER)}
        cache_root="$Root/cache"; cache_inventory_sha256=$null; gpu_driver=$null
        lease_id="lease-$Phase"; lease_path="$Root/lease"
        lease_lock_path="$Root/lease-lock"; lease_acquired=$false; release=$null
        replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{
    param($Identity)
    [void]$script:Events.Add("init:$($Identity.phase)")
    foreach ($Relative in @(
        'audit', 'wave0/receipts', 'wave0/checkpoints', 'wave0/model_cache'
    )) {{
        [IO.Directory]::CreateDirectory(
            [IO.Path]::Combine($Identity.campaign_root, $Relative)
        ) | Out-Null
    }}
}}
function Invoke-A11Build {{
    param($Identity)
    [void]$script:Events.Add("build:$($Identity.phase)")
    throw 'injected:build'
}}
function Get-A11HistoricalArtifactInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(64306)
        sha256={_ps(_HISTORICAL_FILES_SHA256)}
    }}
}}
function Get-A11HistoricalImageInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(21)
        sha256={_ps(_HISTORICAL_IMAGES_SHA256)}
    }}
}}
$Values = @(Invoke-A11Campaign `
    {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)})
[ordered]@{{
    count=$Values.Count
    result=$Values[0]
    events=@($script:Events)
}} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Close-A11Phase",
            "Invoke-A11Campaign",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["count"] == 1
    assert output["result"]["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    assert output["events"] == ["init:calibration", "build:calibration"]
    audit = calibration / "audit"
    assert sorted(path.name for path in audit.glob("*.json")) == [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ]
    assert not validation.exists()


def test_campaign_surfaces_closure_write_failure_without_retry(
    tmp_path: Path,
) -> None:
    calibration = tmp_path / "calibration"
    validation = tmp_path / "validation"
    diagnostic = calibration / "audit" / "78-failure-diagnostic.json"
    body = f"""
$script:ArtifactInventoryCalls = 0
$script:ImageInventoryCalls = 0
function Resolve-A11Worktree {{ return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{}}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    $Root = if ($Phase -ceq 'calibration') {{
        {_ps(str(calibration))}
    }} else {{
        {_ps(str(validation))}
    }}
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; campaign_root=$Root
        source_commit={_ps(_SOURCE)}; specification_commit={_ps(_SPEC)}
        plan_commit={_ps(_PLAN)}; image_tag="tag-$Phase"
        image_id='sha256:' + ('a' * 64); owner_authorization_id={_ps(_OWNER)}
        cache_root="$Root/cache"; cache_inventory_sha256=$null; gpu_driver=$null
        lease_id="lease-$Phase"; lease_path="$Root/lease"
        lease_lock_path="$Root/lease-lock"; lease_acquired=$false; release=$null
        replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{
    param($Identity)
    [IO.Directory]::CreateDirectory(
        [IO.Path]::Combine($Identity.campaign_root, 'audit')
    ) | Out-Null
    [IO.File]::WriteAllBytes(
        [IO.Path]::Combine(
            $Identity.campaign_root, 'audit', '78-failure-diagnostic.json'
        ),
        [Text.Encoding]::UTF8.GetBytes('sentinel')
    )
    throw 'injected:initialize'
}}
function Get-A11HistoricalArtifactInventory {{
    $script:ArtifactInventoryCalls++
    return [pscustomobject]@{{
        records=[object[]]::new(64306)
        sha256={_ps(_HISTORICAL_FILES_SHA256)}
    }}
}}
function Get-A11HistoricalImageInventory {{
    $script:ImageInventoryCalls++
    return [pscustomobject]@{{
        records=[object[]]::new(21)
        sha256={_ps(_HISTORICAL_IMAGES_SHA256)}
    }}
}}
$Values = @(Invoke-A11Campaign `
    {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)})
[ordered]@{{
    count=$Values.Count
    result=$Values[0]
    artifact_inventory_calls=$script:ArtifactInventoryCalls
    image_inventory_calls=$script:ImageInventoryCalls
}} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Close-A11Phase",
            "Invoke-A11Campaign",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["count"] == 1
    result = output["result"]
    assert result["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    assert result["error"] == "injected:initialize"
    assert "exists" in result["closure_error"].lower()
    assert output["artifact_inventory_calls"] == 1
    assert output["image_inventory_calls"] == 1
    assert diagnostic.read_bytes() == b"sentinel"


def test_campaign_suppresses_cache_evidence_and_emits_one_result() -> None:
    body = f"""
function Resolve-A11Worktree {{ return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{}}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
        specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
        image_tag="tag-$Phase"; image_id='sha256:' + ('a' * 64)
        campaign_root="root-$Phase"; cache_root="cache-$Phase"
        cache_inventory_sha256=$null; gpu_driver=$null
        lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
        lease_lock_path='global-lock'; lease_acquired=$false; release=$null
        replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{}}
function Invoke-A11Build {{}}
function Invoke-A11CachePreflight {{
    return [pscustomobject]@{{ cache='evidence' }}
}}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true }}
function Invoke-A11Foundation {{ throw 'injected:foundation' }}
function Release-A11Lease {{
    param($Identity)
    $Identity.lease_acquired=$false
    $Identity.release=[pscustomobject]@{{ released=$true }}
}}
function Close-A11Phase {{}}
$Values = @(Invoke-A11Campaign `
    {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)})
[ordered]@{{ count=$Values.Count; result=$Values[-1] }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["count"] == 1
    assert output["result"]["terminal"] == (
        "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    )
    assert output["result"]["error"] == "injected:foundation"


@pytest.mark.parametrize(
    ("values", "observed"),
    [
        ("$Values = @()", 0),
        (
            "$Values = @([pscustomobject]@{terminal='one'}, "
            + "[pscustomobject]@{terminal='two'})",
            2,
        ),
    ],
)
def test_single_campaign_result_rejects_zero_or_multiple_values(
    values: str, observed: int
) -> None:
    body = f"""
{values}
Get-A11SingleCampaignResult -Values $Values | Out-Null
"""
    completed = _invoke_functions(("Get-A11SingleCampaignResult",), body)

    assert completed.returncode != 0
    assert (
        f"A11 campaign result cardinality mismatch: expected 1, observed {observed}"
        in completed.stderr
    )


def test_calibration_failure_prohibits_validation_and_second_invocation() -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ [void]$script:Events.Add('preflight'); return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{ param($Phase); return [pscustomobject]@{{
    phase=$Phase; source_commit={_ps(_SOURCE)}; specification_commit={_ps(_SPEC)}
    plan_commit={_ps(_PLAN)}; image_tag="tag-$Phase"; image_id="sha256:$Phase"
    campaign_root="root-$Phase"; cache_root="cache-$Phase"; cache_inventory_sha256='cache'
    gpu_driver='driver'; lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
    lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
    audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
    current_stage='preregistered'; terminal=$null
}} }}
function Initialize-A11Phase {{ param($Identity,$Peer); [void]$script:Events.Add("init:$($Identity.phase)") }}
function Invoke-A11Build {{ param($Identity); [void]$script:Events.Add("build:$($Identity.phase)") }}
function Invoke-A11CachePreflight {{ param($Identity); [void]$script:Events.Add("cache:$($Identity.phase)") }}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true; [void]$script:Events.Add("lease:$($Identity.phase)") }}
function Invoke-A11Foundation {{ param($Identity); [void]$script:Events.Add("foundation:$($Identity.phase)") }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); [void]$script:Events.Add("replica:$($Identity.phase):$ReplicaId") }}
function Invoke-A11Gate {{ param($Identity); [void]$script:Events.Add("gate:$($Identity.phase)"); return 'FAIL' }}
function Assert-A11AggregateReceipt {{ throw 'must not verify failed calibration' }}
function Release-A11Lease {{ param($Identity); $Identity.lease_acquired=$false; $Identity.release=@{{ok=$true}}; [void]$script:Events.Add("release:$($Identity.phase)") }}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ throw 'must not compare phases' }}
$Result = Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)}
@{{ events=$script:Events; result=$Result }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    events = result["events"]
    assert events.count("gate:calibration") == 1
    assert not any("validation" in event for event in events)
    assert result["result"]["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"


@pytest.mark.parametrize(
    "failed_stage",
    [
        "initialize",
        "build",
        "cache",
        "lease",
        "foundation",
        "replica",
        "gate",
        "verify",
        "release",
    ],
)
def test_each_calibration_stage_failure_closes_once_without_retry(
    failed_stage: str,
) -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
$script:FailAt = {_ps(failed_stage)}
function Step {{
    param($Name,$Phase)
    [void]$script:Events.Add("$Name`:$Phase")
    if ($Name -ceq $script:FailAt) {{ throw "injected:$Name" }}
}}
function Resolve-A11Worktree {{ return @{{ prior_a11_attempts=@{{ attempts=@() }} }} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{ param($Phase); return [pscustomobject]@{{
    phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag="tag-$Phase"; image_id="sha256:$Phase"
    campaign_root="root-$Phase"; cache_root="cache-$Phase"; cache_inventory_sha256='cache'
    gpu_driver='driver'; lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
    lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
    audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
    current_stage='preregistered'; terminal=$null
}} }}
function Initialize-A11Phase {{ param($Identity,$Peer); Step initialize $Identity.phase }}
function Invoke-A11Build {{ param($Identity); Step build $Identity.phase }}
function Invoke-A11CachePreflight {{ param($Identity); Step cache $Identity.phase }}
function New-A11Lease {{
    param($Identity)
    Step lease $Identity.phase
    $Identity.lease_acquired=$true
}}
function Invoke-A11Foundation {{ param($Identity); Step foundation $Identity.phase }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); Step replica $Identity.phase }}
function Invoke-A11Gate {{
    param($Identity)
    Step gate $Identity.phase
    return {_ps('WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN')}
}}
function Assert-A11AggregateReceipt {{ param($Identity); Step verify $Identity.phase }}
function Release-A11Lease {{
    param($Identity)
    Step release $Identity.phase
    $Identity.lease_acquired=$false
    $Identity.release=@{{ok=$true}}
}}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ throw 'validation must remain forbidden' }}
$Result = Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)}
@{{ events=$script:Events; result=$Result }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    events = result["events"]
    assert events.count(f"{failed_stage}:calibration") == 1
    assert events.count("close:calibration") == 1
    assert not any(event.endswith(":validation") for event in events)
    assert result["result"]["terminal"] == (
        "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    )


def test_launcher_source_has_no_cleanup_retry_or_wave1_capability() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")

    assert "Remove-Item" not in source
    assert "docker image rm" not in source.lower()
    assert "--retry" not in source.lower()
    assert "OwnerAuthorizationId =" not in source
    assert source.count("for ($Index = 0; $Index -lt 12; $Index++)") == 1
    assert source.count("'build', '--no-cache'") == 1
    assert source.count("Invoke-A11Build $Identity") == 1
    values_index = source.index("$A11Values = @(")
    guard_index = source.index("Get-A11SingleCampaignResult -Values $A11Values")
    terminal_index = source.index("$A11Result.terminal", guard_index)
    assert values_index < guard_index < terminal_index
    assert "$A11Result.closure_error" in source
    assert "[Console]::Error.WriteLine" in source
