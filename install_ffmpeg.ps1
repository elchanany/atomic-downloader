$url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
$zip = "ffmpeg.zip"
$extractPath = "ffmpeg_temp"

Write-Host "Downloading FFmpeg from $url..."
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri $url -OutFile $zip

Write-Host "Extracting..."
Expand-Archive -Path $zip -DestinationPath $extractPath -Force

Write-Host "Locating binaries..."
$binPath = Get-ChildItem -Path $extractPath -Recurse -Filter "bin" | Select-Object -ExpandProperty FullName
if ($binPath) {
    Write-Host "Found bin at: $binPath"
    Copy-Item "$binPath\ffmpeg.exe" -Destination . -Force
    Copy-Item "$binPath\ffprobe.exe" -Destination . -Force
    Write-Host "Binaries moved successfully."
} else {
    Write-Error "Could not find bin folder in extracted files."
}

Write-Host "Cleaning up..."
Remove-Item $zip -Force
Remove-Item $extractPath -Recurse -Force
Write-Host "Done."
