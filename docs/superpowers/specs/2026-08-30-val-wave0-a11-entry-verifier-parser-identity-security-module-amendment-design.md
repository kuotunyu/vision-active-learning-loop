# Wave 0 A11 Entry-Verifier Parser-Identity Security-Module Amendment Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `0788f6143691d5a39730fb06508be3949de1b3f0`

## Purpose

Amend the approved v8 parser-identity recovery so both parser workers obtain
Authenticode evidence from an explicit, identity-frozen Microsoft security
provider rather than ambient module auto-loading.

This amendment is a narrow normative overlay on:

| Object | Identity |
|---|---|
| Original design commit | `0788f6143691d5a39730fb06508be3949de1b3f0` |
| Original design blob | `a837d94d58d8ad2ee1c71fd51de64257fe49d060` |
| Original design path | `docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery-design.md` |

All original requirements remain normative except where this document
explicitly replaces the provider-import prohibition, provider evidence schema,
and affected intermediate terminals.

The final success boundary is unchanged:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

## Authoring-time discovery

During docs-only implementation-plan verification, the exact Windows
PowerShell 5.1 process self-attested as:

```text
path: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
engine: 5.1.26100.9168
edition: Desktop
executable SHA-256: 7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5
```

Pure .NET `FileStream` plus `SHA256` produced the exact approved executable
digest. In that no-profile process, both command lookups were absent before an
explicit module import:

```text
Get-FileHash: unavailable
Get-AuthenticodeSignature: unavailable
```

The inherited `PSModulePath` contained the Windows module directory, but
ambient command discovery still did not provide either command. The first
plan-authoring parser check therefore stopped before parsing any plan block.
It did not execute Stage 0, create the v8 workspace, run a RED, or consume any
v8 implementation gate.

An exact-path diagnostic import of the built-in Windows
`Microsoft.PowerShell.Security` manifest made
`Get-AuthenticodeSignature` available with command provenance bound to the
expected GAC assembly. A separate no-profile PowerShell 7 diagnostic showed
that its command lookup silently auto-loaded its bundled
`Microsoft.PowerShell.Security` module. The original design's assumption that
signature evidence required no additional import was therefore false for both
runtimes: Windows lacked the command, while Core supplied it through an
implicit dependency.

## Root cause

The provider dependency was implicit. Executable path, bytes, engine, edition,
and signer policy were frozen, but the mechanism used inside each child to
obtain `signature_status`, `signer_subject`, and `signer_thumbprint` was not.

Depending on ambient module discovery would recreate the same class of defect
the v8 design is intended to eliminate: a label or command name could appear
correct without a proven implementation identity. Removing child signature
verification would instead weaken the approved self-attestation contract.

## Decision

Use exact-path, exact-identity Microsoft security providers for both parser
runtimes and use pure .NET for every SHA-256 measurement.

1. The implementation plan freezes one security manifest and one nested
   security assembly for PowerShell 7 and one pair for Windows PowerShell 5.1.
2. Stage 0 validates all four provider files by path, type, bytes, SHA-256,
   version where present, link/reparse policy, parent chain, signature, signer,
   and thumbprint without executing a parser source.
3. Each worker validates its role-specific provider bytes and link state with
   .NET before import.
4. Each worker imports only its literal manifest path, requires the exact
   returned module/nested-assembly/command provenance, then uses only
   `Get-AuthenticodeSignature` from that provider.
5. Each worker verifies its executable, provider manifest, and provider
   assembly Authenticode records before importing the exact GREEN identity
   module or parsing a target.
6. No worker calls `Get-FileHash`; all hashes use a closed .NET helper.

There is no module-name lookup, gallery lookup, PATH search, auto-loading,
fallback module, second manifest, private reflection, P/Invoke, `Add-Type`, or
dynamic code.

## Alternatives considered

### A. Pin and explicitly import each runtime's Microsoft security provider — selected

This preserves child signature proof and makes the dependency visible,
hashable, statically inspectable, and role-specific. It uses built-in signed
files already present on the host and adds no repository or runtime artifact.

### B. Let PowerShell 7 auto-load and special-case Windows PowerShell — rejected

This would leave one worker dependent on an invisible ambient resolution path
and give the two identity records different evidence semantics.

### C. Trust the controller's signature result inside the child — rejected

Exact controller evidence plus child executable hash is strong, but it does
not satisfy the approved requirement that each parser process self-attest all
identity fields before parsing.

### D. Use P/Invoke, `Add-Type`, or private reflection — rejected

These options add dynamic code, native interop, or private APIs to an evidence
gate. They enlarge the static surface and are less stable than the signed
built-in provider implementing the platform's Authenticode semantics.

## Pinned PowerShell 7 security provider

### Manifest

```text
path: C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1
bytes: 15463
SHA-256: c3be79f92869f0f81050e16ce60736da7525f76d9c8784cf95bf4e83deddf62a
module GUID: A94C8C7E-9810-47C0-B8AF-65089C13A35A
module version: 7.0.0.0
compatible edition: Core
nested assembly: Microsoft.PowerShell.Security.dll
signature: Valid
signer: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
signer thumbprint: AB172913A2960A224809EE8A0C371CD47A079B72
leaf link type: none
reparse point: false
parent-chain reparse/link count: 0
```

### Nested assembly

```text
path: C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\Microsoft.PowerShell.Security.dll
bytes: 345952
SHA-256: 5e4d6fc14660e9e45a77e736580b9a770a12e3895d020c31c69baf0176d1bf90
file version: 7.6.4.500
product version: 7.6.4 SHA: 929d27f4e66dcfba8f5f74ff03105705e483a27d+929d27f4e66dcfba8f5f74ff03105705e483a27d
signature: Valid
signer: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
signer thumbprint: 1D77A9B9E8FE2075D9AD15123257FB90DB0DA4A1
leaf link type: none
reparse point: false
parent-chain reparse/link count: 0
```

## Pinned Windows PowerShell 5.1 security provider

### Manifest

```text
path: C:\Windows\System32\WindowsPowerShell\v1.0\Modules\Microsoft.PowerShell.Security\Microsoft.PowerShell.Security.psd1
bytes: 776
SHA-256: fa7150089e8a67a0aad27cd324d119b9778ccbead6242397780c5d5077246d30
module GUID: A94C8C7E-9810-47C0-B8AF-65089C13A35A
module version: 3.0.0.0
PowerShell version: 5.1
compatible edition: Desktop
nested assembly: Microsoft.PowerShell.Security.dll
signature: Valid
signer: CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
signer thumbprint: 71F53A26BB1625E466727183409A30D03D7923DF
leaf link type: HardLink
reparse point: false
parent-chain reparse/link count: 0
```

### Nested assembly

```text
path: C:\Windows\Microsoft.NET\assembly\GAC_MSIL\Microsoft.PowerShell.Security\v4.0_3.0.0.0__31bf3856ad364e35\Microsoft.PowerShell.Security.dll
bytes: 93696
SHA-256: 9d24d2a9d3b5326a9bd8fcae8863fa5af32d37d7d0eee175600d7d4e89af8010
file version: 10.0.26100.1
product version: 10.0.26100.1
signature: Valid
signer: CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
signer thumbprint: 71F53A26BB1625E466727183409A30D03D7923DF
leaf link type: HardLink
reparse point: false
parent-chain reparse/link count: 0
```

The two Windows provider HardLinks are closed exceptions in addition to the
already approved Windows PowerShell executable HardLink. Each exception
accepts only its listed canonical path and exact identity. No sibling hard-link
path, component-store search, alternate GAC version, symbolic link, junction,
or reparse point is allowed.

## Provider validation and import flow

The complete .NET digest helper is equivalent under both runtimes:

```powershell
function Get-A11FileSha256 {
    param([Parameter(Mandatory)] [string] $Path)
    $Algorithm = [Security.Cryptography.SHA256]::Create()
    $Stream = [IO.File]::Open($Path, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::Read)
    try {
        ([BitConverter]::ToString($Algorithm.ComputeHash($Stream))).Replace('-', '').ToLowerInvariant()
    }
    finally {
        $Stream.Dispose()
        $Algorithm.Dispose()
    }
}
```

Before import, the worker validates the exact role-specific manifest and
assembly paths, ordinary file type, bytes, .NET digest, file/product versions,
leaf link policy, absence of `ReparsePoint`, and zero parent-chain link/reparse
count. It then executes exactly one provider import:

```powershell
$SecurityModule = Import-Module -Name $ExpectedSecurityManifestPath -Force -PassThru -ErrorAction Stop
```

The returned module must have the exact manifest path, GUID, module version,
compatible edition, and sole expected nested assembly path. The worker then
resolves exactly:

```powershell
Get-Command -Name Get-AuthenticodeSignature -CommandType Cmdlet -Module Microsoft.PowerShell.Security -ErrorAction Stop
```

The returned command's module path and DLL path must equal the frozen manifest
and nested assembly. No other exported provider command may be invoked.

Only after provenance passes may the worker call the exact command for its
own executable, provider manifest, and provider assembly. Each result must be
`Valid` with the expected signer subject and thumbprint. The worker then
imports the exact GREEN comparator as its second and final module import,
proves the complete runtime identity record, and only then parses explicit
target files.

`$ProgressPreference` is `SilentlyContinue` before either import so provider
loading cannot emit a progress record to redirected stderr. Any stdout/stderr
beyond the worker's closed evidence protocol is rejection.

## Inventory and verifier overlay

The original 14-property parser-runtime identity record remains unchanged.
The provider is a separately validated execution dependency, not a claimed
property supplied by the caller.

The canonical inventory root order becomes:

```text
schema_version,inventory_id,source_plan_commit,source_design_commit,source_amendment_commit,failed_v7,parser_runtimes,security_providers,workspaces,absent_paths
```

`security_providers` contains PowerShell 7 then Windows PowerShell 5.1. Each
record has exact order:

```text
role,manifest,nested_assembly,allowed_commands
```

Each file object order is:

```text
path,byte_count,sha256,file_version,product_version,signature_status,signer_subject,signer_thumbprint,leaf_link_type,leaf_reparse_point,parent_chain_reparse_points
```

Missing version strings for the Windows manifest are exact empty strings.
`allowed_commands` is exactly the one-element array
`["Get-AuthenticodeSignature"]`.

Provider files are runtime dependencies, not predecessor evidence. The formal
preserved file count therefore remains 24, the workspace count remains five,
and the persistent absence count remains 12. Formal entry and independent
closure revalidate all four provider files without executing either parser or
importing either worker.

## Static admission overlay

The static verifier must require:

- the .NET digest helper above and zero `Get-FileHash` tokens in worker or
  controller;
- exactly two `Import-Module` AST call sites in the worker: the selected exact
  security manifest and the exact GREEN comparator;
- provider selection only from the closed runtime role, with no module name,
  `PSModulePath`, gallery, wildcard, relative path, fallback, or second
  candidate;
- provider byte/hash/link validation before provider import;
- exact module, nested-assembly, and command provenance before signature use;
- exactly three worker calls to the provider command and no other provider
  command invocation;
- executable and provider signature acceptance before GREEN import and before
  the first parser API call;
- exact four provider identities in Stage 0, inventory, formal verifier,
  closure, and report; and
- no reflection, P/Invoke, `Add-Type`, dynamic evaluation, network, write,
  process mutation, or expanded runtime action.

All original static prohibitions remain.

## Terminal overlay

The affected exact PASS terminals become:

```text
ENTRYV8_STAGE0_PASS|v7=preserved_no_go|files=4|workspace=absent|runtimes=2|providers=2|linked=clean|canonical=clean
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-red|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-green|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
ENTRYV8_DUAL_PARSER_PASS|phase=static|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|providers=2|starts=2|writes=0
ENTRYV8_STATIC_PASS|parser_roles=bound|providers=2|scalar=ordinal|files=24|writes=0|retries=0
ENTRYV8_FORMAL_PASS|workspaces=5|files=24|providers=2|v7=no_go_preserved|comparison=ordinal|writes=0
ENTRYV8_CLOSURE_PASS|workspaces=5|files=24|providers=2|formal=exact|writes=0
```

The existing NO_GO terminals and final success terminal remain unchanged. A
provider identity, import, provenance, output, or signature difference is
`ENTRYV8_DUAL_PARSER_UNPROVABLE / NO_GO` during a parser phase and
`ENTRYV8_RECOVERY_UNPROVABLE / NO_GO` during formal or closure. It is never
permission to auto-load, search, import another module, omit a signature field,
or retry.

## Authority and non-goals

This amendment authorizes read-only inspection and exact-path import of the
four pinned provider files only inside the already approved Stage 0/controller/
worker/formal/closure boundary. It does not authorize installing, updating,
copying, replacing, registering, repairing, signing, trusting, or changing a
module, certificate store, execution policy, PATH, `PSModulePath`, host, or
repository file outside the docs-only amendment/plan commits and approved
ignored v8 workspace.

It adds no v8 human file, tracked product file, process start, parser phase,
preserved artifact, absence record, Docker/GPU/A11/runtime action,
`OwnerAuthorizationId`, push, merge, release, or Wave 1 permission.

## Append-only lineage

This amendment commit changes only this file and is a direct child of:

```text
0788f6143691d5a39730fb06508be3949de1b3f0
```

Its exact author and committer are:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its exact subject is:

```text
docs: amend A11 parser identity security provider
```

After written-spec approval, the implementation plan is a one-file direct
child of this amendment commit and uses the same author/committer identity.
The existing uncommitted plan draft is authoring work only; it is not an
execution artifact, evidence input, or consuming gate.

## Success criteria

This amendment is satisfied only when:

1. it is a one-file direct-child commit of the original design with exact
   commit identity;
2. the implementation plan is a one-file direct child of this amendment and
   carries both design blobs;
3. Stage 0, both workers, inventory, static verifier, formal verifier, closure,
   and report use the exact four provider identities;
4. each worker uses .NET SHA-256, exactly one exact-path security-provider
   import, exact provenance, exactly three Authenticode calls, and no ambient
   or fallback resolution;
5. all amended intermediate terminals are exact and single-use; and
6. final closure still emits only:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```
