# Builds dist\AIMeeting: Rust desktop window (AIMeeting.exe) + Python backend (AIMeetingCore.exe).
# Run from repo root with .venv present, plus web\ (static export) and models\.
$py = ".\.venv\Scripts\python.exe"
$ErrorActionPreference = "Continue"
& $py -m PyInstaller --noconfirm --clean --onedir --noconsole --name AIMeetingCore `
  --collect-data faster_whisper --collect-all ctranslate2 --collect-all onnxruntime `
  --collect-submodules uvicorn --collect-submodules sentence_transformers `
  --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging `
  --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata huggingface_hub `
  --copy-metadata safetensors --copy-metadata transformers --copy-metadata torch --copy-metadata sentence_transformers `
  launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
cargo build --release --manifest-path desktop\Cargo.toml
if ($LASTEXITCODE -ne 0) { throw "cargo build failed" }
$ErrorActionPreference = "Stop"
$core = "dist\AIMeetingCore"
Copy-Item web "$core\web" -Recurse -Force
Copy-Item models "$core\models" -Recurse -Force
$ff = (Get-Command ffmpeg).Source | Split-Path
New-Item -ItemType Directory "$core\bin" -Force | Out-Null
Copy-Item "$ff\ffmpeg.exe","$ff\ffprobe.exe" "$core\bin" -Force
# Bundled Ollama runtime (no ROCm / CUDA 13 to save space) and the llama3.1 model
$olSrc = Join-Path $env:LOCALAPPDATA "Programs\Ollama"
$olModels = Join-Path $env:USERPROFILE ".ollama\models"
New-Item -ItemType Directory "$core\ollama\lib\ollama" -Force | Out-Null
Copy-Item "$olSrc\ollama.exe" "$core\ollama\" -Force
Get-ChildItem "$olSrc\lib\ollama" | Where-Object { $_.Name -notin @("rocm_v7_1", "cuda_v13") } | Copy-Item -Destination "$core\ollama\lib\ollama" -Recurse -Force
$mf = "manifests\registry.ollama.ai\library\llama3.1"
New-Item -ItemType Directory "$core\ollama-models\$mf", "$core\ollama-models\blobs" -Force | Out-Null
Copy-Item "$olModels\$mf\latest" "$core\ollama-models\$mf\latest" -Force
$man = Get-Content "$olModels\$mf\latest" -Raw | ConvertFrom-Json
foreach ($d in @($man.config.digest) + @($man.layers.digest)) {
  Copy-Item "$olModels\blobs\$($d.Replace(':','-'))" "$core\ollama-models\blobs\" -Force
}
Copy-Item "desktop\target\release\AIMeeting.exe" "$core\AIMeeting.exe" -Force
if (Test-Path dist\AIMeeting) { Remove-Item dist\AIMeeting -Recurse -Force }
Rename-Item $core "AIMeeting"
Write-Host "Built dist\AIMeeting (run AIMeeting.exe)"
