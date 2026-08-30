# Wave 0 A11 v14 Closure Line-Identity Recovery Implementation Plan

> **For Codex:** Execute with the `executing-plans` skill. This plan is
> already owner-approved for Inline Execution. Stop only on the first
> preserved NO_GO, a new external authorization boundary, or a newly required
> destructive action. Never retry the formal verifier invocation.

**Goal:** Preserve the successful v13 Stage 0 observation and failed v13
closure, then independently prove the exact four-space identity of the
preserved v11 controller line that the v13 closure compared incorrectly.

**Architecture:** One fresh ignored workspace contains one plan-pinned,
read-only PowerShell verifier. RED proves the frozen v13 zero-indent literal is
wrong. GREEN proves the v14 source has the corrected four-space literal and no
process/runtime/write topology. Read-only wrappers establish Git identity and
cleanliness before and after the verifier. The verifier is invoked exactly
once and emits one fresh v14 terminal; it never invokes v13.

**Tech stack:** Git, PowerShell 7.6.4, PowerShell AST, .NET UTF-8 and SHA-256.

## Frozen scope and identity records

```text
V14_PLAN_SUBJECT|docs: plan A11 closure line identity recovery
V14_DESIGN_COMMIT|032ae49d3c6e011726db47268d795ffea5e69fac
V14_DESIGN_BLOB|91a91ddb3f8e7e7e4b51841923712fc7ed3636ed
V14_DESIGN_IDENTITY|8130|8fed6373f6ff7d5b6f62e2ffdabe19f3ed859b6494d4349e24cc3249d0263f53
V13_PLAN_COMMIT|62fa510c335c24e6b8bec81083aa93339913b639
V13_PLAN_BLOB|f8da0fb7c166c95a97cef00d77bae4deab1cb99b
V13_PLAN_IDENTITY|129929|27f604a9adb716e788b3a135e8b6d695f05af55e7349f85a9e12c4b59200507c
V13_DESIGN_COMMIT|84b0f64fa5565d785e32fe3fbe5de1dc473f23aa
V13_DESIGN_BLOB|eb0260c4137cfc29bcefc3b410eb19cb88262a8c
V13_DESIGN_IDENTITY|11644|b6593dce24c5de790678c35c80b8105efebced71e8039d5a4e65b4dd3f1cc61c
PRESERVED_V13_OBSERVATION|controller_invocations=1|child_starts=1|retries=0|exit=0|stderr_bytes=0|stdout_lines=2|result=PASS
PRESERVED_V13_CLOSURE|closure_invocations=1|exception=closure v11 source line rejected|terminal=undefined|result=NO_GO
V11_CONTROLLER_IDENTITY|28071|e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9
V11_LINE_IDENTITY|171|4|142|1ef50cf9ad6633f4da88ea82c2ca16c7abd9864416ae38510806638b88a2fd2b
SOURCE_IDENTITY|task-1-v13-closure-line-identity-v14.ps1|10069|9ede25815ed9da79426cc06220c01a7af768f3ab20883e4453fa0d68fa88523d
```

The source identity values are independently re-derived before this plan is
committed. The committed plan must contain no unresolved template token.

## Frozen verifier source

<!-- SOURCE_BEGIN:task-1-v13-closure-line-identity-v14.ps1 -->
```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$PlanPath = 'docs\superpowers\plans\2026-08-31-val-wave0-a11-closure-line-identity-recovery.md'
$DesignPath = 'docs\superpowers\specs\2026-08-31-val-wave0-a11-closure-line-identity-recovery-design.md'
$V13PlanPath = 'docs\superpowers\plans\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery.md'
$V13DesignPath = 'docs\superpowers\specs\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery-design.md'
$Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-closure-line-identity-recovery'
$V13Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery'
$V12Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-31-val-wave0-a11-stage0-preflight-expression-recovery'
$V11Controller = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery\task-1-stage0-raw-byte-controller-v11.ps1'
$SourceName = 'task-1-v13-closure-line-identity-v14.ps1'
$ExpectedV11Line = '    if (Test-Path -LiteralPath $V8Workspace -or Test-Path -LiteralPath $ConsumedV6Workspace) { throw ''consumed predecessor namespace exists'' }'
$Terminal = 'ENTRYV14_CLOSURE_LINE_IDENTITY_PASS|v13_observation=preserved_pass|v13_closure=preserved_no_go|v11_line=171|leading_spaces=4|linked=clean|canonical=clean'
$Utf8 = [Text.UTF8Encoding]::new($false, $true)

function Get-A11V14Sha256 {
    param([Parameter(Mandatory)] [byte[]] $Bytes)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        [BitConverter]::ToString($Algorithm.ComputeHash($Bytes)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Algorithm.Dispose()
    }
}

function Get-A11V14FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    try {
        [BitConverter]::ToString($Algorithm.ComputeHash($Stream)).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Algorithm.Dispose()
        $Stream.Dispose()
    }
}

function Assert-A11V14OrdinaryFile {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [long] $ByteCount,
        [Parameter(Mandatory)] [string] $Sha256
    )
    $FullPath = [IO.Path]::GetFullPath($Path)
    if (-not [IO.Path]::IsPathFullyQualified($Path) -or -not [StringComparer]::OrdinalIgnoreCase.Equals($FullPath, $Path)) {
        throw 'file path identity rejected'
    }
    $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
    if ($Item.PSIsContainer -or [long]$Item.Length -ne $ByteCount -or ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
        throw 'ordinary file identity rejected'
    }
    if (-not [string]::IsNullOrEmpty([string]$Item.LinkType)) {
        throw 'file link identity rejected'
    }
    $Streams = @(Get-Item -LiteralPath $Path -Stream * -ErrorAction Stop)
    if ($Streams.Count -ne 1 -or [string]$Streams[0].Stream -cne ':$DATA') {
        throw 'file stream identity rejected'
    }
    if ((Get-A11V14FileSha256 -Path $Path) -cne $Sha256) {
        throw 'file digest identity rejected'
    }
}

function Assert-A11V14Utf8Lf {
    param([Parameter(Mandatory)] [string] $Path)
    $Bytes = [IO.File]::ReadAllBytes($Path)
    if ($Bytes.Length -eq 0 -or ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) -or $Bytes -contains 0x0D -or $Bytes[-1] -ne 0x0A -or ($Bytes.Length -gt 1 -and $Bytes[-2] -eq 0x0A)) {
        throw 'UTF-8 LF identity rejected'
    }
    $RoundTrip = $Utf8.GetBytes($Utf8.GetString($Bytes))
    if ($RoundTrip.Length -ne $Bytes.Length -or (Get-A11V14Sha256 -Bytes $RoundTrip) -cne (Get-A11V14Sha256 -Bytes $Bytes)) {
        throw 'UTF-8 roundtrip rejected'
    }
}

function Assert-A11V14RecordOnce {
    param(
        [Parameter(Mandatory)] [string] $Text,
        [Parameter(Mandatory)] [string] $Record
    )
    if (@($Text.Split([char]10) | Where-Object { $_ -ceq $Record }).Count -ne 1) {
        throw 'plan record identity rejected'
    }
}

if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath((Get-Location).Path), $RepositoryRoot)) {
    throw 'working directory identity rejected'
}
if (-not [StringComparer]::OrdinalIgnoreCase.Equals([IO.Path]::GetFullPath($PSCommandPath), (Join-Path $Workspace $SourceName))) {
    throw 'source path identity rejected'
}
if (Test-Path -LiteralPath $V12Workspace) {
    throw 'v12 namespace presence rejected'
}

$PlanFullPath = Join-Path $RepositoryRoot $PlanPath
$DesignFullPath = Join-Path $RepositoryRoot $DesignPath
$V13PlanFullPath = Join-Path $RepositoryRoot $V13PlanPath
$V13DesignFullPath = Join-Path $RepositoryRoot $V13DesignPath
$PlanItem = Get-Item -LiteralPath $PlanFullPath -Force -ErrorAction Stop
if ($PlanItem.PSIsContainer -or ($PlanItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string]$PlanItem.LinkType)) {
    throw 'plan ordinary file identity rejected'
}
$PlanStreams = @(Get-Item -LiteralPath $PlanFullPath -Stream * -ErrorAction Stop)
if ($PlanStreams.Count -ne 1 -or [string]$PlanStreams[0].Stream -cne ':$DATA') {
    throw 'plan stream identity rejected'
}
Assert-A11V14Utf8Lf -Path $PlanFullPath
Assert-A11V14OrdinaryFile -Path $DesignFullPath -ByteCount 8130 -Sha256 '8fed6373f6ff7d5b6f62e2ffdabe19f3ed859b6494d4349e24cc3249d0263f53'
Assert-A11V14OrdinaryFile -Path $V13PlanFullPath -ByteCount 129929 -Sha256 '27f604a9adb716e788b3a135e8b6d695f05af55e7349f85a9e12c4b59200507c'
Assert-A11V14OrdinaryFile -Path $V13DesignFullPath -ByteCount 11644 -Sha256 'b6593dce24c5de790678c35c80b8105efebced71e8039d5a4e65b4dd3f1cc61c'
Assert-A11V14Utf8Lf -Path $DesignFullPath
Assert-A11V14Utf8Lf -Path $V13PlanFullPath
Assert-A11V14Utf8Lf -Path $V13DesignFullPath

$PlanText = $Utf8.GetString([IO.File]::ReadAllBytes($PlanFullPath))
Assert-A11V14RecordOnce -Text $PlanText -Record 'V14_PLAN_SUBJECT|docs: plan A11 closure line identity recovery'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V14_DESIGN_COMMIT|032ae49d3c6e011726db47268d795ffea5e69fac'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V14_DESIGN_BLOB|91a91ddb3f8e7e7e4b51841923712fc7ed3636ed'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V13_PLAN_COMMIT|62fa510c335c24e6b8bec81083aa93339913b639'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V13_PLAN_BLOB|f8da0fb7c166c95a97cef00d77bae4deab1cb99b'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V13_DESIGN_COMMIT|84b0f64fa5565d785e32fe3fbe5de1dc473f23aa'
Assert-A11V14RecordOnce -Text $PlanText -Record 'PRESERVED_V13_OBSERVATION|controller_invocations=1|child_starts=1|retries=0|exit=0|stderr_bytes=0|stdout_lines=2|result=PASS'
Assert-A11V14RecordOnce -Text $PlanText -Record 'PRESERVED_V13_CLOSURE|closure_invocations=1|exception=closure v11 source line rejected|terminal=undefined|result=NO_GO'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V11_CONTROLLER_IDENTITY|28071|e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9'
Assert-A11V14RecordOnce -Text $PlanText -Record 'V11_LINE_IDENTITY|171|4|142|1ef50cf9ad6633f4da88ea82c2ca16c7abd9864416ae38510806638b88a2fd2b'

$SourceRecords = @($PlanText.Split([char]10) | Where-Object { $_.StartsWith("SOURCE_IDENTITY|$SourceName|", [StringComparison]::Ordinal) })
if ($SourceRecords.Count -ne 1) {
    throw 'source identity record count rejected'
}
$SourceParts = @($SourceRecords[0].Split('|'))
[long]$SourceByteCount = 0
if ($SourceParts.Count -ne 4 -or -not [long]::TryParse($SourceParts[2], [Globalization.NumberStyles]::None, [Globalization.CultureInfo]::InvariantCulture, [ref]$SourceByteCount) -or $SourceParts[3] -notmatch '\A[0-9a-f]{64}\z') {
    throw 'source identity record rejected'
}
Assert-A11V14OrdinaryFile -Path $PSCommandPath -ByteCount $SourceByteCount -Sha256 $SourceParts[3]
Assert-A11V14Utf8Lf -Path $PSCommandPath

$WorkspaceChildren = @(Get-ChildItem -LiteralPath $Workspace -Force)
if ($WorkspaceChildren.Count -ne 1 -or $WorkspaceChildren[0].PSIsContainer -or $WorkspaceChildren[0].Name -cne $SourceName) {
    throw 'v14 workspace inventory rejected'
}

$V13Expected = [ordered]@{
    'task-1-stage0-plan-identity-controller-v13.ps1' = @([long]31491, 'dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086')
    'task-1-stage0-v13.ps1' = @([long]24403, '18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967')
}
$V13Children = @(Get-ChildItem -LiteralPath $V13Workspace -Force | Sort-Object Name)
if ($V13Children.Count -ne 2 -or @($V13Children | Where-Object PSIsContainer).Count -ne 0) {
    throw 'v13 workspace inventory rejected'
}
foreach ($Name in $V13Expected.Keys) {
    Assert-A11V14OrdinaryFile -Path (Join-Path $V13Workspace $Name) -ByteCount $V13Expected[$Name][0] -Sha256 $V13Expected[$Name][1]
}

Assert-A11V14OrdinaryFile -Path $V11Controller -ByteCount 28071 -Sha256 'e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9'
Assert-A11V14Utf8Lf -Path $V11Controller
$V11Lines = [IO.File]::ReadAllText($V11Controller, $Utf8).Split([char]10)
if ($V11Lines.Count -lt 171 -or -not [StringComparer]::Ordinal.Equals($V11Lines[170], $ExpectedV11Line)) {
    throw 'v11 line identity rejected'
}
$LeadingSpaces = $V11Lines[170].Length - $V11Lines[170].TrimStart(' ').Length
$LineBytes = $Utf8.GetBytes($V11Lines[170])
if ($LeadingSpaces -ne 4 -or $LineBytes.Length -ne 142 -or (Get-A11V14Sha256 -Bytes $LineBytes) -cne '1ef50cf9ad6633f4da88ea82c2ca16c7abd9864416ae38510806638b88a2fd2b') {
    throw 'v11 line byte identity rejected'
}

$OutputBytes = $Utf8.GetBytes($Terminal + "`n")
$OutputStream = [Console]::OpenStandardOutput()
$OutputStream.Write($OutputBytes, 0, $OutputBytes.Length)
$OutputStream.Flush()
```
<!-- SOURCE_END:task-1-v13-closure-line-identity-v14.ps1 -->

## Task 1: Entry gate and diagnostic RED

**Files:**

- Read: v14 design, v13 design/plan, v13 source inventory, v11 controller.
- Require absent: v14 runtime namespace and v12 runtime namespace.

1. Require branch `codex/wave0-model-contract`, HEAD equal to the v14 design
   commit, exact author/committer identity and subject, linked and canonical
   worktrees clean, and no v14 plan or namespace yet.
2. Verify the v14 design direct parent, blob, byte identity, UTF-8/LF form, and
   exact one-path commit scope.
3. Verify the frozen v13 commit/blob chain, v13 two-source inventory, v12
   namespace absence, and v11 controller identity.
4. RED reads the exact committed v13 plan as data. It extracts the assignment
   beginning `$V11Line=` from the final closure, evaluates only that quoted
   PowerShell string literal, and requires:
   - frozen expectation leading spaces: zero;
   - actual line 171 leading spaces: four;
   - ordinal equality: false;
   - actual line bytes/hash: the frozen v14 values;
   - process starts: zero.
5. Emit exactly:

```text
ENTRYV14_LINE_IDENTITY_RED_PASS|v13_expected_spaces=0|actual_spaces=4|ordinal_equal=false|line=171|starts=0
```

Any other result preserves the current state and stops before plan commit or
runtime materialization.

## Task 2: Commit the implementation plan

**Files:**

- Create and commit only: `docs/superpowers/plans/2026-08-31-val-wave0-a11-closure-line-identity-recovery.md`.

1. Extract the frozen block strictly between the source markers, excluding
   the Markdown fence, and encode it as strict UTF-8 without BOM, LF-only,
   exactly one final LF.
2. Compute its decimal byte count and lowercase SHA-256 with .NET SHA-256.
3. Replace the one provisional source-identity field, then independently repeat the
   extraction and require the recorded identity to match.
4. Parse every PowerShell fence with the current PowerShell parser. Review
   every command and reject writes, process starts, external runtime, Docker,
   GPU, model, network, authorization, push, merge, or release surface.
5. Require this plan to be the only worktree change, then commit with exact
   identity and subject `docs: plan A11 closure line identity recovery`.
6. Require the plan commit direct parent to be the v14 design commit, the
   commit to contain exactly this plan path, and both worktrees to be clean.

## Task 3: Materialization and static GREEN

**Files:**

- Create exactly once:
  `.superpowers/sdd/2026-08-31-val-wave0-a11-closure-line-identity-recovery/task-1-v13-closure-line-identity-v14.ps1`.

1. Rerun the complete entry gate against the committed plan. Freeze the exact
   plan commit and blob for all remaining wrappers.
2. Rerun diagnostic RED against committed inputs. Do not use a runtime result
   to change the source.
3. Admit the frozen block and its `SOURCE_IDENTITY` record. Reject any missing,
   duplicate, malformed, or mismatched record/block.
4. Use exactly one `apply_patch` call to create the namespace's single source.
   No other materialization method or file is allowed.
5. Admission requires exact path containment, ordinary non-reparse file,
   single `:$DATA` stream, UTF-8 without BOM, LF-only endings, one final LF,
   exact byte count, exact SHA-256, exact one-file inventory, and clean Git in
   both worktrees (the ignored source does not appear in status).
6. GREEN parses the admitted source as data and requires:
   - zero parse errors;
   - exactly one `$ExpectedV11Line` assignment whose static value begins with
     four ASCII spaces and is ordinal-equal to actual v11 line 171;
   - zero zero-indent expectation assignments;
   - exact source identity and exact one-source inventory;
   - no `Process.Start`, `Start-Process`, call operator, dot-source,
     `Invoke-Expression`, dynamic command, external executable, file-write,
     Docker, GPU, CUDA, model, network, `OwnerAuthorizationId`, Git mutation,
     push, merge, or release surface;
   - exactly one standard-output `Write` and one `Flush`;
   - process starts: zero.
7. Emit exactly:

```text
ENTRYV14_LINE_IDENTITY_GREEN_PASS|expected_spaces=4|actual_spaces=4|ordinal_equal=true|source_files=1|starts=0
```

Any difference preserves the source and stops without invoking it.

## Task 4: Single invocation boundary and formal verifier

1. The boundary repeats exact branch/HEAD/parent/subject/author/committer/plan
   blob, plan/source/design/v13/v11 identities, namespace inventories, v12
   absence, parser/AST GREEN, and linked/canonical cleanliness.
2. Pin the executable already used by the plan review and record its ordinary
   file identity. The exact argv is:

```text
-NoLogo -NoProfile -NonInteractive -File <repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-closure-line-identity-recovery\task-1-v13-closure-line-identity-v14.ps1
```

3. Emit a boundary record with `invocations=0`, then invoke the source exactly
   once. Capture raw stdout, raw stderr, exit code, elapsed time, and process
   identity in memory only. Do not create a transcript or result file.
4. Require exit zero, empty stderr, and stdout exactly equal to the one
   LF-terminated terminal:

```text
ENTRYV14_CLOSURE_LINE_IDENTITY_PASS|v13_observation=preserved_pass|v13_closure=preserved_no_go|v11_line=171|leading_spaces=4|linked=clean|canonical=clean
```

Any launch uncertainty, timeout, capture difference, nonzero exit, stderr,
extra output, or side effect is a fresh preserved v14 NO_GO. The invocation is
consumed when issued and is never repeated.

## Task 5: Final closure

1. Read-only closure repeats all frozen Git, document, source, v13 inventory,
   v12 absence, and v11 line identities. Require exact one-source v14
   inventory, unchanged source identity, and both worktrees clean.
2. Require the captured formal invocation count to be exactly one and the v13
   controller/child invocation counts to remain unchanged at one/one.
3. Preserve the literal v13 closure exception and undefined v13 failure
   terminal; never claim that v13 closure was rerun or changed to PASS.
4. On success emit:

```text
ENTRYV14_RECOVERY_PASS / A11_RUNTIME_NOT_AUTHORIZED
```

5. Stop. Do not begin a new A11 runtime attempt, Tasks 7-8, Wave 1, Docker,
   GPU, model, push, merge, release, or any other repository work.
