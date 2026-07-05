# 城市交通状态查询系统 - 前端启动脚本

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  城市交通状态查询系统 - 前端启动  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# 检查Node.js
Write-Host "检查Node.js是否已安装..." -ForegroundColor Yellow
$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue

if (-not $nodeInstalled) {
    Write-Host "未检测到Node.js,请先安装Node.js" -ForegroundColor Red
    Write-Host "下载地址: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

$nodeVersion = node --version
Write-Host "Node.js版本: $nodeVersion" -ForegroundColor Green

# 检查pnpm
Write-Host "检查pnpm是否已安装..." -ForegroundColor Yellow
$pnpmInstalled = Get-Command pnpm -ErrorAction SilentlyContinue

if (-not $pnpmInstalled) {
    Write-Host "未检测到pnpm,正在安装..." -ForegroundColor Yellow
    npm install -g pnpm
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pnpm安装失败!" -ForegroundColor Red
        pause
        exit 1
    }
    
    Write-Host "pnpm安装成功!" -ForegroundColor Green
}

$pnpmVersion = pnpm --version
Write-Host "pnpm版本: $pnpmVersion" -ForegroundColor Green

# 进入frontend目录
Set-Location -Path $PSScriptRoot

# 检查node_modules
if (-not (Test-Path "node_modules")) {
    Write-Host ""
    Write-Host "首次运行,正在安装依赖..." -ForegroundColor Yellow
    pnpm install
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败!" -ForegroundColor Red
        pause
        exit 1
    }
    
    Write-Host "依赖安装成功!" -ForegroundColor Green
}

# 启动开发服务器
Write-Host ""
Write-Host "正在启动前端开发服务器..." -ForegroundColor Yellow
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "后端代理: http://localhost:5000/api" -ForegroundColor Cyan
Write-Host ""
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Gray
Write-Host ""

pnpm run dev
