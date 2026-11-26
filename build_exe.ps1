# Builds dist\AIMeeting (run from repo root with the venv active or .venv present).
$ErrorActionPreference = "Continue"
$py = ".\.venv\Scripts\python.exe"
& $py -m PyInstaller --noconfirm --clean --onedir --name AIMeeting `
  --collect-data faster_whisper --collect-all ctranslate2 --collect-all onnxruntime `
  --collect-submodules uvicorn --collect-submodules sentence_transformers `
  --copy-metadata tqdm --copy-metadata regex --copy-metadata requests --copy-metadata packaging `
  --copy-metadata filelock --copy-metadata numpy --copy-metadata tokenizers --copy-metadata huggingface_hub `
  --copy-metadata safetensors --copy-metadata transformers --copy-metadata torch --copy-metadata sentence_transformers `
  launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }
$ErrorActionPreference = "Stop"
$out = "dist\AIMeeting"
Copy-Item web "$out\web" -Recurse -Force
Copy-Item models "$out\models" -Recurse -Force
$ff = (Get-Command ffmpeg).Source | Split-Path
New-Item -ItemType Directory "$out\bin" -Force | Out-Null
Copy-Item "$ff\ffmpeg.exe","$ff\ffprobe.exe" "$out\bin" -Force
Write-Host "Built $out"
