$ErrorActionPreference = 'Stop'

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$input = Join-Path $workspace 'the special.mp4'
$output = Join-Path $workspace 'special-compressed.mp4'

$ffmpeg = 'C:\Users\KIIT0001\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.2-full_build\bin\ffmpeg.exe'

if (-not (Test-Path $ffmpeg)) {
    throw "FFmpeg not found at $ffmpeg"
}

if (-not (Test-Path $input)) {
    throw "Input video not found at $input"
}

& $ffmpeg -i $input -vf "scale=960:540:force_original_aspect_ratio=decrease,pad=960:540:(ow-iw)/2:(oh-ih)/2" -c:v libx264 -preset slow -crf 26 -c:a aac -b:a 128k -movflags +faststart $output

Write-Host "Compressed video saved to: $output"
