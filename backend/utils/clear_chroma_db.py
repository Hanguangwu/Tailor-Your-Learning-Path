import chromadb
import os

# 初始化 ChromaDB 客户端
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

def list_collections():
    """列出所有集合"""
    collection_names = chroma_client.list_collections()
    print("现有集合:")
    for i, name in enumerate(collection_names):
        print(f"{i+1}. {name}")
    return collection_names

def delete_collection(collection_name):
    """删除指定的集合"""
    try:
        chroma_client.delete_collection(collection_name)
        print(f"成功删除集合: {collection_name}")
        return True
    except Exception as e:
        print(f"删除集合时出错: {str(e)}")
        return False

def clear_collection(collection_name):
    """清空集合中的所有数据但保留集合"""
    try:
        collection = chroma_client.get_collection(collection_name)
        # 获取所有文档ID
        ids = collection.get()["ids"]
        if ids:
            # 删除所有文档
            collection.delete(ids)
            print(f"成功清空集合 '{collection_name}' 中的 {len(ids)} 条数据")
        else:
            print(f"集合 '{collection_name}' 中没有数据")
        return True
    except Exception as e:
        print(f"清空集合时出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("ChromaDB 管理工具")
    print("=" * 50)
    
    collections = list_collections()
    
    if not collections:
        print("没有找到任何集合")
        exit(0)
    
    choice = input("\n请选择操作:\n1. 删除特定集合\n2. 清空特定集合内容\n请输入选项 (1/2): ")
    
    if choice == "1":
        index = input(f"请输入要删除的集合序号 (1-{len(collections)}): ")
        try:
            index = int(index) - 1
            if 0 <= index < len(collections):
                confirm = input(f"确定要删除集合 '{collections[index]}' 吗? (y/n): ")
                if confirm.lower() == 'y':
                    delete_collection(collections[index])
            else:
                print("无效的序号")
        except ValueError:
            print("请输入有效的数字")
    
    elif choice == "2":
        index = input(f"请输入要清空的集合序号 (1-{len(collections)}): ")
        try:
            index = int(index) - 1
            if 0 <= index < len(collections):
                confirm = input(f"确定要清空集合 '{collections[index]}' 中的所有数据吗? (y/n): ")
                if confirm.lower() == 'y':
                    clear_collection(collections[index])
            else:
                print("无效的序号")
        except ValueError:
            print("请输入有效的数字")
    
    else:
        print("无效的选项")