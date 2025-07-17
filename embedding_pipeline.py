import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

load_dotenv()

CSV_PATH = os.getenv("CSV_PATH")
CHROMA_DB_DIR = os.getenv("CHROMA_DB_DIR")
MODEL_NAME = os.getenv("MODEL_NAME")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
OVERLAP = int(os.getenv("OVERLAP"))

df = pd.read_csv(CSV_PATH)
df.fillna("", inplace=True) 

def create_chunks(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)


chroma_client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = chroma_client.get_or_create_collection(name="faq_embeddings", embedding_function=embedding_fn)


doc_id = 0
for idx, row in tqdm(df.iterrows(), total=len(df)):
    question = row['Questions']
    answer = row['Answers']
    

    full_text = f"Sual: {question}\nCavab: {answer}"
    

    chunks = create_chunks(full_text)

    for chunk in chunks:
        doc_id += 1
        collection.add(
            documents=[chunk], 
            metadatas=[{
                "question": question  
            }],
            ids=[f"doc_{doc_id}"]
        )

print("Embeddings stored OK.")
