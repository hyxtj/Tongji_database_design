# 城市交通状态查询系统 - 后端启动脚本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  城市交通状态查询系统 - 后端启动  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查是否已安装uv
Write-Host "检查uv是否已安装..." -ForegroundColor Yellow
$uvInstalled = Get-Command uv -ErrorAction SilentlyContinue

if (-not $uvInstalled) {
    Write-Host "未检测到uv,正在安装..." -ForegroundColor Red
    pip install uv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "uv安装失败,请手动安装: pip install uv" -ForegroundColor Red
        pause
        exit 1
    }
    Write-Host "uv安装成功!" -ForegroundColor Green
}

# 进入backend目录
Set-Location -Path $PSScriptRoot

# 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host ".env文件不存在,正在从.env.example复制..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host ".env文件已创建,请根据需要修改配置" -ForegroundColor Green
}

# 同步依赖
Write-Host ""
Write-Host "正在同步Python依赖..." -ForegroundColor Yellow
uv sync

if ($LASTEXITCODE -ne 0) {
    Write-Host "依赖安装失败!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "依赖安装成功!" -ForegroundColor Green

# 启动应用
Write-Host ""
Write-Host "正在启动后端服务..." -ForegroundColor Yellow
Write-Host "后端地址: http://localhost:5000" -ForegroundColor Cyan
Write-Host "健康检查: http://localhost:5000/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

uv run python app.py
