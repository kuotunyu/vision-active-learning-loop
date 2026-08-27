"""Real PowerShell behavior tests for the Wave 0 A7 launcher boundary."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_LAUNCHER = _ROOT / "scripts" / "start_wave0_a7.ps1"
_RUNNER = _ROOT / "scripts" / "run_wave0_a7.ps1"
_SOURCE = "a" * 40
_SPEC = "b" * 40
_PLAN = "c" * 40
_RUN_ID = "wave0-a7-20260826T120000000Z"
_TAG = f"vision-active-learning-loop:wave0-a7-{_SOURCE[:12]}-{_RUN_ID}"
_BASE = "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"


def _powershell_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _invoke_functions(
    names: tuple[str, ...], body: str
) -> subprocess.CompletedProcess[str]:
    if not _LAUNCHER.is_file():
        raise AssertionError("production A7 launcher script is missing")
    launcher = _powershell_literal(str(_LAUNCHER))
    requested = ",".join(_powershell_literal(name) for name in names)
    script = f"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {launcher}, [ref]$Tokens, [ref]$Errors
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
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _invoke_runner_functions(
    names: tuple[str, ...], body: str
) -> subprocess.CompletedProcess[str]:
    runner = _powershell_literal(str(_RUNNER))
    requested = ",".join(_powershell_literal(name) for name in names)
    script = f"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {runner}, [ref]$Tokens, [ref]$Errors
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
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _new_arguments_body(*, mutation: str | None = None) -> str:
    source = "z" * 40 if mutation == "malformed_source" else _SOURCE
    base = f"sha256:{'f' * 64}" if mutation == "wrong_base" else _BASE
    mutation_body = {
        None: "",
        "joined": (
            "$BuildArguments[7] = $BuildArguments[7] + "
            "' org.opencontainers.image.val.run_id=shadow'"
        ),
        "duplicate": (
            "$BuildArguments[9] = 'org.opencontainers.image.revision=' + "
            f"{_powershell_literal(_RUN_ID)}"
        ),
        "blank": "$BuildArguments[13] = 'org.opencontainers.image.val.plan_commit='",
        "malformed_source": "",
        "wrong_base": "",
        "sixth": (
            "$Prefix = @($BuildArguments[0..15]); "
            "$Suffix = @($BuildArguments[16..18]); "
            "$BuildArguments = @($Prefix + '--label' + "
            "'org.opencontainers.image.extra=forbidden' + $Suffix)"
        ),
        "whitespace_key": (
            "$BuildArguments[11] = $BuildArguments[11] + "
            "' org.opencontainers.image.val.plan_commit=shadow'"
        ),
    }[mutation]
    return f"""
$BuildArguments = @(New-A7BuildArguments `
    -SourceCommit {_powershell_literal(source)} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -BaseDigest {_powershell_literal(base)} `
    -ImageTag {_powershell_literal(_TAG)})
{mutation_body}
Assert-A7BuildArguments `
    -Arguments $BuildArguments `
    -SourceCommit {_powershell_literal(source)} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -BaseDigest {_powershell_literal(base)} `
    -ImageTag {_powershell_literal(_TAG)}
$BuildArguments | ConvertTo-Json -Compress
"""


def test_launcher_builds_five_independent_label_pairs() -> None:
    completed = _invoke_functions(
        ("New-A7BuildArguments", "Assert-A7BuildArguments"),
        _new_arguments_body(),
    )

    assert completed.returncode == 0, completed.stderr
    observed = json.loads(completed.stdout)
    assert observed[:7] == [
        "build",
        "--no-cache",
        "--progress",
        "plain",
        "--file",
        "docker/wave0.Dockerfile",
        "--label",
    ]
    assert observed[6:16] == [
        "--label",
        f"org.opencontainers.image.revision={_SOURCE}",
        "--label",
        f"org.opencontainers.image.val.run_id={_RUN_ID}",
        "--label",
        f"org.opencontainers.image.val.spec_commit={_SPEC}",
        "--label",
        f"org.opencontainers.image.val.plan_commit={_PLAN}",
        "--label",
        f"org.opencontainers.image.base.digest={_BASE}",
    ]
    assert observed[16:] == ["--tag", _TAG, "."]


@pytest.mark.parametrize(
    "mutation",
    [
        "joined",
        "duplicate",
        "blank",
        "malformed_source",
        "wrong_base",
        "sixth",
        "whitespace_key",
    ],
)
def test_launcher_rejects_invalid_label_vectors(mutation: str) -> None:
    completed = _invoke_functions(
        ("New-A7BuildArguments", "Assert-A7BuildArguments"),
        _new_arguments_body(mutation=mutation),
    )

    assert completed.returncode != 0


def test_launcher_preserves_zero_byte_stdout_and_exit_code(tmp_path: Path) -> None:
    stdout_path = tmp_path / "logs" / "stdout.log"
    stderr_path = tmp_path / "logs" / "stderr.log"
    stdout_path.parent.mkdir()
    body = f"""
$NativeArguments = @('-c', 'import sys; sys.exit(3)')
$Result = Invoke-A7Native `
    -Executable {_powershell_literal(sys.executable)} `
    -Arguments $NativeArguments `
    -StdoutPath {_powershell_literal(str(stdout_path))} `
    -StderrPath {_powershell_literal(str(stderr_path))}
$Result | ConvertTo-Json -Compress
"""

    completed = _invoke_functions(("Write-A7NewText", "Invoke-A7Native"), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["exit_code"] == 3
    assert result["stdout"] == ""
    assert result["stderr"] == ""
    assert stdout_path.is_file() and stdout_path.stat().st_size == 0
    assert stderr_path.is_file() and stderr_path.stat().st_size == 0


def test_launcher_passes_native_argv_without_shell_reparsing(tmp_path: Path) -> None:
    stdout_path = tmp_path / "stdout.log"
    stderr_path = tmp_path / "stderr.log"
    expected = ["two words", "semi;Write-Output injected", "$HOME", 'quote"value']
    native_arguments = [
        "-c",
        "import json,sys; print(json.dumps(sys.argv[1:]))",
        *expected,
    ]
    encoded_arguments = ",".join(
        _powershell_literal(value) for value in native_arguments
    )
    body = f"""
$NativeArguments = @({encoded_arguments})
$Result = Invoke-A7Native `
    -Executable {_powershell_literal(sys.executable)} `
    -Arguments $NativeArguments `
    -StdoutPath {_powershell_literal(str(stdout_path))} `
    -StderrPath {_powershell_literal(str(stderr_path))}
$Result | ConvertTo-Json -Compress
"""

    completed = _invoke_functions(("Write-A7NewText", "Invoke-A7Native"), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["exit_code"] == 0
    assert json.loads(result["stdout"]) == expected
    assert result["stderr"] == ""
    assert json.loads(stdout_path.read_text(encoding="utf-8")) == expected


def _inspect_document(*, mutation: str | None = None) -> str:
    labels = {
        "org.opencontainers.image.revision": _SOURCE,
        "org.opencontainers.image.val.run_id": _RUN_ID,
        "org.opencontainers.image.val.spec_commit": _SPEC,
        "org.opencontainers.image.val.plan_commit": _PLAN,
        "org.opencontainers.image.base.digest": _BASE,
        "org.opencontainers.image.vendor": "fixture-vendor",
    }
    image_id = f"sha256:{'d' * 64}"
    repo_tags = [_TAG]
    if mutation == "missing":
        labels.pop("org.opencontainers.image.val.run_id")
    elif mutation == "concatenated":
        labels[
            "org.opencontainers.image.revision"
        ] += f" org.opencontainers.image.val.run_id={_RUN_ID}"
        labels.pop("org.opencontainers.image.val.run_id")
    elif mutation == "wrong_label":
        labels["org.opencontainers.image.val.plan_commit"] = "e" * 40
    elif mutation == "wrong_tag":
        repo_tags = ["vision-active-learning-loop:wrong"]
    elif mutation == "wrong_id":
        image_id = f"sha256:{'e' * 64}"
    document = [
        {
            "Id": image_id,
            "RepoTags": repo_tags,
            "Config": {"Labels": labels},
        }
    ]
    if mutation == "multiple":
        document.append(json.loads(json.dumps(document[0])))
    return json.dumps(document, sort_keys=True, separators=(",", ":"))


def _inspect_body(document: str) -> str:
    image_id = f"sha256:{'d' * 64}"
    return f"""
Assert-A7ImageInspect `
    -InspectJson {_powershell_literal(document)} `
    -ImageId {_powershell_literal(image_id)} `
    -ImageTag {_powershell_literal(_TAG)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -BaseDigest {_powershell_literal(_BASE)}
'VERIFIED'
"""


def test_launcher_accepts_exact_single_image_inspect() -> None:
    completed = _invoke_functions(
        ("Assert-A7ImageInspect",), _inspect_body(_inspect_document())
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "VERIFIED"


@pytest.mark.parametrize(
    "mutation",
    ["missing", "concatenated", "wrong_label", "wrong_tag", "wrong_id", "multiple"],
)
def test_launcher_rejects_missing_concatenated_or_wrong_image_inspect_labels(
    mutation: str,
) -> None:
    completed = _invoke_functions(
        ("Assert-A7ImageInspect",), _inspect_body(_inspect_document(mutation=mutation))
    )

    assert completed.returncode != 0


def _git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _new_git_fixture(tmp_path: Path) -> tuple[Path, Path, str]:
    repository = tmp_path / "repository"
    linked = tmp_path / "linked"
    repository.mkdir()
    initialized = _git(repository, "init", "-b", "main")
    assert initialized.returncode == 0, initialized.stderr
    assert _git(repository, "config", "user.name", "Fixture").returncode == 0
    assert (
        _git(repository, "config", "user.email", "fixture@example.invalid").returncode
        == 0
    )
    (repository / "tracked.txt").write_text("baseline\n", encoding="utf-8")
    assert _git(repository, "add", "tracked.txt").returncode == 0
    committed = _git(repository, "commit", "-m", "baseline")
    assert committed.returncode == 0, committed.stderr
    head = _git(repository, "rev-parse", "HEAD").stdout.strip()
    assert _git(repository, "branch", "codex/fixture").returncode == 0
    added = _git(
        repository,
        "worktree",
        "add",
        str(linked),
        "codex/fixture",
    )
    assert added.returncode == 0, added.stderr
    return repository, linked, head


def _resolve_worktree_body(repository: Path, branch: str, head: str) -> str:
    return f"""
$Resolved = Resolve-A7Worktree `
    -RepositoryRoot {_powershell_literal(str(repository))} `
    -ExpectedBranch {_powershell_literal(branch)} `
    -ExpectedHead {_powershell_literal(head)}
$Resolved | ConvertTo-Json -Compress
"""


def test_launcher_resolves_exact_clean_registered_worktree(tmp_path: Path) -> None:
    repository, linked, head = _new_git_fixture(tmp_path)

    completed = _invoke_functions(
        ("Resolve-A7Worktree",),
        _resolve_worktree_body(repository, "codex/fixture", head),
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert Path(result["worktree"]).resolve() == linked.resolve()
    assert Path(result["canonical_root"]).resolve() == repository.resolve()
    assert Path(result["common_dir"]).resolve() == (repository / ".git").resolve()
    assert result["branch"] == "codex/fixture"
    assert result["head"] == head


@pytest.mark.parametrize("mutation", ["branch", "head"])
def test_launcher_rejects_wrong_git_identity(tmp_path: Path, mutation: str) -> None:
    repository, _, head = _new_git_fixture(tmp_path)
    branch = "codex/wrong" if mutation == "branch" else "codex/fixture"
    expected_head = "f" * 40 if mutation == "head" else head

    completed = _invoke_functions(
        ("Resolve-A7Worktree",),
        _resolve_worktree_body(repository, branch, expected_head),
    )

    assert completed.returncode != 0


@pytest.mark.parametrize("mutation", ["linked", "canonical", "staged"])
def test_launcher_rejects_dirty_git_identity(tmp_path: Path, mutation: str) -> None:
    repository, linked, head = _new_git_fixture(tmp_path)
    if mutation == "linked":
        (linked / "untracked.txt").write_text("dirty\n", encoding="utf-8")
    elif mutation == "canonical":
        (repository / "untracked.txt").write_text("dirty\n", encoding="utf-8")
    else:
        (linked / "tracked.txt").write_text("staged\n", encoding="utf-8")
        assert _git(linked, "add", "tracked.txt").returncode == 0

    completed = _invoke_functions(
        ("Resolve-A7Worktree",),
        _resolve_worktree_body(repository, "codex/fixture", head),
    )

    assert completed.returncode != 0


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _history_fixture(tmp_path: Path) -> dict[str, object]:
    fixture = _protected_git_lineage_fixture(tmp_path)
    artifact_root = Path(fixture["artifact_root"])
    for name in ("failed-b/evidence.txt", "failed-a/evidence.txt"):
        path = artifact_root / name
        path.parent.mkdir()
        path.write_text(name + "\n", encoding="utf-8")
    original_image = fixture["current_images"][0]
    current_images = [
        {
            "tag": "vision-active-learning-loop:wave0-failed-b",
            "image_id": f"sha256:{'3' * 64}",
        },
        original_image,
        {
            "tag": "vision-active-learning-loop:wave0-failed-a",
            "image_id": f"sha256:{'2' * 64}",
        },
    ]
    fixture["current_images"] = current_images
    fixture["output"] = tmp_path / "augmented.json"
    fixture["protected_root"] = fixture["repository"]
    return fixture


def _history_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = New-A7AugmentedBaseline `
    -OriginalBaselinePath {_powershell_literal(str(fixture['baseline_path']))} `
    -ExpectedBaselineSha256 {_powershell_literal(str(fixture['baseline_sha256']))} `
    -ArtifactRoot {_powershell_literal(str(fixture['artifact_root']))} `
    -ProtectedGitRoot {_powershell_literal(str(fixture['protected_root']))} `
    -ImageRecordsJson {_powershell_literal(json.dumps(fixture['current_images']))} `
    -SourceCommit {_powershell_literal(str(fixture['source_commit']))} `
    -GitExecutable {_powershell_literal(str(fixture['git']))} `
    -ExpectedSpecCommit {_powershell_literal(str(fixture['spec_commit']))} `
    -ExpectedPlanCommit {_powershell_literal(str(fixture['plan_commit']))} `
    -OutputPath {_powershell_literal(str(fixture['output']))}
$Result | ConvertTo-Json -Compress
"""


def test_history_augments_exact_original_subset_with_preserved_failures(
    tmp_path: Path,
) -> None:
    fixture = _history_fixture(tmp_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7AugmentedBaseline"), _history_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    output = Path(fixture["output"])
    document = json.loads(output.read_text(encoding="utf-8"))
    assert result["sha256"] == _sha256(output)
    assert result["artifact_count"] == 3
    assert result["image_count"] == 3
    assert result["protected_git_count"] == 68
    assert document["source_commit"] == fixture["source_commit"]
    assert document["parent_baseline_sha256"] == "4" * 64
    assert [entry["path"] for entry in document["artifact_files"]] == [
        "failed-a/evidence.txt",
        "failed-b/evidence.txt",
        "original.txt",
    ]
    assert [entry["tag"] for entry in document["images"]] == sorted(
        entry["tag"] for entry in fixture["current_images"]
    )


def test_history_accepts_regular_baseline_file_under_strict_mode(
    tmp_path: Path,
) -> None:
    fixture = _history_fixture(tmp_path)
    body = "Set-StrictMode -Version Latest\n" + _history_body(fixture)

    completed = _invoke_functions(("Write-A7NewText", "New-A7AugmentedBaseline"), body)

    assert completed.returncode == 0, completed.stderr
    assert Path(fixture["output"]).is_file()


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_artifact",
        "changed_artifact",
        "duplicate_artifact",
        "phantom_artifact",
        "changed_protected_git",
        "changed_image_id",
        "duplicate_image",
        "wrong_baseline_hash",
        "existing_destination",
    ],
)
def test_history_rejects_drift_duplicates_and_existing_destination(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _history_fixture(tmp_path)
    baseline = fixture["baseline"]
    if mutation == "missing_artifact":
        (Path(fixture["artifact_root"]) / "original.txt").unlink()
    elif mutation == "changed_artifact":
        (Path(fixture["artifact_root"]) / "original.txt").write_text(
            "changed\n", encoding="utf-8"
        )
    elif mutation == "duplicate_artifact":
        baseline["artifact_files"].append(dict(baseline["artifact_files"][0]))
    elif mutation == "phantom_artifact":
        baseline["artifact_files"].append(
            {"path": "phantom.txt", "size": 0, "sha256": "0" * 64}
        )
    elif mutation == "changed_protected_git":
        (Path(fixture["protected_root"]) / "protected/record-00.txt").write_text(
            "changed\n", encoding="utf-8"
        )
    elif mutation == "changed_image_id":
        fixture["current_images"][1]["image_id"] = f"sha256:{'9' * 64}"
    elif mutation == "duplicate_image":
        fixture["current_images"].append(dict(fixture["current_images"][0]))
    elif mutation == "wrong_baseline_hash":
        fixture["baseline_sha256"] = "f" * 64
    elif mutation == "existing_destination":
        Path(fixture["output"]).write_text("occupied", encoding="utf-8")
    if mutation in {"duplicate_artifact", "phantom_artifact"}:
        Path(fixture["baseline_path"]).write_text(
            json.dumps(baseline, sort_keys=True, separators=(",", ":")),
            encoding="utf-8",
        )
        fixture["baseline_sha256"] = _sha256(Path(fixture["baseline_path"]))

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7AugmentedBaseline"), _history_body(fixture)
    )

    assert completed.returncode != 0


def test_history_rejects_symlinked_baseline_path(tmp_path: Path) -> None:
    fixture = _history_fixture(tmp_path)
    target = Path(fixture["baseline_path"])
    link = tmp_path / "baseline-link.json"
    try:
        link.symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    fixture["baseline_path"] = link
    fixture["baseline_sha256"] = _sha256(target)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7AugmentedBaseline"), _history_body(fixture)
    )

    assert completed.returncode != 0


_TRANSITION_PATH = (
    "docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md"
)
_COMPATIBILITY_PLAN_PATH = "docs/superpowers/plans/2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md"


def _git_stdout(repository: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


def _protected_record(repository: Path, relative_path: str) -> dict[str, object]:
    path = repository / Path(relative_path)
    return {
        "path": relative_path,
        "size": path.stat().st_size,
        "sha256": _sha256(path),
    }


def _rewrite_lineage_baseline(fixture: dict[str, object]) -> None:
    path = Path(fixture["baseline_path"])
    path.write_text(
        json.dumps(fixture["baseline"], sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    fixture["baseline_sha256"] = _sha256(path)


def _protected_git_lineage_fixture(tmp_path: Path) -> dict[str, object]:
    repository = tmp_path / "protected-repository"
    repository.mkdir()
    _git_stdout(repository, "init", "--initial-branch=fixture-main")
    _git_stdout(repository, "config", "core.autocrlf", "false")
    _git_stdout(repository, "config", "user.name", "fixture")
    _git_stdout(repository, "config", "user.email", "fixture@example.invalid")

    unchanged_paths = [f"protected/record-{index:02d}.txt" for index in range(67)]
    for index, relative_path in enumerate(unchanged_paths):
        path = repository / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"immutable-{index:02d}\n", encoding="utf-8")
    spec_path = repository / _TRANSITION_PATH
    spec_path.parent.mkdir(parents=True)
    spec_path.write_text("approved spec before compatibility\n", encoding="utf-8")
    _git_stdout(repository, "add", "--", "protected", _TRANSITION_PATH)
    _git_stdout(repository, "commit", "-m", "fixture: root protected state")

    root_paths = sorted([*unchanged_paths, _TRANSITION_PATH])
    root_records = [_protected_record(repository, path) for path in root_paths]

    spec_path.write_text("approved spec with compatibility\n", encoding="utf-8")
    _git_stdout(repository, "add", "--", _TRANSITION_PATH)
    _git_stdout(repository, "commit", "-m", "docs: approve compatibility")
    spec_commit = _git_stdout(repository, "rev-parse", "HEAD")
    spec_git_object = _git_stdout(repository, "rev-parse", f"HEAD:{_TRANSITION_PATH}")

    plan_path = repository / _COMPATIBILITY_PLAN_PATH
    plan_path.parent.mkdir(parents=True)
    plan_path.write_text("approved compatibility plan\n", encoding="utf-8")
    _git_stdout(repository, "add", "--", _COMPATIBILITY_PLAN_PATH)
    _git_stdout(repository, "commit", "-m", "docs: plan compatibility")
    plan_commit = _git_stdout(repository, "rev-parse", "HEAD")

    marker = repository / "implementation-marker.txt"
    marker.write_text("candidate\n", encoding="utf-8")
    _git_stdout(repository, "add", "--", marker.name)
    _git_stdout(repository, "commit", "-m", "fix: candidate marker")
    source_commit = _git_stdout(repository, "rev-parse", "HEAD")

    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    artifact = artifact_root / "original.txt"
    artifact.write_text("immutable history\n", encoding="utf-8")
    image = {
        "tag": "vision-active-learning-loop:wave0-fixture",
        "image_id": f"sha256:{'1' * 64}",
    }
    baseline = {
        "schema_version": 1,
        "parent_baseline_sha256": "4" * 64,
        "artifact_root": str(artifact_root),
        "artifact_files": [
            {
                "path": "original.txt",
                "size": artifact.stat().st_size,
                "sha256": _sha256(artifact),
            }
        ],
        "images": [image],
        "protected_git": root_records,
    }
    baseline_path = tmp_path / "lineage-root-baseline.json"
    baseline_path.write_text(
        json.dumps(baseline, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    current_records = [_protected_record(repository, path) for path in root_paths]
    root_transition = next(
        record for record in root_records if record["path"] == _TRANSITION_PATH
    )
    current_transition = next(
        record for record in current_records if record["path"] == _TRANSITION_PATH
    )
    return {
        "artifact_root": artifact_root,
        "baseline": baseline,
        "baseline_path": baseline_path,
        "baseline_sha256": _sha256(baseline_path),
        "current_images": [image],
        "current_records": current_records,
        "git": shutil.which("git") or "git",
        "output": tmp_path / "lineage-augmented.json",
        "plan_commit": plan_commit,
        "repository": repository,
        "root_records": root_records,
        "source_commit": source_commit,
        "spec_commit": spec_commit,
        "spec_git_object": spec_git_object,
        "transition": {
            "path": _TRANSITION_PATH,
            "root_size": root_transition["size"],
            "root_sha256": root_transition["sha256"],
            "current_size": current_transition["size"],
            "current_sha256": current_transition["sha256"],
            "spec_commit": spec_commit,
            "spec_git_object": spec_git_object,
            "plan_commit": plan_commit,
            "reason": "owner-approved-design-amendment",
        },
        "transition_path": _TRANSITION_PATH,
    }


def _lineage_history_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = New-A7AugmentedBaseline `
    -OriginalBaselinePath {_powershell_literal(str(fixture['baseline_path']))} `
    -ExpectedBaselineSha256 {_powershell_literal(str(fixture['baseline_sha256']))} `
    -ArtifactRoot {_powershell_literal(str(fixture['artifact_root']))} `
    -ProtectedGitRoot {_powershell_literal(str(fixture['repository']))} `
    -ImageRecordsJson {_powershell_literal(json.dumps(fixture['current_images']))} `
    -SourceCommit {_powershell_literal(str(fixture['source_commit']))} `
    -GitExecutable {_powershell_literal(str(fixture['git']))} `
    -ExpectedSpecCommit {_powershell_literal(str(fixture['spec_commit']))} `
    -ExpectedPlanCommit {_powershell_literal(str(fixture['plan_commit']))} `
    -OutputPath {_powershell_literal(str(fixture['output']))}
$Result | ConvertTo-Json -Compress
"""


def _invoke_augmented_lineage(
    fixture: dict[str, object],
) -> subprocess.CompletedProcess[str]:
    return _invoke_functions(
        ("Write-A7NewText", "New-A7AugmentedBaseline"),
        _lineage_history_body(fixture),
    )


def test_history_accepts_only_owner_approved_spec_transition(tmp_path: Path) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)

    completed = _invoke_augmented_lineage(fixture)

    assert completed.returncode == 0, completed.stderr
    document = json.loads(Path(fixture["output"]).read_text(encoding="utf-8"))
    assert document["protected_git"] == fixture["root_records"]
    assert document["current_protected_git"] == fixture["current_records"]
    assert document["approved_protected_git_transitions"] == [fixture["transition"]]


def test_history_records_all_67_unchanged_protected_git_paths(tmp_path: Path) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)

    completed = _invoke_augmented_lineage(fixture)

    assert completed.returncode == 0, completed.stderr
    document = json.loads(Path(fixture["output"]).read_text(encoding="utf-8"))
    root = {record["path"]: record for record in document["protected_git"]}
    current = {record["path"]: record for record in document["current_protected_git"]}
    unchanged = [path for path in root if path != fixture["transition_path"]]
    assert len(unchanged) == 67
    assert all(root[path] == current[path] for path in unchanged)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_transition",
        "duplicate_root_path",
        "wrong_root_hash",
        "missing_unchanged_path",
        "changed_unchanged_path",
        "dirty_spec",
        "staged_spec",
        "wrong_source_commit",
        "wrong_spec_commit",
        "non_parent_plan",
        "existing_destination",
    ],
)
def test_history_rejects_forbidden_protected_git_lineage_mutations(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)
    repository = Path(fixture["repository"])
    baseline = fixture["baseline"]
    if mutation == "missing_transition":
        baseline["protected_git"] = [
            record
            for record in baseline["protected_git"]
            if record["path"] != _TRANSITION_PATH
        ]
        _rewrite_lineage_baseline(fixture)
    elif mutation == "duplicate_root_path":
        baseline["protected_git"].append(dict(baseline["protected_git"][0]))
        _rewrite_lineage_baseline(fixture)
    elif mutation == "wrong_root_hash":
        baseline["protected_git"][-1]["sha256"] = "f" * 64
        _rewrite_lineage_baseline(fixture)
    elif mutation == "missing_unchanged_path":
        (repository / "protected/record-00.txt").unlink()
    elif mutation == "changed_unchanged_path":
        (repository / "protected/record-00.txt").write_text(
            "changed\n", encoding="utf-8"
        )
    elif mutation == "dirty_spec":
        (repository / _TRANSITION_PATH).write_text("dirty\n", encoding="utf-8")
    elif mutation == "staged_spec":
        (repository / _TRANSITION_PATH).write_text("staged\n", encoding="utf-8")
        _git_stdout(repository, "add", "--", _TRANSITION_PATH)
    elif mutation == "wrong_source_commit":
        fixture["source_commit"] = "f" * 40
    elif mutation == "wrong_spec_commit":
        fixture["spec_commit"] = str(fixture["source_commit"])
    elif mutation == "non_parent_plan":
        fixture["plan_commit"] = str(fixture["source_commit"])
    elif mutation == "existing_destination":
        Path(fixture["output"]).write_text("occupied", encoding="utf-8")

    completed = _invoke_augmented_lineage(fixture)

    assert completed.returncode != 0


def _prepare_task8_lineage_fixture(tmp_path: Path) -> dict[str, object]:
    fixture = _protected_git_lineage_fixture(tmp_path)
    completed = _invoke_augmented_lineage(fixture)
    assert completed.returncode == 0, completed.stderr
    fixture["augmented_sha256"] = _sha256(Path(fixture["output"]))
    return fixture


def _rewrite_augmented_lineage(fixture: dict[str, object]) -> None:
    path = Path(fixture["output"])
    path.write_text(
        json.dumps(fixture["augmented"], sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    fixture["augmented_sha256"] = _sha256(path)


def _task8_lineage_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = Test-A7ProtectedGitLineage `
    -RootBaselinePath {_powershell_literal(str(fixture['baseline_path']))} `
    -RootBaselineSha256 {_powershell_literal(str(fixture['baseline_sha256']))} `
    -AugmentedBaselinePath {_powershell_literal(str(fixture['output']))} `
    -AugmentedBaselineSha256 {_powershell_literal(str(fixture['augmented_sha256']))} `
    -ProjectRoot {_powershell_literal(str(fixture['repository']))} `
    -SourceCommit {_powershell_literal(str(fixture['source_commit']))} `
    -SpecCommit {_powershell_literal(str(fixture['spec_commit']))} `
    -PlanCommit {_powershell_literal(str(fixture['plan_commit']))}
$Result | ConvertTo-Json -Compress
"""


def _invoke_task8_lineage(
    fixture: dict[str, object],
) -> subprocess.CompletedProcess[str]:
    return _invoke_runner_functions(
        ("Test-A7ProtectedGitLineage",), _task8_lineage_body(fixture)
    )


def test_task8_accepts_the_exact_approved_protected_git_transition(
    tmp_path: Path,
) -> None:
    fixture = _prepare_task8_lineage_fixture(tmp_path)

    completed = _invoke_task8_lineage(fixture)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "root_protected_git_count": 68,
        "current_protected_git_count": 68,
        "approved_transition_count": 1,
        "status": "PRESERVED",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_transition",
        "second_transition",
        "wrong_transition_path",
        "wrong_reason",
        "wrong_root_hash",
        "wrong_current_hash",
        "wrong_spec_commit",
        "wrong_spec_object",
        "wrong_plan_commit",
        "missing_current_path",
        "extra_current_path",
        "changed_unchanged_current",
        "dirty_checkout",
        "non_parent_plan",
    ],
)
def test_task8_rejects_forbidden_protected_git_lineage_mutations(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _prepare_task8_lineage_fixture(tmp_path)
    augmented = json.loads(Path(fixture["output"]).read_text(encoding="utf-8"))
    fixture["augmented"] = augmented
    transition = augmented["approved_protected_git_transitions"][0]
    if mutation == "missing_transition":
        augmented["approved_protected_git_transitions"] = []
    elif mutation == "second_transition":
        duplicate = dict(transition)
        duplicate["path"] = "protected/record-00.txt"
        augmented["approved_protected_git_transitions"].append(duplicate)
    elif mutation == "wrong_transition_path":
        transition["path"] = "protected/record-00.txt"
    elif mutation == "wrong_reason":
        transition["reason"] = "wildcard-amendment"
    elif mutation == "wrong_root_hash":
        transition["root_sha256"] = "f" * 64
    elif mutation == "wrong_current_hash":
        transition["current_sha256"] = "f" * 64
    elif mutation == "wrong_spec_commit":
        transition["spec_commit"] = str(fixture["source_commit"])
    elif mutation == "wrong_spec_object":
        transition["spec_git_object"] = "f" * 40
    elif mutation == "wrong_plan_commit":
        transition["plan_commit"] = str(fixture["source_commit"])
    elif mutation == "missing_current_path":
        augmented["current_protected_git"].pop(0)
    elif mutation == "extra_current_path":
        augmented["current_protected_git"].append(
            {"path": "extra.txt", "size": 0, "sha256": "0" * 64}
        )
    elif mutation == "changed_unchanged_current":
        augmented["current_protected_git"][0]["sha256"] = "f" * 64
    elif mutation == "dirty_checkout":
        (Path(fixture["repository"]) / "protected/record-00.txt").write_text(
            "dirty\n", encoding="utf-8"
        )
    elif mutation == "non_parent_plan":
        fixture["plan_commit"] = str(fixture["source_commit"])
    if mutation not in {"dirty_checkout", "non_parent_plan"}:
        _rewrite_augmented_lineage(fixture)

    completed = _invoke_task8_lineage(fixture)

    assert completed.returncode != 0


def test_task8_runner_orders_lineage_before_artifact_history() -> None:
    runner = _powershell_literal(str(_RUNNER))
    command = f"""
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {runner}, [ref]$Tokens, [ref]$Errors
)
if ($Errors.Count -ne 0) {{ throw 'parse failure' }}
$Calls = @($Ast.FindAll({{
    param($Node)
    if ($Node -isnot [Management.Automation.Language.CommandAst]) {{ return $false }}
    if ($Node.GetCommandName() -notin @(
        'Test-A7ProtectedGitLineage', 'Test-HistoricalBaseline'
    )) {{ return $false }}
    $Parent = $Node.Parent
    while ($null -ne $Parent) {{
        if ($Parent -is [Management.Automation.Language.FunctionDefinitionAst]) {{ return $false }}
        $Parent = $Parent.Parent
    }}
    return $true
}}, $true) | Sort-Object {{ $_.Extent.StartOffset }})
$Calls | ForEach-Object {{ $_.GetCommandName() }}
"""
    completed = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.splitlines() == [
        "Test-A7ProtectedGitLineage",
        "Test-HistoricalBaseline",
    ]


def test_task8_runner_mounts_only_the_verified_run_scoped_cache() -> None:
    source = _RUNNER.read_text(encoding="utf-8")

    assert "$Task7Binding = Test-Task7AuditBinding" in source
    assert "$ModelCacheRoot = [string]$Task7Binding.model_cache_root" in source
    assert "$HistoricalModelCache" not in source
    assert '"${ModelCacheRoot}:/artifacts/wave0/model_cache:ro"' in source
    assert "'HF_HUB_OFFLINE=1'" in source
    assert "'TRANSFORMERS_OFFLINE=1'" in source


def test_launcher_and_runner_bind_the_a9_plan_identity() -> None:
    expected = (
        "docs/superpowers/plans/"
        "2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md"
    )

    for path in (_LAUNCHER, _RUNNER):
        source = path.read_text(encoding="utf-8")
        assert expected in source
        assert "2026-08-27-val-wave0-a8-cache-and-lease-lifecycle.md" not in source
        assert "2026-08-26-val-wave0-a7-history-compatibility.md" not in source


def _historical_lease_fixture(tmp_path: Path) -> dict[str, Path]:
    artifact_root = tmp_path / "artifacts"
    leases = artifact_root / "leases"
    leases.mkdir(parents=True)
    historical = artifact_root / "historical.txt"
    historical.write_text("immutable\n", encoding="utf-8")
    campaign = artifact_root / "a7-runs" / _RUN_ID
    campaign.mkdir(parents=True)
    (campaign / "current.txt").write_text("current\n", encoding="utf-8")
    root = tmp_path / "root-baseline.json"
    root_document = {
        "artifact_root": str(artifact_root),
        "artifact_files": [
            {
                "path": "historical.txt",
                "size": historical.stat().st_size,
                "sha256": _sha256(historical),
            }
        ],
        "images": [],
        "protected_git": [],
    }
    root.write_text(json.dumps(root_document, separators=(",", ":")), encoding="utf-8")
    augmented = tmp_path / "augmented-baseline.json"
    augmented.write_text(
        json.dumps(
            {
                **root_document,
                "parent_baseline_sha256": _sha256(root),
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    active = leases / "GPU-12345678.json"
    active.write_text('{"lease":true}', encoding="utf-8")
    return {
        "artifact_root": artifact_root,
        "campaign": campaign,
        "root": root,
        "augmented": augmented,
        "active": active,
        "released": leases / f"{_RUN_ID}.released",
        "release_record": leases / f"{_RUN_ID}.release.json",
    }


def _historical_lease_body(fixture: dict[str, Path]) -> str:
    return f"""
$CampaignRoot = {_powershell_literal(str(fixture['campaign']))}
$ImageTag = 'vision-active-learning-loop:wave0-current'
$RunId = {_powershell_literal(_RUN_ID)}
$Lease = [pscustomobject]@{{ gpu_uuid = 'GPU-12345678' }}
function docker {{
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    $global:LASTEXITCODE = 0
}}
$Result = Test-HistoricalBaseline `
    -RootBaselinePath {_powershell_literal(str(fixture['root']))} `
    -RootBaselineSha256 {_powershell_literal(_sha256(fixture['root']))} `
    -AugmentedBaselinePath {_powershell_literal(str(fixture['augmented']))} `
    -AugmentedBaselineSha256 {_powershell_literal(_sha256(fixture['augmented']))} `
    -ActiveLeasePath {_powershell_literal(str(fixture['active']))} `
    -ReleasedLeasePath {_powershell_literal(str(fixture['released']))} `
    -ReleaseRecordPath {_powershell_literal(str(fixture['release_record']))}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def test_task8_history_excludes_only_the_current_active_lease(tmp_path: Path) -> None:
    fixture = _historical_lease_fixture(tmp_path)

    completed = _invoke_runner_functions(
        ("Test-HistoricalBaseline",), _historical_lease_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    active_relative = "leases/GPU-12345678.json"
    assert result["status"] == "PRESERVED"
    assert result["approved_lease_exclusions"] == [
        active_relative,
        f"leases/{_RUN_ID}.release.json",
        f"leases/{_RUN_ID}.released",
    ]
    assert result["observed_lease_exclusions"] == [active_relative]
    assert result["baseline_artifact_count"] == 1
    assert result["observed_historical_count"] == 1
    assert result["exact_set_match"] is True


def test_task8_history_requires_lifecycle_paths_in_task8_context(
    tmp_path: Path,
) -> None:
    fixture = _historical_lease_fixture(tmp_path)
    body = f"""
$CampaignRoot = {_powershell_literal(str(fixture['campaign']))}
$ImageTag = 'vision-active-learning-loop:wave0-current'
$RunId = {_powershell_literal(_RUN_ID)}
$Lease = [pscustomobject]@{{ gpu_uuid = 'GPU-12345678' }}
function docker {{ $global:LASTEXITCODE = 0 }}
Test-HistoricalBaseline `
    -RootBaselinePath {_powershell_literal(str(fixture['root']))} `
    -RootBaselineSha256 {_powershell_literal(_sha256(fixture['root']))} `
    -AugmentedBaselinePath {_powershell_literal(str(fixture['augmented']))} `
    -AugmentedBaselineSha256 {_powershell_literal(_sha256(fixture['augmented']))}
"""

    completed = _invoke_runner_functions(("Test-HistoricalBaseline",), body)

    assert completed.returncode != 0
    assert "requires lease lifecycle paths" in completed.stderr


@pytest.mark.parametrize(
    "mutation",
    (
        "missing_active",
        "preexisting_released",
        "preexisting_release_record",
        "wrong_active_name",
        "unapproved_extra",
    ),
)
def test_task8_history_rejects_unauthorized_lease_state(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _historical_lease_fixture(tmp_path)
    if mutation == "missing_active":
        fixture["active"].unlink()
    elif mutation == "preexisting_released":
        fixture["released"].write_text("occupied\n", encoding="utf-8")
    elif mutation == "preexisting_release_record":
        fixture["release_record"].write_text("{}\n", encoding="utf-8")
    elif mutation == "wrong_active_name":
        wrong_active = fixture["active"].with_name("wrong.json")
        fixture["active"].replace(wrong_active)
        fixture["active"] = wrong_active
    elif mutation == "unapproved_extra":
        (fixture["active"].parent / "unapproved.json").write_text(
            "unexpected\n", encoding="utf-8"
        )

    completed = _invoke_runner_functions(
        ("Test-HistoricalBaseline",), _historical_lease_body(fixture)
    )

    assert completed.returncode != 0


def test_task8_history_rejects_linked_active_lease(tmp_path: Path) -> None:
    fixture = _historical_lease_fixture(tmp_path)
    target = tmp_path / "lease-target.json"
    fixture["active"].replace(target)
    try:
        fixture["active"].symlink_to(target)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")

    completed = _invoke_runner_functions(
        ("Test-HistoricalBaseline",), _historical_lease_body(fixture)
    )

    assert completed.returncode != 0


def _gpu_preflight_body(mutation: str | None = None) -> str:
    gpu_row = "GPU-12345678,NVIDIA GeForce RTX 4090,24564,100,24464"
    context = "desktop-linux"
    version = {"Client": {"Version": "fixture"}, "Server": {"Os": "linux"}}
    info = {"OSType": "linux"}
    wsl = "Running"
    compute = "GPU-12345678,4321,C:/Windows/dwm.exe,[N/A]"
    containers: list[dict[str, str]] = []
    leases: list[str] = []
    val_data_root = ""
    if mutation == "wrong_context":
        context = "default"
    elif mutation == "missing_server":
        version.pop("Server")
    elif mutation == "wrong_server":
        version["Server"] = {"Os": "windows"}
    elif mutation == "wrong_info":
        info["OSType"] = "windows"
    elif mutation == "wsl_stopped":
        wsl = "Stopped"
    elif mutation == "zero_gpu":
        gpu_row = ""
    elif mutation == "two_gpu":
        gpu_row += "\nGPU-87654321,NVIDIA GeForce RTX 4090,24564,0,24564"
    elif mutation == "wrong_gpu_name":
        gpu_row = "GPU-12345678,NVIDIA RTX 6000 Ada,24564,100,24464"
    elif mutation == "wrong_gpu_uuid":
        gpu_row = "12345678,NVIDIA GeForce RTX 4090,24564,100,24464"
    elif mutation == "numeric_compute":
        compute = "GPU-12345678,9876,C:/compute.exe,512"
    elif mutation == "active_container":
        containers = [{"id": "abc", "name": "val-wave0"}]
    elif mutation == "active_lease":
        leases = ["D:/leases/active.json"]
    elif mutation == "val_data_root":
        val_data_root = "D:/RDD"
    return f"""
$Result = Test-A7DockerGpuPreflight `
    -DockerContext {_powershell_literal(context)} `
    -DockerVersionJson {_powershell_literal(json.dumps(version))} `
    -DockerInfoJson {_powershell_literal(json.dumps(info))} `
    -DockerDesktopWslState {_powershell_literal(wsl)} `
    -DockerGpuCsv {_powershell_literal(gpu_row)} `
    -HostComputeCsv {_powershell_literal(compute)} `
    -ProjectContainersJson {_powershell_literal(json.dumps(containers))} `
    -ActiveLeasePathsJson {_powershell_literal(json.dumps(leases))} `
    -ValDataRoot {_powershell_literal(val_data_root)}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def test_docker_gpu_preflight_accepts_single_idle_rtx4090_with_wddm_rows() -> None:
    completed = _invoke_functions(("Test-A7DockerGpuPreflight",), _gpu_preflight_body())

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["gpu_uuid"] == "GPU-12345678"
    assert result["gpu_name"] == "NVIDIA GeForce RTX 4090"
    assert result["memory_total_mib"] == 24564
    assert result["host_processes"][0]["used_gpu_memory_mib"] is None
    assert result["containers"] == []


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_context",
        "missing_server",
        "wrong_server",
        "wrong_info",
        "wsl_stopped",
        "zero_gpu",
        "two_gpu",
        "wrong_gpu_name",
        "wrong_gpu_uuid",
        "numeric_compute",
        "active_container",
        "active_lease",
        "val_data_root",
    ],
)
def test_docker_gpu_preflight_rejects_unapproved_or_contended_state(
    mutation: str,
) -> None:
    completed = _invoke_functions(
        ("Test-A7DockerGpuPreflight",), _gpu_preflight_body(mutation)
    )

    assert completed.returncode != 0


def _project_container_body(
    records: list[dict[str, str]], registered_image_ids: list[str]
) -> str:
    return f"""
$Result = Select-A7ProjectContainers `
    -ContainerRecordsJson {_powershell_literal(json.dumps(records))} `
    -RegisteredImageIdsJson {_powershell_literal(json.dumps(registered_image_ids))}
ConvertTo-Json -InputObject @($Result) -Depth 6 -Compress
"""


def _container_record(**overrides: str) -> dict[str, str]:
    record = {
        "id": "a" * 64,
        "name": "unrelated",
        "configured_image": "nvidia/cuda@sha256:" + "b" * 64,
        "image_id": "sha256:" + "c" * 64,
    }
    record.update(overrides)
    return record


@pytest.mark.parametrize(
    ("overrides", "registered_image_ids"),
    [
        ({"name": "val-a7-worker"}, []),
        ({"name": "val-wave0-worker"}, []),
        ({"configured_image": "vision-active-learning-loop:wave0-a7-fixture"}, []),
        ({}, ["sha256:" + "c" * 64]),
    ],
)
def test_project_container_selector_matches_only_approved_ownership_signals(
    overrides: dict[str, str], registered_image_ids: list[str]
) -> None:
    record = _container_record(**overrides)

    completed = _invoke_functions(
        ("Select-A7ProjectContainers",),
        _project_container_body([record], registered_image_ids),
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [record]


def test_digest_launched_project_container_matches_registered_image_id() -> None:
    record = _container_record(
        configured_image="nvidia/cuda@sha256:" + "b" * 64,
        image_id="sha256:" + "d" * 64,
    )

    completed = _invoke_functions(
        ("Select-A7ProjectContainers",),
        _project_container_body([record], ["sha256:" + "d" * 64]),
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [record]


@pytest.mark.parametrize(
    "record",
    [
        _container_record(name="other-val-a7-worker"),
        _container_record(configured_image="vision-active-learning-loop:not-wave0"),
        _container_record(image_id="sha256:" + "e" * 64),
    ],
)
def test_project_container_selector_rejects_substring_and_unrelated_matches(
    record: dict[str, str],
) -> None:
    completed = _invoke_functions(
        ("Select-A7ProjectContainers",),
        _project_container_body([record], ["sha256:" + "d" * 64]),
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == []


@pytest.mark.parametrize(
    "mutation",
    [
        "duplicate_container_id",
        "missing_field",
        "extra_field",
        "malformed_container_id",
        "malformed_image_id",
        "duplicate_registered_image_id",
    ],
)
def test_project_container_selector_fails_closed_on_malformed_inventory(
    mutation: str,
) -> None:
    records = [_container_record()]
    registered = ["sha256:" + "d" * 64]
    if mutation == "duplicate_container_id":
        duplicate = _container_record(name="second")
        records.append(duplicate)
    elif mutation == "missing_field":
        records[0].pop("configured_image")
    elif mutation == "extra_field":
        records[0]["status"] = "running"
    elif mutation == "malformed_container_id":
        records[0]["id"] = "short"
    elif mutation == "malformed_image_id":
        records[0]["image_id"] = "d" * 64
    elif mutation == "duplicate_registered_image_id":
        registered.append(registered[0])

    completed = _invoke_functions(
        ("Select-A7ProjectContainers",),
        _project_container_body(records, registered),
    )

    assert completed.returncode != 0


def _lease_fixture(tmp_path: Path) -> dict[str, object]:
    fixture = _closed_audit_fixture(tmp_path)
    lease_root = tmp_path / "leases"
    lease_root.mkdir()
    fixture["lease"] = lease_root / "gpu-0.json"
    fixture["baseline_hash"] = _sha256(Path(fixture["baseline"]))
    fixture["build_hash"] = _sha256(Path(fixture["build"]))
    fixture["microcheck_hash"] = _sha256(Path(fixture["microcheck"]))
    return fixture


def _lease_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = New-A7Lease `
    -LeasePath {_powershell_literal(str(fixture['lease']))} `
    -OwnerAuthorizationId 'owner-a7-fixture' `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -Branch 'codex/fixture' `
    -ImageTag {_powershell_literal(_TAG)} `
    -ImageId 'sha256:{'d' * 64}' `
    -BaseImageDigest {_powershell_literal(_BASE)} `
    -GpuUuid 'GPU-12345678' `
    -CampaignRoot {_powershell_literal(str(fixture['campaign']))} `
    -HistoricalBaselinePath {_powershell_literal(str(fixture['baseline']))} `
    -HistoricalBaselineSha256 {_powershell_literal(str(fixture['baseline_hash']))} `
    -BuildAuditPath {_powershell_literal(str(fixture['build']))} `
    -BuildAuditSha256 {_powershell_literal(str(fixture['build_hash']))} `
    -MicrocheckAuditPath {_powershell_literal(str(fixture['microcheck']))} `
    -MicrocheckAuditSha256 {_powershell_literal(str(fixture['microcheck_hash']))} `
    -ModelCacheRoot {_powershell_literal(str(fixture['model_cache_root']))} `
    -ModelCachePreflightAuditPath {_powershell_literal(str(fixture['model_cache_audit']))} `
    -ModelCachePreflightAuditSha256 {_powershell_literal(str(fixture['model_cache_audit_hash']))} `
    -ModelCacheReceiptPath {_powershell_literal(str(fixture['model_cache_receipt']))} `
    -ModelCacheReceiptSha256 {_powershell_literal(str(fixture['model_cache_receipt_hash']))} `
    -HostProcessesJson '[{{"gpu_uuid":"GPU-12345678","pid":4321,"process_name":"dwm.exe","used_gpu_memory_mib":null}}]' `
    -ContainersJson '[]' `
    -ClaimedAt '2026-08-26T12:00:00.0000000Z'
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def test_gpu_lease_is_atomic_hash_bound_and_parseable(tmp_path: Path) -> None:
    fixture = _lease_fixture(tmp_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"), _lease_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    lease = Path(fixture["lease"])
    document = json.loads(lease.read_text(encoding="utf-8"))
    assert result["sha256"] == _sha256(lease)
    assert document["run_id"] == _RUN_ID
    assert document["build_audit_sha256"] == fixture["build_hash"]
    assert document["microcheck_audit_sha256"] == fixture["microcheck_hash"]
    assert document["host_processes"][0]["used_gpu_memory_mib"] is None
    assert document["containers"] == []


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_build",
        "missing_microcheck",
        "changed_build_hash",
        "changed_microcheck_hash",
        "existing_lease",
        "missing_baseline",
    ],
)
def test_gpu_lease_rejects_missing_changed_or_contended_inputs(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _lease_fixture(tmp_path)
    if mutation == "missing_build":
        Path(fixture["build"]).unlink()
    elif mutation == "missing_microcheck":
        Path(fixture["microcheck"]).unlink()
    elif mutation == "changed_build_hash":
        fixture["build_hash"] = "e" * 64
    elif mutation == "changed_microcheck_hash":
        fixture["microcheck_hash"] = "e" * 64
    elif mutation == "existing_lease":
        Path(fixture["lease"]).write_text("occupied", encoding="utf-8")
    elif mutation == "missing_baseline":
        Path(fixture["baseline"]).unlink()

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"), _lease_body(fixture)
    )

    assert completed.returncode != 0
    if mutation != "existing_lease":
        assert not Path(fixture["lease"]).exists()


def test_gpu_lease_rejects_symlinked_lease_root(tmp_path: Path) -> None:
    fixture = _lease_fixture(tmp_path)
    target = tmp_path / "real-leases"
    target.mkdir()
    link = tmp_path / "linked-leases"
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    fixture["lease"] = link / "gpu-0.json"

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"), _lease_body(fixture)
    )

    assert completed.returncode != 0


def _closure_fixture(tmp_path: Path) -> dict[str, object]:
    artifact_root = tmp_path / "artifacts"
    campaign = artifact_root / "a7-runs" / _RUN_ID
    audit = campaign / "audit"
    protected_root = tmp_path / "protected"
    artifact_root.mkdir()
    protected_root.mkdir()
    historical = artifact_root / "historical.txt"
    historical.write_text("immutable\n", encoding="utf-8")
    protected = protected_root / "contract.txt"
    protected.write_text("protected\n", encoding="utf-8")
    baseline = tmp_path / "augmented.json"
    image = {
        "tag": "vision-active-learning-loop:wave0-historical",
        "image_id": f"sha256:{'1' * 64}",
    }
    baseline.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": _SOURCE,
                "parent_baseline_sha256": "4" * 64,
                "artifact_root": str(artifact_root),
                "artifact_files": [
                    {
                        "path": "historical.txt",
                        "size": historical.stat().st_size,
                        "sha256": _sha256(historical),
                    }
                ],
                "images": [image],
                "protected_git": [
                    {
                        "path": "contract.txt",
                        "size": protected.stat().st_size,
                        "sha256": _sha256(protected),
                    }
                ],
                "current_protected_git": [
                    {
                        "path": "contract.txt",
                        "size": protected.stat().st_size,
                        "sha256": _sha256(protected),
                    }
                ],
                "approved_protected_git_transitions": [
                    {
                        "path": "contract.txt",
                        "root_size": protected.stat().st_size,
                        "root_sha256": _sha256(protected),
                        "current_size": protected.stat().st_size,
                        "current_sha256": _sha256(protected),
                        "spec_commit": "a" * 40,
                        "spec_git_object": "b" * 40,
                        "plan_commit": "c" * 40,
                        "reason": "owner-approved-design-amendment",
                    }
                ],
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    audit.mkdir(parents=True)
    (audit / "00-task7-identity.json").write_text("{}", encoding="utf-8")
    return {
        "artifact_root": artifact_root,
        "campaign": campaign,
        "audit": audit,
        "protected_root": protected_root,
        "baseline": baseline,
        "baseline_hash": _sha256(baseline),
        "images": [image],
        "lease": tmp_path / "leases" / "gpu.json",
    }


def _closure_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = Close-A7Campaign `
    -CampaignRoot {_powershell_literal(str(fixture['campaign']))} `
    -ProtectedGitRoot {_powershell_literal(str(fixture['protected_root']))} `
    -HistoricalBaselinePath {_powershell_literal(str(fixture['baseline']))} `
    -HistoricalBaselineSha256 {_powershell_literal(str(fixture['baseline_hash']))} `
    -CurrentImagesJson {_powershell_literal(json.dumps(fixture['images']))} `
    -CurrentImageTag {_powershell_literal(_TAG)} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -Stage 'image_build' `
    -FailureMessage 'fixture build failed' `
    -LeasePath {_powershell_literal(str(fixture['lease']))} `
    -Terminal 'WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def test_transition_post_claim_failure_writes_complete_closure(tmp_path: Path) -> None:
    fixture = _closure_fixture(tmp_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "Get-A7LeaseReleasePaths", "Close-A7Campaign"),
        _closure_body(fixture),
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    audit = Path(fixture["audit"])
    expected = {
        "23-image-build-failure-diagnostic.json",
        "30-historical-preservation.json",
        "40-campaign-result.json",
        "41-campaign-file-manifest.json",
        "51-campaign-closure-manifest.json",
    }
    assert expected.issubset({path.name for path in audit.iterdir()})
    assert result["state"] == "CLOSED"
    assert result["lease_acquired"] is False
    closure = json.loads(
        (audit / "51-campaign-closure-manifest.json").read_text(encoding="utf-8")
    )
    assert closure["terminal"].endswith("WAVE1_FORBIDDEN")
    assert len(closure["files"]) == 4
    for record in closure["files"]:
        path = Path(fixture["campaign"]) / record["path"]
        assert path.stat().st_size == record["size"]
        assert _sha256(path) == record["sha256"]


def test_closure_preserves_owner_approved_protected_git_transition(
    tmp_path: Path,
) -> None:
    fixture = _closure_fixture(tmp_path)
    baseline_path = Path(fixture["baseline"])
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    root_payload = b"owner-approved-root-version\n"
    root_sha256 = hashlib.sha256(root_payload).hexdigest()
    root_record = baseline["protected_git"][0]
    current_record = baseline["current_protected_git"][0]
    root_record["size"] = len(root_payload)
    root_record["sha256"] = root_sha256
    transition = baseline["approved_protected_git_transitions"][0]
    transition["root_size"] = len(root_payload)
    transition["root_sha256"] = root_sha256
    transition["current_size"] = current_record["size"]
    transition["current_sha256"] = current_record["sha256"]
    baseline_path.write_text(
        json.dumps(baseline, separators=(",", ":")), encoding="utf-8"
    )
    fixture["baseline_hash"] = _sha256(baseline_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "Get-A7LeaseReleasePaths", "Close-A7Campaign"),
        _closure_body(fixture),
    )

    assert completed.returncode == 0, completed.stderr
    preservation = json.loads(
        (Path(fixture["audit"]) / "30-historical-preservation.json").read_text(
            encoding="utf-8"
        )
    )
    assert preservation["preserved"] is True
    assert preservation["error"] is None


def test_closure_no_clobber_rejects_existing_destination(tmp_path: Path) -> None:
    fixture = _closure_fixture(tmp_path)
    diagnostic = Path(fixture["audit"]) / "23-image-build-failure-diagnostic.json"
    diagnostic.write_text("occupied", encoding="utf-8")

    completed = _invoke_functions(
        ("Write-A7NewText", "Get-A7LeaseReleasePaths", "Close-A7Campaign"),
        _closure_body(fixture),
    )

    assert completed.returncode != 0
    assert diagnostic.read_text(encoding="utf-8") == "occupied"


def _write_docker_adapter(path: Path) -> None:
    path.write_text(
        """import json
import sys
from pathlib import Path

args = list(sys.argv[1:])
if args[:1] != ["--state"] or len(args) < 5 or args[2:3] != ["--mode"]:
    raise SystemExit(90)
state_path = Path(args[1])
mode = args[3]
command = args[4:]
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {
    "build_count": 0,
    "microcheck_count": 0,
    "model_cache_preflight_count": 0,
    "commands": [],
}
state["commands"].append(command)
if command[:1] == ["build"]:
    state["build_count"] += 1
    labels = {}
    for index, value in enumerate(command):
        if value == "--label":
            key, label_value = command[index + 1].split("=", 1)
            labels[key] = label_value
    tag = command[command.index("--tag") + 1]
    state.update({"labels": labels, "tag": tag, "built": mode != "build_fail"})
    state_path.write_text(json.dumps(state), encoding="utf-8")
    raise SystemExit(7 if mode == "build_fail" else 0)
if command[:2] == ["image", "inspect"]:
    if not state.get("built"):
        state_path.write_text(json.dumps(state), encoding="utf-8")
        raise SystemExit(1)
    labels = dict(state["labels"])
    if mode == "inspect_wrong":
        labels["org.opencontainers.image.val.plan_commit"] = "f" * 40
    document = [{
        "Id": "sha256:" + "d" * 64,
        "RepoTags": [state["tag"]],
        "Config": {"Labels": labels},
    }]
    print(json.dumps(document, separators=(",", ":")))
    state_path.write_text(json.dumps(state), encoding="utf-8")
    raise SystemExit(0)
if command[:1] == ["run"]:
    entrypoint = command[command.index("--entrypoint") + 1]
    if entrypoint == "val":
        state["model_cache_preflight_count"] += 1
        mount = next(value for value in command if value.endswith(":/artifacts:rw"))
        artifact_root = Path(mount[: -len(":/artifacts:rw")])
        receipt_path = artifact_root / "wave0" / "receipts" / "model-assets.json"
        empty_sha = __import__("hashlib").sha256(b"").hexdigest()
        locks = {
            f".cache/huggingface/download/{filename}.lock": {
                "size": 0,
                "sha256": empty_sha,
            }
            for filename in (
                "README.md",
                "config.json",
                "model.safetensors",
                "preprocessor_config.json",
            )
        }
        models = {
            "rtdetr": {
                "name": "rtdetr",
                "repo_id": "PekingU/rtdetr_r18vd",
                "revision": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
                "huggingface_metadata": {
                    "commit_hash": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
                    "inventory": locks,
                },
            },
            "dinov2": {
                "name": "dinov2",
                "repo_id": "facebook/dinov2-small",
                "revision": "ed25f3a31f01632728cabb09d1542f84ab7b0056",
                "huggingface_metadata": {
                    "commit_hash": "ed25f3a31f01632728cabb09d1542f84ab7b0056",
                    "inventory": locks,
                },
            },
        }
        receipt = {
            "schema_version": 1,
            "receipt_type": "model-assets",
            "normative": {"status": "PASS", "errors": [], "models": models},
            "metadata": {"run_id": state["labels"]["org.opencontainers.image.val.run_id"]},
        }
        if mode == "cache_wrong_run":
            receipt["metadata"]["run_id"] = "wave0-a7-20260827T000000000Z"
        elif mode == "cache_wrong_revision":
            receipt["normative"]["models"]["rtdetr"]["revision"] = "f" * 40
        elif mode == "cache_missing_lock":
            del receipt["normative"]["models"]["rtdetr"]["huggingface_metadata"]["inventory"][".cache/huggingface/download/README.md.lock"]
        elif mode == "cache_nonzero_lock":
            receipt["normative"]["models"]["dinov2"]["huggingface_metadata"]["inventory"][".cache/huggingface/download/config.json.lock"] = {"size": 1, "sha256": "f" * 64}
        elif mode == "cache_extra_lock":
            receipt["normative"]["models"]["rtdetr"]["huggingface_metadata"]["inventory"][".cache/huggingface/download/extra.lock"] = {"size": 0, "sha256": empty_sha}
        elif mode == "cache_fail_receipt":
            receipt["normative"]["status"] = "FAIL"
            receipt["normative"]["errors"] = ["fixture"]
        if mode == "cache_malformed_receipt":
            receipt_path.write_text("not-json", encoding="utf-8")
        elif mode != "cache_missing_receipt" and mode != "cache_exit":
            receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")
        state_path.write_text(json.dumps(state), encoding="utf-8")
        if mode == "cache_stderr":
            print("unexpected stderr", file=sys.stderr)
        print("NOT-PASS" if mode == "cache_stdout" else "PASS")
        raise SystemExit(7 if mode == "cache_exit" else 0)
    state["microcheck_count"] += 1
    state_path.write_text(json.dumps(state), encoding="utf-8")
    if mode == "micro_blank":
        raise SystemExit(0)
    if mode == "micro_malformed":
        print("not-json")
        raise SystemExit(0)
    mount = next(value for value in command if value.endswith(":/audit:ro"))
    audit_root = Path(mount[: -len(":/audit:ro")])
    inventory_path = audit_root / "21-a7-source-inventory.json"
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    result = {
        "schema_version": 1,
        "status": "RECORDED",
        "source_commit": inventory["source_commit"],
        "source_inventory_sha256": __import__("hashlib").sha256(inventory_path.read_bytes()).hexdigest(),
        "source_files": inventory["files"],
        "manifest_target": "vision_active_learning_loop.diagnostics.grid_sample_attribution:main",
        "canonical_dtypes": ["bfloat16", "float16", "float32", "float64"],
        "snapshot_tensor_count": 27,
        "snapshot_names": [f"tensor-{index:02d}" for index in range(27)],
        "snapshot_corruption_rejected": True,
        "receipt_kinds": ["control", "instrumented", "isolated-vjp", "aggregate"],
        "classifier_statuses": ["ATTRIBUTED", "INCONCLUSIVE", "NOT_ATTRIBUTED"],
        "cuda_initialized": mode == "micro_cuda",
    }
    if mode == "micro_wrong_source":
        result["source_commit"] = "f" * 40
    payload = json.dumps(result, separators=(",", ":"))
    print(payload)
    if mode == "micro_multiple":
        print(payload)
    raise SystemExit(0)
raise SystemExit(91)
""",
        encoding="utf-8",
    )


def _write_task8_adapter(
    path: Path, state_path: Path, *, mode: str = "ok", exit_code: int = 0
) -> None:
    path.write_text(
        f"""import hashlib
import json
import os
import sys
from pathlib import Path

args = sys.argv[1:]
state_path = Path({str(state_path)!r})
mode = {mode!r}
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {{}}
state["task8_count"] = state.get("task8_count", 0) + 1
state["task8_argv"] = args
state_path.write_text(json.dumps(state), encoding="utf-8")
values = dict(zip(args[0::2], args[1::2]))
campaign = Path(values["-HostCampaignRoot"])
audit = campaign / "audit"
lease = Path(values["-LeasePath"])
released = lease.parent / f"{{values['-RunId']}}.released"
release_record = lease.parent / f"{{values['-RunId']}}.release.json"
lease_document = json.loads(lease.read_text(encoding="utf-8"))
lease_sha256 = hashlib.sha256(lease.read_bytes()).hexdigest()
release_document = {{
    "schema_version": 1,
    "run_id": values["-RunId"],
    "source_commit": lease_document["source_commit"],
    "image_digest": values["-ImageDigest"],
    "released_at": "2026-08-27T12:34:56.0000000Z",
    "original_lease_sha256": lease_sha256,
}}
if mode == "task8_release_hash_mismatch":
    release_document["original_lease_sha256"] = "0" * 64
elif mode == "task8_release_wrong_run":
    release_document["run_id"] = "wave0-a7-20260827T000000000Z"
elif mode == "task8_release_wrong_source":
    release_document["source_commit"] = "f" * 40
elif mode == "task8_release_wrong_image":
    release_document["image_digest"] = "sha256:" + "e" * 64
elif mode == "task8_release_extra_field":
    release_document["unexpected"] = True
elif mode == "task8_release_bad_timestamp":
    release_document["released_at"] = "not-a-timestamp"
if mode == "task8_active_lease":
    pass
elif mode == "task8_missing_release":
    lease.unlink()
    release_record.write_text(json.dumps(release_document), encoding="utf-8")
elif mode == "task8_missing_release_record":
    os.replace(lease, released)
else:
    os.replace(lease, released)
    release_record.write_text(json.dumps(release_document), encoding="utf-8")
terminal = "WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
if mode != "task8_missing_30":
    (audit / "30-historical-preservation.json").write_text(json.dumps({{"preserved": True}}), encoding="utf-8")
if mode != "task8_missing_40":
    result_text = "not-json" if mode == "task8_malformed_result" else json.dumps({{
        "run_id": values["-RunId"],
        "terminal": (
            "WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
            if mode == "task8_terminal_mismatch" else terminal
        ),
    }})
    (audit / "40-campaign-result.json").write_text(result_text, encoding="utf-8")
if mode != "task8_missing_41":
    (audit / "41-campaign-file-manifest.json").write_text(json.dumps({{"files": []}}), encoding="utf-8")
records = []
for name in ("30-historical-preservation.json", "40-campaign-result.json", "41-campaign-file-manifest.json"):
    target = audit / name
    if target.is_file():
        records.append({{"path": "audit/" + name, "size": target.stat().st_size, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}})
if mode != "task8_missing_51":
    closure_text = "not-json" if mode == "task8_malformed_closure" else json.dumps({{
        "run_id": values["-RunId"], "terminal": terminal, "files": records
    }})
    (audit / "51-campaign-closure-manifest.json").write_text(closure_text, encoding="utf-8")
if mode == "task8_hash_drift":
    (audit / "30-historical-preservation.json").write_text("drifted", encoding="utf-8")
if mode == "task8_preexisting_52":
    (audit / "52-task7-post-task8-validation-failure.json").write_text("occupied-52", encoding="utf-8")
if mode == "task8_preexisting_53":
    (audit / "53-task7-post-task8-validation-closure.json").write_text("occupied-53", encoding="utf-8")
owned = []
for name in (
    "30-historical-preservation.json", "40-campaign-result.json",
    "41-campaign-file-manifest.json", "51-campaign-closure-manifest.json",
):
    target = audit / name
    if target.is_file():
        owned.append({{
            "path": name,
            "size": target.stat().st_size,
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }})
state["task8_owned_before_validation"] = owned
state_path.write_text(json.dumps(state), encoding="utf-8")
raise SystemExit({exit_code})
""",
        encoding="utf-8",
    )


def _launch_fixture(
    tmp_path: Path, *, mode: str = "ok", task8_exit: int = 0
) -> dict[str, object]:
    artifact_root = tmp_path / "artifacts"
    (artifact_root / "a7-runs").mkdir(parents=True)
    lease_root = artifact_root / "leases"
    lease_root.mkdir()
    historical = artifact_root / "historical.txt"
    historical.write_text("immutable\n", encoding="utf-8")
    protected_root = tmp_path / "protected"
    protected_root.mkdir()
    protected = protected_root / "contract.txt"
    protected.write_text("protected\n", encoding="utf-8")
    image = {
        "tag": "vision-active-learning-loop:wave0-historical",
        "image_id": f"sha256:{'1' * 64}",
    }
    baseline = tmp_path / "augmented.json"
    baseline.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_commit": _SOURCE,
                "parent_baseline_sha256": "4" * 64,
                "artifact_root": str(artifact_root),
                "artifact_files": [
                    {
                        "path": "historical.txt",
                        "size": historical.stat().st_size,
                        "sha256": _sha256(historical),
                    }
                ],
                "images": [image],
                "protected_git": [
                    {
                        "path": "contract.txt",
                        "size": protected.stat().st_size,
                        "sha256": _sha256(protected),
                    }
                ],
                "current_protected_git": [
                    {
                        "path": "contract.txt",
                        "size": protected.stat().st_size,
                        "sha256": _sha256(protected),
                    }
                ],
                "approved_protected_git_transitions": [
                    {
                        "path": "contract.txt",
                        "root_size": protected.stat().st_size,
                        "root_sha256": _sha256(protected),
                        "current_size": protected.stat().st_size,
                        "current_sha256": _sha256(protected),
                        "spec_commit": "a" * 40,
                        "spec_git_object": "b" * 40,
                        "plan_commit": "c" * 40,
                        "reason": "owner-approved-design-amendment",
                    }
                ],
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    docker_state = tmp_path / "docker-state.json"
    docker_adapter = tmp_path / "docker_adapter.py"
    task8_state = tmp_path / "task8-state.json"
    task8_adapter = tmp_path / "task8_adapter.py"
    _write_docker_adapter(docker_adapter)
    effective_task8_exit = 9 if mode == "task8_valid_nonzero" else task8_exit
    _write_task8_adapter(
        task8_adapter, task8_state, mode=mode, exit_code=effective_task8_exit
    )
    preflight = {
        "gpu_uuid": "GPU-12345678",
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "host_processes": [
            {
                "gpu_uuid": "GPU-12345678",
                "pid": 4321,
                "process_name": "dwm.exe",
                "used_gpu_memory_mib": None,
            }
        ],
        "containers": [],
    }
    return {
        "artifact_root": artifact_root,
        "lease_root": lease_root,
        "protected_root": protected_root,
        "baseline": baseline,
        "baseline_hash": _sha256(baseline),
        "images": [image],
        "docker_state": docker_state,
        "docker_adapter": docker_adapter,
        "docker_prefix": [
            str(docker_adapter),
            "--state",
            str(docker_state),
            "--mode",
            mode,
        ],
        "task8_state": task8_state,
        "task8_adapter": task8_adapter,
        "preflight": preflight,
        "campaign": artifact_root / "a7-runs" / _RUN_ID,
        "lease": lease_root / "GPU-12345678.json",
    }


_LAUNCH_FUNCTIONS = (
    "New-A7BuildArguments",
    "Get-A7LeaseReleasePaths",
    "Assert-A7LeaseReleaseEvidence",
    "Assert-A7BuildArguments",
    "Write-A7NewText",
    "Invoke-A7Native",
    "Invoke-A7ModelCachePreflight",
    "Assert-A7ImageInspect",
    "New-A7Lease",
    "Close-A7Campaign",
    "Close-A7PostTask8ValidationFailure",
    "Invoke-A7Launch",
)


def _launch_body(fixture: dict[str, object]) -> str:
    docker_prefix = ",".join(
        _powershell_literal(value) for value in fixture["docker_prefix"]
    )
    return f"""
$Result = Invoke-A7Launch `
    -RegisteredWorktree {_powershell_literal(str(_ROOT))} `
    -ProtectedGitRoot {_powershell_literal(str(fixture['protected_root']))} `
    -ArtifactRoot {_powershell_literal(str(fixture['artifact_root']))} `
    -LeaseRoot {_powershell_literal(str(fixture['lease_root']))} `
    -HistoricalBaselinePath {_powershell_literal(str(fixture['baseline']))} `
    -HistoricalBaselineSha256 {_powershell_literal(str(fixture['baseline_hash']))} `
    -HistoricalImagesJson {_powershell_literal(json.dumps(fixture['images']))} `
    -PreflightJson {_powershell_literal(json.dumps(fixture['preflight']))} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -ExpectedSourceCommit {_powershell_literal(_SOURCE)} `
    -ExpectedSpecCommit {_powershell_literal(_SPEC)} `
    -ExpectedPlanCommit {_powershell_literal(_PLAN)} `
    -ExpectedBranch 'codex/fixture' `
    -OwnerAuthorizationId 'owner-a7-fixture' `
    -DockerExecutable {_powershell_literal(sys.executable)} `
    -DockerPrefixArguments @({docker_prefix}) `
    -Task8Executable {_powershell_literal(sys.executable)} `
    -Task8PrefixArguments @() `
    -Task8RunnerPath {_powershell_literal(str(fixture['task8_adapter']))}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


_BUILD_AUDIT_FIELDS = {
    "schema_version",
    "owner_authorization_id",
    "run_id",
    "source_commit",
    "spec_commit",
    "plan_commit",
    "branch",
    "image_tag",
    "image_id",
    "base_image_digest",
    "argv",
    "augmented_baseline_path",
    "augmented_baseline_sha256",
    "argv_audit_path",
    "argv_audit_sha256",
    "stdout_path",
    "stdout_sha256",
    "stderr_path",
    "stderr_sha256",
    "exit_code",
    "started_at",
    "completed_at",
}
_MICROCHECK_AUDIT_FIELDS = {
    "schema_version",
    "owner_authorization_id",
    "run_id",
    "source_commit",
    "spec_commit",
    "plan_commit",
    "branch",
    "image_tag",
    "image_id",
    "base_image_digest",
    "augmented_baseline_path",
    "augmented_baseline_sha256",
    "source_inventory_path",
    "source_inventory_sha256",
    "payload_path",
    "payload_sha256",
    "payload",
    "docker_argv",
    "stdout_path",
    "stdout_sha256",
    "stderr_path",
    "stderr_sha256",
    "exit_code",
    "started_at",
    "completed_at",
}
_MODEL_CACHE_AUDIT_FIELDS = {
    "schema_version",
    "owner_authorization_id",
    "run_id",
    "source_commit",
    "spec_commit",
    "plan_commit",
    "branch",
    "image_tag",
    "image_id",
    "base_image_digest",
    "augmented_baseline_path",
    "augmented_baseline_sha256",
    "docker_argv",
    "network",
    "gpu_enabled",
    "cache_root",
    "receipt_path",
    "receipt_sha256",
    "receipt_models",
    "stdout_path",
    "stdout_sha256",
    "stderr_path",
    "stderr_sha256",
    "exit_code",
    "started_at",
    "completed_at",
}


def _microcheck_payload(source_inventory_sha256: str) -> dict[str, object]:
    return {
        "schema_version": 1,
        "status": "RECORDED",
        "source_commit": _SOURCE,
        "source_inventory_sha256": source_inventory_sha256,
        "source_files": [],
        "manifest_target": (
            "vision_active_learning_loop.diagnostics.grid_sample_attribution:main"
        ),
        "canonical_dtypes": ["bfloat16", "float16", "float32", "float64"],
        "snapshot_tensor_count": 27,
        "snapshot_names": [f"tensor-{index:02d}" for index in range(27)],
        "snapshot_corruption_rejected": True,
        "receipt_kinds": [
            "control",
            "instrumented",
            "isolated-vjp",
            "aggregate",
        ],
        "classifier_statuses": ["ATTRIBUTED", "INCONCLUSIVE", "NOT_ATTRIBUTED"],
        "cuda_initialized": False,
    }


def _closed_audit_fixture(tmp_path: Path) -> dict[str, object]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    audit.mkdir(parents=True)
    baseline = tmp_path / "augmented-baseline.json"
    baseline.write_text('{"baseline":true}', encoding="utf-8")
    image_id = "sha256:" + "d" * 64
    build_argv = ["docker", "build", "--tag", _TAG, "."]
    microcheck_argv = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--workdir",
        "/workspace",
        "--entrypoint",
        "python",
        "-v",
        f"{tmp_path / 'worktree'}:/workspace:ro",
        "-v",
        (
            f"{tmp_path / 'worktree' / 'schemas' / 'grid-sample-attribution-receipt.schema.json'}"
            ":/opt/val/schemas/grid-sample-attribution-receipt.schema.json:ro"
        ),
        "-v",
        f"{audit}:/audit:ro",
        image_id,
        "/workspace/scripts/run_wave0_a7_cpu_microcheck.py",
        "--workspace-root",
        "/workspace",
        "--source-inventory",
        "/audit/21-a7-source-inventory.json",
    ]
    argv_audit = audit / "19-image-build-argv.json"
    argv_audit.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "run_id": _RUN_ID,
                "source_commit": _SOURCE,
                "argv": build_argv,
                "recorded_before_build": True,
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    build_stdout = audit / "20-image-build.stdout.log"
    build_stderr = audit / "20-image-build.stderr.log"
    build_stdout.write_text("", encoding="utf-8")
    build_stderr.write_text("", encoding="utf-8")
    source_inventory = audit / "21-a7-source-inventory.json"
    source_inventory.write_text(
        json.dumps(
            {"schema_version": 1, "source_commit": _SOURCE, "files": []},
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    payload_document = _microcheck_payload(_sha256(source_inventory))
    payload_text = json.dumps(payload_document, separators=(",", ":"))
    payload = audit / "22-a7-cpu-micro-check-payload.json"
    payload.write_text(payload_text, encoding="utf-8")
    micro_stdout = audit / "22-a7-cpu-micro-check.stdout.log"
    micro_stderr = audit / "22-a7-cpu-micro-check.stderr.log"
    micro_stdout.write_text(payload_text + "\n", encoding="utf-8")
    micro_stderr.write_text("", encoding="utf-8")
    started = "2026-08-26T12:00:00.0000000+00:00"
    completed = "2026-08-26T12:00:01.0000000+00:00"
    build_document = {
        "schema_version": 1,
        "owner_authorization_id": "owner-a7-fixture",
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "branch": "codex/fixture",
        "image_tag": _TAG,
        "image_id": image_id,
        "base_image_digest": _BASE,
        "argv": build_argv,
        "augmented_baseline_path": str(baseline),
        "augmented_baseline_sha256": _sha256(baseline),
        "argv_audit_path": str(argv_audit),
        "argv_audit_sha256": _sha256(argv_audit),
        "stdout_path": str(build_stdout),
        "stdout_sha256": _sha256(build_stdout),
        "stderr_path": str(build_stderr),
        "stderr_sha256": _sha256(build_stderr),
        "exit_code": 0,
        "started_at": started,
        "completed_at": completed,
    }
    microcheck_document = {
        "schema_version": 1,
        "owner_authorization_id": "owner-a7-fixture",
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "branch": "codex/fixture",
        "image_tag": _TAG,
        "image_id": image_id,
        "base_image_digest": _BASE,
        "augmented_baseline_path": str(baseline),
        "augmented_baseline_sha256": _sha256(baseline),
        "source_inventory_path": str(source_inventory),
        "source_inventory_sha256": _sha256(source_inventory),
        "payload_path": str(payload),
        "payload_sha256": _sha256(payload),
        "payload": payload_document,
        "docker_argv": microcheck_argv,
        "stdout_path": str(micro_stdout),
        "stdout_sha256": _sha256(micro_stdout),
        "stderr_path": str(micro_stderr),
        "stderr_sha256": _sha256(micro_stderr),
        "exit_code": 0,
        "started_at": started,
        "completed_at": completed,
    }
    build = audit / "20-image-build-result.json"
    microcheck = audit / "22-a7-cpu-micro-check.json"
    build.write_text(
        json.dumps(build_document, separators=(",", ":")), encoding="utf-8"
    )
    microcheck.write_text(
        json.dumps(microcheck_document, separators=(",", ":")),
        encoding="utf-8",
    )
    model_cache_root = campaign / "cache-preflight" / "wave0" / "model_cache"
    model_cache_root.mkdir(parents=True)
    model_cache_receipts = campaign / "cache-preflight" / "wave0" / "receipts"
    model_cache_receipts.mkdir()
    empty_sha = hashlib.sha256(b"").hexdigest()
    locks = {
        f".cache/huggingface/download/{filename}.lock": {
            "size": 0,
            "sha256": empty_sha,
        }
        for filename in (
            "README.md",
            "config.json",
            "model.safetensors",
            "preprocessor_config.json",
        )
    }
    model_cache_models = {
        "rtdetr": {
            "name": "rtdetr",
            "repo_id": "PekingU/rtdetr_r18vd",
            "revision": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
            "huggingface_metadata": {
                "commit_hash": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
                "inventory": locks,
            },
        },
        "dinov2": {
            "name": "dinov2",
            "repo_id": "facebook/dinov2-small",
            "revision": "ed25f3a31f01632728cabb09d1542f84ab7b0056",
            "huggingface_metadata": {
                "commit_hash": "ed25f3a31f01632728cabb09d1542f84ab7b0056",
                "inventory": locks,
            },
        },
    }
    model_cache_receipt = model_cache_receipts / "model-assets.json"
    model_cache_receipt.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "receipt_type": "model-assets",
                "normative": {
                    "status": "PASS",
                    "errors": [],
                    "models": model_cache_models,
                },
                "metadata": {"run_id": _RUN_ID},
            },
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    model_cache_stdout = audit / "23-a7-model-cache-preflight.stdout.log"
    model_cache_stderr = audit / "23-a7-model-cache-preflight.stderr.log"
    model_cache_stdout.write_text("PASS\n", encoding="utf-8")
    model_cache_stderr.write_text("", encoding="utf-8")
    model_cache_argv = [
        "docker",
        "run",
        "--rm",
        "--network",
        "bridge",
        "--workdir",
        "/workspace",
        "--entrypoint",
        "val",
        "-e",
        "VAL_ARTIFACT_ROOT=/artifacts",
        "-e",
        "PYTHONPATH=/workspace/src",
        "-e",
        "HF_HUB_DISABLE_PROGRESS_BARS=1",
        "-e",
        "HF_HUB_VERBOSITY=error",
        "-v",
        f"{tmp_path / 'worktree'}:/workspace:ro",
        "-v",
        f"{campaign / 'cache-preflight'}:/artifacts:rw",
        image_id,
        "assets",
        "verify",
        "--config",
        "/workspace/configs/models/pinned-models.yaml",
        "--cache-root",
        "/artifacts/wave0/model_cache",
        "--output",
        "/artifacts/wave0/receipts/model-assets.json",
        "--run-id",
        _RUN_ID,
        "--download",
    ]
    model_cache_document = {
        "schema_version": 1,
        "owner_authorization_id": "owner-a7-fixture",
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "branch": "codex/fixture",
        "image_tag": _TAG,
        "image_id": image_id,
        "base_image_digest": _BASE,
        "augmented_baseline_path": str(baseline),
        "augmented_baseline_sha256": _sha256(baseline),
        "docker_argv": model_cache_argv,
        "network": "bridge",
        "gpu_enabled": False,
        "cache_root": str(model_cache_root),
        "receipt_path": str(model_cache_receipt),
        "receipt_sha256": _sha256(model_cache_receipt),
        "receipt_models": model_cache_models,
        "stdout_path": str(model_cache_stdout),
        "stdout_sha256": _sha256(model_cache_stdout),
        "stderr_path": str(model_cache_stderr),
        "stderr_sha256": _sha256(model_cache_stderr),
        "exit_code": 0,
        "started_at": started,
        "completed_at": completed,
    }
    model_cache_audit = audit / "23-a7-model-cache-preflight.json"
    model_cache_audit.write_text(
        json.dumps(model_cache_document, separators=(",", ":")),
        encoding="utf-8",
    )
    return {
        "audit": audit,
        "baseline": baseline,
        "build": build,
        "build_argv": build_argv,
        "build_document": build_document,
        "campaign": campaign,
        "image_id": image_id,
        "lease": tmp_path / "lease.json",
        "microcheck": microcheck,
        "microcheck_argv": microcheck_argv,
        "microcheck_document": microcheck_document,
        "model_cache_root": model_cache_root,
        "model_cache_audit": model_cache_audit,
        "model_cache_audit_hash": _sha256(model_cache_audit),
        "model_cache_audit_document": model_cache_document,
        "model_cache_receipt": model_cache_receipt,
        "model_cache_receipt_hash": _sha256(model_cache_receipt),
        "model_cache_argv": model_cache_argv,
        "payload": payload,
        "payload_text": payload_text,
    }


def _rewrite_closed_audit(fixture: dict[str, object], kind: str) -> None:
    path = Path(fixture[kind])
    path.write_text(
        json.dumps(fixture[f"{kind}_document"], separators=(",", ":")),
        encoding="utf-8",
    )


def _mutate_closed_audit(fixture: dict[str, object], kind: str, mutation: str) -> None:
    document = fixture[f"{kind}_document"]
    if mutation == "missing_field":
        document.pop("owner_authorization_id")
    elif mutation == "extra_field":
        document["unapproved"] = True
    elif mutation == "wrong_identity":
        document["source_commit"] = "f" * 40
    elif mutation == "wrong_path":
        document["stdout_path"] = str(Path(fixture["audit"]) / "wrong.log")
    elif mutation == "changed_log_hash":
        document["stdout_sha256"] = "f" * 64
    elif mutation == "changed_argv":
        field = "argv" if kind == "build" else "docker_argv"
        document[field] = [*document[field], "--unapproved"]
    elif mutation == "nonzero_exit":
        document["exit_code"] = 9
    elif mutation == "malformed_timestamp":
        document["completed_at"] = "tomorrow"
    elif mutation == "changed_payload_hash":
        assert kind == "microcheck"
        document["payload_sha256"] = "f" * 64
    _rewrite_closed_audit(fixture, kind)


def _closed_audit_lease_body(fixture: dict[str, object]) -> str:
    return f"""
$Result = New-A7Lease `
    -LeasePath {_powershell_literal(str(fixture['lease']))} `
    -OwnerAuthorizationId 'owner-a7-fixture' `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -Branch 'codex/fixture' `
    -ImageTag {_powershell_literal(_TAG)} `
    -ImageId {_powershell_literal(str(fixture['image_id']))} `
    -BaseImageDigest {_powershell_literal(_BASE)} `
    -GpuUuid 'GPU-12345678' `
    -CampaignRoot {_powershell_literal(str(fixture['campaign']))} `
    -HistoricalBaselinePath {_powershell_literal(str(fixture['baseline']))} `
    -HistoricalBaselineSha256 {_powershell_literal(_sha256(Path(fixture['baseline'])))} `
    -BuildAuditPath {_powershell_literal(str(fixture['build']))} `
    -BuildAuditSha256 {_powershell_literal(_sha256(Path(fixture['build'])))} `
    -MicrocheckAuditPath {_powershell_literal(str(fixture['microcheck']))} `
    -MicrocheckAuditSha256 {_powershell_literal(_sha256(Path(fixture['microcheck'])))} `
    -ModelCacheRoot {_powershell_literal(str(fixture['model_cache_root']))} `
    -ModelCachePreflightAuditPath {_powershell_literal(str(fixture['model_cache_audit']))} `
    -ModelCachePreflightAuditSha256 {_powershell_literal(_sha256(Path(fixture['model_cache_audit'])))} `
    -ModelCacheReceiptPath {_powershell_literal(str(fixture['model_cache_receipt']))} `
    -ModelCacheReceiptSha256 {_powershell_literal(_sha256(Path(fixture['model_cache_receipt'])))} `
    -HostProcessesJson '[]' `
    -ContainersJson '[]' `
    -ClaimedAt '2026-08-26T12:00:02.0000000Z'
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def _task7_audit_binding_body(fixture: dict[str, object]) -> str:
    lease = {
        "owner_authorization_id": "owner-a7-fixture",
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "branch": "codex/fixture",
        "image_tag": _TAG,
        "image_id": fixture["image_id"],
        "base_image_digest": _BASE,
        "historical_baseline_path": str(fixture["baseline"]),
        "historical_baseline_sha256": _sha256(Path(fixture["baseline"])),
        "build_audit_sha256": _sha256(Path(fixture["build"])),
        "microcheck_audit_sha256": _sha256(Path(fixture["microcheck"])),
        "model_cache_root": str(fixture["model_cache_root"]),
        "model_cache_preflight_audit_path": str(fixture["model_cache_audit"]),
        "model_cache_preflight_audit_sha256": _sha256(
            Path(fixture["model_cache_audit"])
        ),
        "model_cache_receipt_path": str(fixture["model_cache_receipt"]),
        "model_cache_receipt_sha256": _sha256(Path(fixture["model_cache_receipt"])),
    }
    return f"""
$AuditRoot = {_powershell_literal(str(fixture['audit']))}
$Lease = {_powershell_literal(json.dumps(lease))} | ConvertFrom-Json
$Binding = Test-Task7AuditBinding
$Binding | ConvertTo-Json -Depth 8 -Compress
"""


def test_build_audit_and_microcheck_audit_are_closed_in_controlled_launch(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    audit = Path(fixture["campaign"]) / "audit"
    build = json.loads(
        (audit / "20-image-build-result.json").read_text(encoding="utf-8")
    )
    microcheck = json.loads(
        (audit / "22-a7-cpu-micro-check.json").read_text(encoding="utf-8")
    )
    model_cache = json.loads(
        (audit / "23-a7-model-cache-preflight.json").read_text(encoding="utf-8")
    )
    payload_path = audit / "22-a7-cpu-micro-check-payload.json"
    stdout_line = (
        (audit / "22-a7-cpu-micro-check.stdout.log")
        .read_text(encoding="utf-8")
        .splitlines()[0]
    )
    assert set(build) == _BUILD_AUDIT_FIELDS
    assert set(microcheck) == _MICROCHECK_AUDIT_FIELDS
    assert set(model_cache) == _MODEL_CACHE_AUDIT_FIELDS
    assert payload_path.read_bytes() == stdout_line.encode("utf-8")
    assert microcheck["payload"] == json.loads(stdout_line)


def test_audit_binding_gpu_lease_accepts_closed_task7_audits(tmp_path: Path) -> None:
    fixture = _closed_audit_fixture(tmp_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"), _closed_audit_lease_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    assert Path(fixture["lease"]).is_file()


def test_gpu_lease_parseback_rejects_an_extra_property(tmp_path: Path) -> None:
    fixture = _closed_audit_fixture(tmp_path)
    body = f"""
Remove-Item Function:Write-A7NewText
function Write-A7NewText {{
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Document = $Text | ConvertFrom-Json
    $Document | Add-Member -NotePropertyName unexpected -NotePropertyValue $true
    [IO.File]::WriteAllText(
        $Path,
        ($Document | ConvertTo-Json -Depth 8 -Compress),
        [Text.UTF8Encoding]::new($false)
    )
}}
{_closed_audit_lease_body(fixture)}
"""

    completed = _invoke_functions(("Write-A7NewText", "New-A7Lease"), body)

    assert completed.returncode != 0
    assert "property inventory mismatch" in completed.stderr


def test_audit_binding_gpu_lease_accepts_regular_files_under_strict_mode(
    tmp_path: Path,
) -> None:
    fixture = _closed_audit_fixture(tmp_path)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"),
        "Set-StrictMode -Version Latest\n" + _closed_audit_lease_body(fixture),
    )

    assert completed.returncode == 0, completed.stderr
    assert Path(fixture["lease"]).is_file()


@pytest.mark.parametrize("kind", ["build", "microcheck"])
@pytest.mark.parametrize(
    "mutation",
    [
        "missing_field",
        "extra_field",
        "wrong_identity",
        "wrong_path",
        "changed_log_hash",
        "changed_argv",
        "nonzero_exit",
        "malformed_timestamp",
        "changed_payload_hash",
    ],
)
def test_audit_binding_gpu_lease_rejects_mutated_task7_audits(
    tmp_path: Path, kind: str, mutation: str
) -> None:
    if mutation == "changed_payload_hash" and kind == "build":
        pytest.skip("payload belongs only to the micro-check audit")
    fixture = _closed_audit_fixture(tmp_path)
    _mutate_closed_audit(fixture, kind, mutation)

    completed = _invoke_functions(
        ("Write-A7NewText", "New-A7Lease"), _closed_audit_lease_body(fixture)
    )

    assert completed.returncode != 0
    assert not Path(fixture["lease"]).exists()


def test_task8_accepts_closed_task7_binding_audits(tmp_path: Path) -> None:
    fixture = _closed_audit_fixture(tmp_path)

    completed = _invoke_runner_functions(
        ("Test-Task7AuditBinding",), _task7_audit_binding_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "model_cache_root": str(fixture["model_cache_root"])
    }


@pytest.mark.parametrize(
    "mutation",
    (
        "missing",
        "extra",
        "reordered",
        "wrong_progress_value",
        "wrong_verbosity_value",
        "token_added",
    ),
)
def test_task8_rejects_mutated_hf_logging_environment(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _closed_audit_fixture(tmp_path)
    argv = fixture["model_cache_audit_document"]["docker_argv"]
    if mutation == "missing":
        del argv[13:15]
    elif mutation == "extra":
        argv[17:17] = ["-e", "HF_HUB_DISABLE_PROGRESS_BARS=1"]
    elif mutation == "reordered":
        argv[13:17] = argv[15:17] + argv[13:15]
    elif mutation == "wrong_progress_value":
        argv[14] = "HF_HUB_DISABLE_PROGRESS_BARS=0"
    elif mutation == "wrong_verbosity_value":
        argv[16] = "HF_HUB_VERBOSITY=warning"
    elif mutation == "token_added":
        argv[17:17] = ["-e", "HF_TOKEN=forbidden"]
    _rewrite_closed_audit(fixture, "model_cache_audit")

    completed = _invoke_runner_functions(
        ("Test-Task7AuditBinding",), _task7_audit_binding_body(fixture)
    )

    assert completed.returncode != 0
    assert "Task 7 model-cache Docker argv binding mismatch" in completed.stderr


def test_task8_binding_returns_verified_run_scoped_model_cache(
    tmp_path: Path,
) -> None:
    fixture = _closed_audit_fixture(tmp_path)

    completed = _invoke_runner_functions(
        ("Test-Task7AuditBinding",), _task7_audit_binding_body(fixture)
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {"model_cache_root": str(fixture["model_cache_root"])}


def test_task8_accepts_regular_audit_files_under_strict_mode(tmp_path: Path) -> None:
    fixture = _closed_audit_fixture(tmp_path)

    completed = _invoke_runner_functions(
        ("Test-Task7AuditBinding",),
        "Set-StrictMode -Version Latest\n" + _task7_audit_binding_body(fixture),
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "model_cache_root": str(fixture["model_cache_root"])
    }


def test_task8_derives_run_scoped_release_evidence_paths(tmp_path: Path) -> None:
    lease = tmp_path / "leases" / "GPU-12345678.json"
    expected_released = lease.parent / f"{_RUN_ID}.released"
    expected_record = lease.parent / f"{_RUN_ID}.release.json"

    completed = _invoke_runner_functions(
        ("Get-A7LeaseReleasePaths",),
        f"""
$Paths = Get-A7LeaseReleasePaths `
    -ActivePath {_powershell_literal(str(lease))} `
    -RunId {_powershell_literal(_RUN_ID)}
$Paths | ConvertTo-Json -Compress
""",
    )

    assert completed.returncode == 0, completed.stderr
    paths = json.loads(completed.stdout)
    assert paths == {
        "released": str(expected_released),
        "release_record": str(expected_record),
    }


@pytest.mark.parametrize("linked_kind", ("released", "record"))
def test_task7_rejects_linked_release_evidence(
    tmp_path: Path, linked_kind: str
) -> None:
    leases = tmp_path / "leases"
    leases.mkdir()
    active = leases / "GPU-12345678.json"
    lease_document = {
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "image_id": f"sha256:{'d' * 64}",
    }
    active.write_text(json.dumps(lease_document), encoding="utf-8")
    lease_sha256 = _sha256(active)
    released_target = tmp_path / "released-target.json"
    active.replace(released_target)
    record_document = {
        "schema_version": 1,
        "run_id": _RUN_ID,
        "source_commit": _SOURCE,
        "image_digest": f"sha256:{'d' * 64}",
        "released_at": "2026-08-27T12:34:56.0000000Z",
        "original_lease_sha256": lease_sha256,
    }
    record_target = tmp_path / "record-target.json"
    record_target.write_text(json.dumps(record_document), encoding="utf-8")
    released = leases / f"{_RUN_ID}.released"
    record = leases / f"{_RUN_ID}.release.json"
    try:
        if linked_kind == "released":
            released.symlink_to(released_target)
            record.write_bytes(record_target.read_bytes())
        else:
            released.write_bytes(released_target.read_bytes())
            record.symlink_to(record_target)
    except OSError as exc:
        pytest.skip(f"symlink creation unavailable: {exc}")
    body = f"""
Assert-A7LeaseReleaseEvidence `
    -ActivePath {_powershell_literal(str(active))} `
    -ReleasedPath {_powershell_literal(str(released))} `
    -RecordPath {_powershell_literal(str(record))} `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -ImageDigest 'sha256:{'d' * 64}'
"""

    completed = _invoke_functions(
        ("Get-A7LeaseReleasePaths", "Assert-A7LeaseReleaseEvidence"), body
    )

    assert completed.returncode != 0


@pytest.mark.parametrize("kind", ["build", "microcheck"])
@pytest.mark.parametrize(
    "mutation",
    [
        "missing_field",
        "extra_field",
        "wrong_identity",
        "wrong_path",
        "changed_log_hash",
        "changed_argv",
        "nonzero_exit",
        "malformed_timestamp",
        "changed_payload_hash",
    ],
)
def test_task8_audit_binding_rejects_mutated_task7_audits(
    tmp_path: Path, kind: str, mutation: str
) -> None:
    if mutation == "changed_payload_hash" and kind == "build":
        pytest.skip("payload belongs only to the micro-check audit")
    fixture = _closed_audit_fixture(tmp_path)
    _mutate_closed_audit(fixture, kind, mutation)

    completed = _invoke_runner_functions(
        ("Test-Task7AuditBinding",), _task7_audit_binding_body(fixture)
    )

    assert completed.returncode != 0
    assert not Path(fixture["lease"]).exists()


def test_microcheck_invocation_is_cpu_networkless_and_before_gpu_lease(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    docker_state = json.loads(Path(fixture["docker_state"]).read_text(encoding="utf-8"))
    task8_state = json.loads(Path(fixture["task8_state"]).read_text(encoding="utf-8"))
    assert result["state"] == "CLOSED"
    assert result["validation_status"] == "PASSED"
    assert docker_state["build_count"] == 1
    assert docker_state["microcheck_count"] == 1
    run_argv = next(
        command for command in docker_state["commands"] if command[0] == "run"
    )
    assert run_argv[:7] == [
        "run",
        "--rm",
        "--network",
        "none",
        "--workdir",
        "/workspace",
        "--entrypoint",
    ]
    assert "python" in run_argv
    assert "--gpus" not in run_argv
    assert "VAL_DATA_ROOT" not in " ".join(run_argv)
    assert "pytest" not in run_argv
    assert not any(value.startswith("/workspace/tests") for value in run_argv)
    expected_schema_mount = (
        f"{_ROOT / 'schemas' / 'grid-sample-attribution-receipt.schema.json'}"
        ":/opt/val/schemas/grid-sample-attribution-receipt.schema.json:ro"
    )
    assert run_argv.count(expected_schema_mount) == 1
    assert task8_state["task8_count"] == 1
    assert task8_state["task8_argv"] == [
        "-RunId",
        _RUN_ID,
        "-ImageTag",
        _TAG,
        "-ImageDigest",
        f"sha256:{'d' * 64}",
        "-HostCampaignRoot",
        str(fixture["campaign"]),
        "-LeasePath",
        str(fixture["lease"]),
    ]
    assert not Path(fixture["lease"]).exists()
    assert (Path(fixture["lease"]).parent / f"{_RUN_ID}.released").is_file()


def test_model_cache_preflight_runs_once_between_microcheck_and_gpu_lease(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    docker_state = json.loads(Path(fixture["docker_state"]).read_text(encoding="utf-8"))
    run_commands = [
        command for command in docker_state["commands"] if command[0] == "run"
    ]
    assert docker_state["microcheck_count"] == 1
    assert docker_state["model_cache_preflight_count"] == 1
    assert len(run_commands) == 2
    assert run_commands[0][run_commands[0].index("--network") + 1] == "none"
    assert run_commands[0][run_commands[0].index("--entrypoint") + 1] == "python"
    assert run_commands[1][run_commands[1].index("--network") + 1] == "bridge"
    assert run_commands[1][run_commands[1].index("--entrypoint") + 1] == "val"
    assert "--gpus" not in run_commands[1]
    audit = Path(fixture["campaign"]) / "audit"
    cache_audit = audit / "23-a7-model-cache-preflight.json"
    assert cache_audit.is_file()
    released = Path(fixture["lease"]).parent / f"{_RUN_ID}.released"
    lease = json.loads(released.read_text(encoding="utf-8"))
    assert lease["model_cache_root"] == str(
        Path(fixture["campaign"]) / "cache-preflight" / "wave0" / "model_cache"
    )
    assert lease["model_cache_preflight_audit_path"] == str(cache_audit)
    assert lease["model_cache_preflight_audit_sha256"] == _sha256(cache_audit)
    assert lease["model_cache_receipt_sha256"] == _sha256(
        Path(lease["model_cache_receipt_path"])
    )
    source = _LAUNCHER.read_text(encoding="utf-8")
    assert (
        source.index("$Stage = 'model_cache_preflight'")
        < source.index("$Stage = 'gpu_lease'")
        < source.index("$Stage = 'task8'")
    )


def test_previous_fixed_gpu_release_evidence_does_not_block_fresh_run(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path)
    lease = Path(fixture["lease"])
    previous_released = Path(str(lease) + ".released")
    previous_record = Path(str(lease) + ".release.json")
    previous_released.write_text("preserved released lease", encoding="utf-8")
    previous_record.write_text("preserved release record", encoding="utf-8")

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    assert previous_released.read_text(encoding="utf-8") == "preserved released lease"
    assert previous_record.read_text(encoding="utf-8") == "preserved release record"
    assert (lease.parent / f"{_RUN_ID}.released").is_file()
    assert (lease.parent / f"{_RUN_ID}.release.json").is_file()


@pytest.mark.parametrize("suffix", [".released", ".release.json"])
def test_existing_run_scoped_release_destination_fails_before_claim(
    tmp_path: Path,
    suffix: str,
) -> None:
    fixture = _launch_fixture(tmp_path)
    destination = Path(fixture["lease"]).parent / f"{_RUN_ID}{suffix}"
    destination.write_text("occupied", encoding="utf-8")

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode != 0
    assert destination.read_text(encoding="utf-8") == "occupied"
    assert not Path(fixture["campaign"]).exists()
    assert not Path(fixture["docker_state"]).exists()
    assert not Path(fixture["task8_state"]).exists()


@pytest.mark.parametrize(
    "mode",
    [
        "build_fail",
        "inspect_wrong",
        "micro_blank",
        "micro_multiple",
        "micro_malformed",
        "micro_cuda",
        "micro_wrong_source",
        "cache_exit",
        "cache_stdout",
        "cache_stderr",
        "cache_missing_receipt",
        "cache_malformed_receipt",
        "cache_fail_receipt",
        "cache_wrong_run",
        "cache_wrong_revision",
        "cache_missing_lock",
        "cache_nonzero_lock",
        "cache_extra_lock",
    ],
)
def test_transition_failure_closes_without_gpu_or_task8_retry(
    tmp_path: Path, mode: str
) -> None:
    fixture = _launch_fixture(tmp_path, mode=mode)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    state = json.loads(Path(fixture["docker_state"]).read_text(encoding="utf-8"))
    assert result["state"] == "CLOSED"
    assert not Path(fixture["lease"]).exists()
    assert not Path(fixture["task8_state"]).exists()
    assert state["build_count"] == 1
    assert state["microcheck_count"] <= 1
    assert state["model_cache_preflight_count"] <= 1
    assert (
        Path(fixture["campaign"]) / "audit" / "51-campaign-closure-manifest.json"
    ).is_file()


def test_task8_nonzero_with_complete_evidence_remains_a_valid_closed_result(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path, mode="task8_valid_nonzero")

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    task8_state = json.loads(Path(fixture["task8_state"]).read_text(encoding="utf-8"))
    assert task8_state["task8_count"] == 1
    assert result["task8_exit_code"] == 9
    assert result["terminal"].endswith("WAVE1_FORBIDDEN")
    audit = Path(fixture["campaign"]) / "audit"
    assert not (audit / "52-task7-post-task8-validation-failure.json").exists()
    assert not (audit / "53-task7-post-task8-validation-closure.json").exists()


@pytest.mark.parametrize(
    "mode",
    [
        "task8_missing_30",
        "task8_missing_40",
        "task8_missing_41",
        "task8_missing_51",
        "task8_malformed_result",
        "task8_malformed_closure",
        "task8_terminal_mismatch",
        "task8_hash_drift",
        "task8_active_lease",
        "task8_missing_release",
        "task8_missing_release_record",
        "task8_release_hash_mismatch",
        "task8_release_wrong_run",
        "task8_release_wrong_source",
        "task8_release_wrong_image",
        "task8_release_extra_field",
        "task8_release_bad_timestamp",
    ],
)
def test_post_task8_validation_failure_uses_only_52_53_evidence(
    tmp_path: Path, mode: str
) -> None:
    fixture = _launch_fixture(tmp_path, mode=mode)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    state = json.loads(Path(fixture["task8_state"]).read_text(encoding="utf-8"))
    assert state["task8_count"] == 1
    audit = Path(fixture["campaign"]) / "audit"
    failure_path = audit / "52-task7-post-task8-validation-failure.json"
    closure_path = audit / "53-task7-post-task8-validation-closure.json"
    assert failure_path.is_file()
    assert closure_path.is_file()
    failure = json.loads(failure_path.read_text(encoding="utf-8"))
    closure = json.loads(closure_path.read_text(encoding="utf-8"))
    assert set(failure) == {
        "schema_version",
        "owner_authorization_id",
        "run_id",
        "source_commit",
        "spec_commit",
        "plan_commit",
        "image_tag",
        "image_id",
        "campaign_root",
        "task8_exit_code",
        "observed_terminal",
        "validation_error",
        "required_files",
        "lease_state",
        "pre_publication_files",
        "recorded_at",
    }
    assert set(closure) == {
        *set(failure),
        "status",
        "failure_record",
    }
    assert set(failure["lease_state"]) == {"active", "released", "release_record"}
    assert all(
        set(record) in ({"path", "exists"}, {"path", "exists", "size", "sha256"})
        for record in failure["required_files"]
    )
    assert result["task8_invocation_count"] == 1
    assert result["validation_status"] == "FAILED"
    assert closure["status"] == "POST_TASK8_VALIDATION_FAILED"
    assert closure["failure_record"] == {
        "path": "audit/52-task7-post-task8-validation-failure.json",
        "size": failure_path.stat().st_size,
        "sha256": _sha256(failure_path),
    }
    before = {
        record["path"]: record for record in state["task8_owned_before_validation"]
    }
    for relative_path, record in before.items():
        path = audit / relative_path
        assert path.stat().st_size == record["size"]
        assert _sha256(path) == record["sha256"]
    if mode == "task8_active_lease":
        assert Path(fixture["lease"]).is_file()
        assert failure["lease_state"]["active"]["exists"] is True


@pytest.mark.parametrize(
    ("mode", "name", "content"),
    [
        (
            "task8_preexisting_52",
            "52-task7-post-task8-validation-failure.json",
            "occupied-52",
        ),
        (
            "task8_preexisting_53",
            "53-task7-post-task8-validation-closure.json",
            "occupied-53",
        ),
    ],
)
def test_post_task8_existing_52_53_fails_without_clobber_or_retry(
    tmp_path: Path, mode: str, name: str, content: str
) -> None:
    fixture = _launch_fixture(tmp_path, mode=mode)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode != 0
    state = json.loads(Path(fixture["task8_state"]).read_text(encoding="utf-8"))
    assert state["task8_count"] == 1
    destination = Path(fixture["campaign"]) / "audit" / name
    assert destination.read_text(encoding="utf-8") == content


def test_launcher_exit_code_fails_closed_on_post_task8_validation_failure() -> None:
    body = """
$Results = @(
    Get-A7ProductionExitCode -Result ([pscustomobject]@{
        validation_status = 'FAILED'
        task8_exit_code = 0
    })
    Get-A7ProductionExitCode -Result ([pscustomobject]@{
        validation_status = 'PASSED'
        task8_exit_code = 7
    })
    Get-A7ProductionExitCode -Result ([pscustomobject]@{
        task8_exit_code = $null
    })
)
$Results | ConvertTo-Json -Compress
"""

    completed = _invoke_functions(("Get-A7ProductionExitCode",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [2, 7, 2]


def test_transition_preclaim_existing_campaign_leaves_image_and_lease_unclaimed(
    tmp_path: Path,
) -> None:
    fixture = _launch_fixture(tmp_path)
    Path(fixture["campaign"]).mkdir(parents=True)

    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))

    assert completed.returncode != 0
    assert not Path(fixture["docker_state"]).exists()
    assert not Path(fixture["lease"]).exists()


def test_launcher_top_level_invokes_production_once() -> None:
    body = f"""
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {_powershell_literal(str(_LAUNCHER))}, [ref]$Tokens, [ref]$Errors
)
if ($Errors.Count -ne 0) {{ throw 'parse failure' }}
$Calls = @($Ast.FindAll({{
    param($Node)
    if ($Node -isnot [Management.Automation.Language.CommandAst]) {{ return $false }}
    if ($Node.GetCommandName() -cne 'Invoke-A7Production') {{ return $false }}
    $Parent = $Node.Parent
    while ($null -ne $Parent) {{
        if ($Parent -is [Management.Automation.Language.FunctionDefinitionAst]) {{ return $false }}
        $Parent = $Parent.Parent
    }}
    return $true
}}, $true))
$Calls.Count
"""
    completed = subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", body],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "1"


def _write_model_cache_preflight_adapter(path: Path) -> None:
    path.write_text(
        """import hashlib
import json
import sys
from pathlib import Path

args = list(sys.argv[1:])
if args[:1] != ["--state"] or len(args) < 3:
    raise SystemExit(90)
state_path = Path(args[1])
command = args[2:]
state_path.write_text(json.dumps({"argv": command}), encoding="utf-8")
mount = next(value for value in command if value.endswith(":/artifacts:rw"))
artifact_root = Path(mount[: -len(":/artifacts:rw")])
cache_root = artifact_root / "wave0" / "model_cache"
receipt_path = artifact_root / "wave0" / "receipts" / "model-assets.json"
empty_sha = hashlib.sha256(b"").hexdigest()
models = {}
for name, repo_id, revision in (
    ("rtdetr", "PekingU/rtdetr_r18vd", "cc5b50f32f0100caaa3bd275343e2fb17762c73d"),
    ("dinov2", "facebook/dinov2-small", "ed25f3a31f01632728cabb09d1542f84ab7b0056"),
):
    inventory = {}
    for filename in ("README.md", "config.json", "model.safetensors", "preprocessor_config.json"):
        lock_rel = f".cache/huggingface/download/{filename}.lock"
        inventory[lock_rel] = {"size": 0, "sha256": empty_sha}
    models[name] = {
        "name": name,
        "repo_id": repo_id,
        "revision": revision,
        "huggingface_metadata": {
            "commit_hash": revision,
            "inventory": inventory,
        },
    }
receipt = {
    "schema_version": 1,
    "receipt_type": "model-assets",
    "normative": {
        "status": "PASS",
        "errors": [],
        "invariants": {
            "all_assets_verified": True,
            "apache_2_0_licenses": True,
            "data_root_unset": True,
            "exact_file_inventory": True,
            "exact_huggingface_metadata": True,
            "exact_revisions": True,
            "exact_transformers_source": True,
        },
        "models": models,
    },
    "metadata": {"run_id": "wave0-a7-20260826T120000000Z"},
}
receipt_path.write_text(json.dumps(receipt, separators=(",", ":")), encoding="utf-8")
print("PASS")
""",
        encoding="utf-8",
    )


def test_model_cache_preflight_is_networked_cpu_only_and_audited(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    audit.mkdir(parents=True)
    worktree = tmp_path / "worktree"
    (worktree / "configs").mkdir(parents=True)
    (worktree / "configs" / "models").mkdir(parents=True)
    (worktree / "configs" / "models" / "pinned-models.yaml").write_text("models: {}\n")
    baseline = tmp_path / "baseline.json"
    baseline.write_text('{"baseline":true}', encoding="utf-8")
    adapter = tmp_path / "model_cache_adapter.py"
    state = tmp_path / "model_cache_state.json"
    _write_model_cache_preflight_adapter(adapter)
    body = f"""
$Result = Invoke-A7ModelCachePreflight `
    -CampaignRoot {_powershell_literal(str(campaign))} `
    -AuditRoot {_powershell_literal(str(audit))} `
    -WorktreePath {_powershell_literal(str(worktree))} `
    -DockerExecutable {_powershell_literal(sys.executable)} `
    -DockerPrefixArguments @({_powershell_literal(str(adapter))},{_powershell_literal('--state')},{_powershell_literal(str(state))}) `
    -OwnerAuthorizationId 'owner-a8-fixture' `
    -RunId {_powershell_literal(_RUN_ID)} `
    -SourceCommit {_powershell_literal(_SOURCE)} `
    -SpecCommit {_powershell_literal(_SPEC)} `
    -PlanCommit {_powershell_literal(_PLAN)} `
    -Branch 'codex/fixture' `
    -ImageTag {_powershell_literal(_TAG)} `
    -ImageId 'sha256:{'d' * 64}' `
    -BaseImageDigest {_powershell_literal(_BASE)} `
    -HistoricalBaselinePath {_powershell_literal(str(baseline))} `
    -HistoricalBaselineSha256 {_powershell_literal(_sha256(baseline))}
$Result | ConvertTo-Json -Depth 8 -Compress
"""

    completed = _invoke_functions(
        ("Write-A7NewText", "Invoke-A7Native", "Invoke-A7ModelCachePreflight"),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    argv = json.loads(state.read_text(encoding="utf-8"))["argv"]
    assert argv[:8] == [
        "run",
        "--rm",
        "--network",
        "bridge",
        "--workdir",
        "/workspace",
        "--entrypoint",
        "val",
    ]
    assert "--gpus" not in argv
    assert "VAL_DATA_ROOT" not in "\n".join(argv)
    assert "HF_HUB_OFFLINE" not in "\n".join(argv)
    assert "TRANSFORMERS_OFFLINE" not in "\n".join(argv)
    assert argv[12:16] == [
        "-e",
        "HF_HUB_DISABLE_PROGRESS_BARS=1",
        "-e",
        "HF_HUB_VERBOSITY=error",
    ]
    joined = "\n".join(argv)
    for forbidden in (
        "HF_TOKEN",
        "HUGGING_FACE_HUB_TOKEN",
        "HF_HOME",
        "--env-file",
        "--secret",
    ):
        assert forbidden not in joined
    assert argv[-11:] == [
        "assets",
        "verify",
        "--config",
        "/workspace/configs/models/pinned-models.yaml",
        "--cache-root",
        "/artifacts/wave0/model_cache",
        "--output",
        "/artifacts/wave0/receipts/model-assets.json",
        "--run-id",
        _RUN_ID,
        "--download",
    ]
    audit_path = Path(result["audit_path"])
    receipt_path = Path(result["receipt_path"])
    assert audit_path.is_file()
    assert receipt_path.is_file()
    assert result["audit_sha256"] == _sha256(audit_path)
    assert result["receipt_sha256"] == _sha256(receipt_path)
    document = json.loads(audit_path.read_text(encoding="utf-8"))
    assert document["docker_argv"] == ["docker", *argv]
    assert document["network"] == "bridge"
    assert document["gpu_enabled"] is False
    assert (
        document["receipt_models"]
        == json.loads(receipt_path.read_text(encoding="utf-8"))["normative"]["models"]
    )
    before = {
        "audit": audit_path.read_bytes(),
        "receipt": receipt_path.read_bytes(),
    }

    repeated = _invoke_functions(
        ("Write-A7NewText", "Invoke-A7Native", "Invoke-A7ModelCachePreflight"),
        body,
    )

    assert repeated.returncode != 0
    assert audit_path.read_bytes() == before["audit"]
    assert receipt_path.read_bytes() == before["receipt"]
