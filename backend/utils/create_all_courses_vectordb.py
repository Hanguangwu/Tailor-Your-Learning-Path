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
    name="all_courses_collection",
    metadata={"hnsw:space": "cosine"}  # Use cosine similarity
)

# Progress file to keep track of processed rows
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.txt")

def get_last_processed_index():
    """Get the last processed index from the progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as file:
            return int(file.read().strip())
    return -1

def update_progress(index):
    """Update the progress file with the last processed index."""
    with open(PROGRESS_FILE, 'w') as file:
        file.write(str(index))

def process_courses_file():
    """Process the Top_Courses_All.csv file and store data in the vector database"""
    # File path
    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Top_Courses_All.csv")
    
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='latin1')
        except:
            df = pd.read_csv(file_path, encoding='gbk')
    
    last_processed_index = get_last_processed_index()
    
    for index, row in df.iterrows():
        if index <= last_processed_index:
            continue  # Skip already processed rows
        
        try:
            # Extract key fields
            course_id = str(row['_id'])  # Use existing _id
            title = str(row.get('course_name', ''))
            description = str(row.get('description', ''))
            
            # Create document
            course_doc = {
                "id": course_id,
                "title": title,
                "description": description,
                "platform": row.get('platform', ''),
                "source": "Top_Courses_All.csv"
            }
            
            # Create text representation
            text_representation = f"Course Title: {title}\nDescription: {description}\nPlatform: {row.get('platform', '')}"
            
            # Generate embedding vector
            embedding = embeddings.embed_query(text_representation)
            
            # Store in ChromaDB
            collection.add(
                ids=[course_id],
                embeddings=[embedding],
                documents=[text_representation],
                metadatas=[course_doc]
            )
            
            update_progress(index)  # Update progress after successful processing
            
            if index % 100 == 0:
                print(f"Processed {index} entries from Top_Courses_All.csv")
                
        except Exception as e:
            print(f"Error processing course data (row {index}): {str(e)}")

if __name__ == "__main__":
    print("Starting to process course data and store in vector database...")
    process_courses_file()
    print(f"Processing complete. Data stored in: {CHROMA_DB_PATH}")
    print(f"Total number of courses in vector database: {collection.count()}")