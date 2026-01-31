# -*- coding: utf-8 -*-
import os
import shutil
import time

def migrate_postgres_data():
    source = "K:/data/postgres"
    target_dir = "K:/data/databases/users"
    target = os.path.join(target_dir, "postgres")

    print("=" * 50)
    print("数据目录迁移脚本")
    print("=" * 50)

    # 检查源目录
    if not os.path.exists(source):
        print(f"错误: 源目录不存在: {source}")
        return False

    print(f"\n源目录: {source}")
    print(f"目标目录: {target}")

    # 创建目标目录
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"已创建目录: {target_dir}")

    # 检查目标是否已存在
    if os.path.exists(target):
        print(f"目标目录已存在，将先删除...")
        shutil.rmtree(target)
        time.sleep(1)

    print(f"\n正在复制数据...")
    print("这可能需要几分钟，请耐心等待...")

    try:
        # 复制目录
        shutil.copytree(source, target)
        print(f"\n[成功] 复制成功!")

        # 验证复制
        if os.path.exists(os.path.join(target, "PG_VERSION")):
            print("[成功] PG_VERSION 文件验证成功")

            # 列出一些关键文件
            print("\n关键文件列表:")
            key_files = ["PG_VERSION", "postgresql.conf", "postgresql.auto.conf"]
            for f in key_files:
                fp = os.path.join(target, f)
                if os.path.exists(fp):
                    print(f"  [OK] {f}")

            # 删除源目录
            print(f"\n正在删除源目录...")
            time.sleep(2)
            shutil.rmtree(source)
            print("[成功] 源目录已删除")

            print("\n" + "=" * 50)
            print("迁移完成!")
            print("=" * 50)
            print(f"\n新目录结构:")
            print(f"  K:/data/")
            print(f"  ├── databases/")
            print(f"  │   └── users/")
            print(f"  │       └── postgres/  <-- 数据已移到这里")
            print(f"  └── backup/")
            print(f"\nDocker 配置已更新:")
            print(f"  K:/data/databases/users/postgres:/var/lib/postgresql/data")
            print("\n请重启 Docker 容器进行测试!")

            return True
        else:
            print("[错误] 验证失败: PG_VERSION 文件不存在")
            return False

    except Exception as e:
        print(f"错误: {e}")
        return False

if __name__ == "__main__":
    success = migrate_postgres_data()
    exit(0 if success else 1)
