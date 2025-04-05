import os
import pandas as pd
import chromadb
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from getOpenAIAPIKey import get_chatanywhere_api_key, get_chatanywhere_url

# Load environment variables
load_dotenv()

# Initialize embeddings model
embeddings = OpenAIEmbeddings(
    api_key=get_chatanywhere_api_key(),
    base_url=get_chatanywhere_url()
)

# Initialize ChromaDB client
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
os.makedirs(CHROMA_DB_PATH, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

# Create or get collection
collection = chroma_client.get_or_create_collection(
    name="category_collection",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)

def process_category_files():
    """Process all files in the Category_Tables directory and store them in the vector database"""
    # Data directory
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Category_Tables")
    
    # Iterate over each file in the directory
    for file_name in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file_name)
        if os.path.isfile(file_path):
            print(f"Processing data: {file_path}")
            process_data(file_path)

def process_data(file_path):
    """Process data from a given file"""
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    
    for index, row in df.iterrows():
        try:
            # Extract key fields
            category_id = f"category_{index}"
            title = str(row.get('title', '')) if 'title' in df.columns else str(row.get('name', ''))
            description = str(row.get('description', '')) if 'description' in df.columns else ''
            
            # Create document
            category_doc = {
                "id": category_id,
                "title": title,
                "description": description,
                "source": os.path.basename(file_path)
            }
            
            # Create text representation
            text_representation = f"Title: {title}\nDescription: {description}\nSource: {os.path.basename(file_path)}"
            
            # Generate embedding vector
            embedding = embeddings.embed_query(text_representation)
            
            # Store in ChromaDB
            collection.add(
                ids=[category_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[category_doc]
            )
            
            if index % 100 == 0:
                print(f"Processed {index} entries from {os.path.basename(file_path)}")
                
        except Exception as e:
            print(f"Error processing data (row {index}): {str(e)}")

if __name__ == "__main__":
    print("Starting to process category data and store in vector database...")
    process_category_files()
    print(f"Processing complete. Data stored in: {CHROMA_DB_PATH}")
    print(f"Total number of categories in vector database: {collection.count()}")