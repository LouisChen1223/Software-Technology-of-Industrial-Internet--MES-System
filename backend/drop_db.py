"""
清空数据库脚本
警告：此操作将删除所有数据！
"""
from app.database import engine, Base


def drop_all_tables():
    """删除所有表"""
    response = input("警告：此操作将删除所有数据表！是否继续？(yes/no): ")
    if response.lower() != "yes":
        print("操作已取消")
        return
    
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✓ All tables dropped successfully!")


if __name__ == "__main__":
    drop_all_tables()
