# Set Flutter domestic mirrors
Write-Host "Setting up Flutter domestic mirrors..." -ForegroundColor Green

$env:PUB_HOSTED_URL = "https://mirrors.aliyun.com/dart-pub/"
$env:FLUTTER_STORAGE_BASE_URL = "https://mirrors.aliyun.com/flutter/"

Write-Host "Domestic mirrors have been set up:" -ForegroundColor Green
Write-Host "PUB_HOSTED_URL = $env:PUB_HOSTED_URL" -ForegroundColor Cyan
Write-Host "FLUTTER_STORAGE_BASE_URL = $env:FLUTTER_STORAGE_BASE_URL" -ForegroundColor Cyan

Write-Host "`nNow you can run flutter pub get or other Flutter commands." -ForegroundColor Green

# Wait for user input
Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
