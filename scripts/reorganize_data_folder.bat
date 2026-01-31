@echo off
chcp 65001 >nul
echo ============================================
echo 数据目录重构脚本
echo ============================================
echo.
echo 当前 K:\data\ 结构将被重组为:
echo.
echo K:/data/
echo ├── database_manager/          # 数据管理系统
echo │   ├── config/               # 配置中心
echo │   ├── metadata/             # 元数据管理
echo │   ├── plugins/              # 功能插件
echo │   └── api_gateway/          # API网关
echo ├── databases/                # 数据库文件存储
echo │   ├── finance/             # 金融数据
echo │   ├── users/               # 用户数据
echo │   ├── logs/                # 系统日志
echo │   └── custom/              # 自定义数据
echo └── backup/                  # 数据备份
echo.
echo ============================================
echo 警告: 此操作不会移动正在使用的 postgres 数据库
echo ============================================
echo.

echo 步骤 1: 创建目录结构...
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
echo 目录创建完成!
echo.

echo 步骤 2: 创建配置文件...
echo # 数据库管理器配置 > K:\data\database_manager\config\database_manager.yaml
echo app: >> K:\data\database_manager\config\database_manager.yaml
echo   name: "Database Manager" >> K:\data\database_manager\config\database_manager.yaml
echo   version: "1.0.0" >> K:\data\database_manager\config\database_manager.yaml
echo   data_path: "K:/data/databases" >> K:\data\database_manager\config\database_manager.yaml
echo. >> K:\data\database_manager\config\database_manager.yaml
echo databases: >> K:\data\database_manager\config\database_manager.yaml
echo   postgres: >> K:\data\database_manager\config\database_manager.yaml
echo     path: "K:/data/postgres" >> K:\data\database_manager\config\database_manager.yaml
echo     type: "postgresql" >> K:\data\database_manager\config\database_manager.yaml
echo. >> K:\data\database_manager\config\database_manager.yaml
echo categories: >> K:\data\database_manager\config\database_manager.yaml
echo   - name: "finance" >> K:\data\database_manager\config\database_manager.yaml
echo     description: "金融数据存储" >> K:\data\database_manager\config\database_manager.yaml
echo   - name: "users" >> K:\data\database_manager\config\database_manager.yaml
echo     description: "用户数据存储" >> K:\data\database_manager\config\database_manager.yaml
echo   - name: "logs" >> K:\data\database_manager\config\database_manager.yaml
echo     description: "系统日志存储" >> K:\data\database_manager\config\database_manager.yaml
echo.

echo 配置文件已创建: K:\data\database_manager\config\database_manager.yaml
echo.

echo 步骤 3: 迁移现有备份文件...
if exist "K:\data\cv_algorithm_hub_backup.sql" (
    move "K:\data\cv_algorithm_hub_backup.sql" "K:\data\backup\" 2>nul
    echo 已迁移: cv_algorithm_hub_backup.sql -> backup/
) else (
    echo 未找到备份文件 cv_algorithm_hub_backup.sql
)

echo.
echo 步骤 4: 创建日志文件...
echo [%date% %time%] 数据目录结构初始化完成 > K:\data\databases\logs\init.log
echo.

echo ============================================
echo 数据目录重构完成!
echo ============================================
echo.
echo 新结构:
tree K:\data\ /F 2>nul | head -50
echo.
echo 注意: postgres 数据库保持原位，路径为 K:\data\postgres
echo      这是因为 Docker 容器正在使用此数据库
echo.
pause
