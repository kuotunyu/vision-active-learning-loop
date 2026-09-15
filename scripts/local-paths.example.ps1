# Copy this file to scripts\local-paths.ps1 (git-ignored) and fill in the paths for your machine.
# run_lite_seed17.ps1 dot-sources it; explicit parameters always win, the file only fills parameters left empty.
# The two environment variables serve the verification scripts in docs\status\ (dot-source this file first).
$LocalDefaults = @{
    Manifest   = '<evidence-root>\lite\data\czech\manifest.json'
    PublicView = '<evidence-root>\lite\data\czech\public-pool.json'
    Images     = '<data-root>\rdd2022\czech\images'
    Snapshot   = '<evidence-root>\wave0\model_cache\snapshots\PekingU--rtdetr_r18vd\cc5b50f32f0100caaa3bd275343e2fb17762c73d'
    OutputRoot = '<evidence-root>\lite'
    Embeddings = '<evidence-root>\lite\data\czech\embeddings-dinov2-small.npz'
}
$env:VAL_EVIDENCE_ROOT = '<evidence-root>'
$env:VAL_DATA_ROOT = '<data-root>'
