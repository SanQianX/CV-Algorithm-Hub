@echo off
chcp 65001 >nul
echo ============================================
echo 数据目录迁移脚本
echo ============================================
echo.
echo 警告: 此脚本将执行以下操作:
echo  1. 停止所有 Docker 容器
echo  2. 移动 postgres 数据到 databases/users/postgres
echo  3. 创建新目录结构
echo  4. 重新启动容器
echo.
echo 目标结构:
echo K:/data/
echo ├── database_manager/
echo ├── databases/
echo │   ├── finance/
echo │   ├── users/postgres/
echo │   ├── logs/
echo │   └── custom/
echo └── backup/
echo.
echo ============================================
set /p confirm="确认执行迁移? (y/n): "
if /i "%confirm%" neq "y" exit /b 1

echo.
echo 步骤 1: 停止 Docker 容器...
docker-compose down
if errorlevel 1 echo 警告: 容器停止时出现错误，继续执行...

echo.
echo 步骤 2: 等待文件解锁...
timeout /t 3 /nobreak >nul

echo.
echo 步骤 3: 创建目录结构...
mkdir K:\data\database_manager\config
mkdir K:\data\database_manager\metadata
mkdir K:\data\database_manager\plugins
mkdir K:\data\database_manager\api_gateway

mkdir K:\data\databases\finance
mkdir K:\data\databases\users
mkdir K:\data\databases\logs
mkdir K:\data\databases\custom

mkdir K:\data\backup

echo.
echo 步骤 4: 移动 postgres 数据...
echo 正在移动 K:\data\postgres\* 到 K:\data\databases\users\postgres\
timeout /t 2 /nobreak >nul

rem 使用 xcopy 复制并删除源文件
xcopy /E /I /Q /Y "K:\data\postgres\*" "K:\data\databases\users\postgres\" >nul 2>&1
if exist "K:\data\databases\users\postgres\PG_VERSION" (
    echo 复制成功，删除原目录...
    rmdir /S /Q "K:\data\postgres" 2>nul
    echo 移动完成!
) else (
    echo 警告: 移动可能失败，请手动检查
)

echo.
echo 步骤 5: 迁移备份文件...
if exist "K:\data\cv_algorithm_hub_backup.sql" (
    move /Y "K:\data\cv_algorithm_hub_backup.sql" "K:\data\backup\" >nul
    echo 已移动备份文件
)

echo.
echo 步骤 6: 重新启动容器...
echo.
docker-compose up -d

echo.
echo ============================================
echo 迁移完成!
echo ============================================
echo.
echo 新目录结构:
tree K:\data\ /F 2>nul | head -40
echo.
echo 请访问 http://localhost 测试功能
echo.
pause
