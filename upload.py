import os
from dotenv import load_dotenv
import openai
import pinecone
import docx
import pandas as pd
import fitz  # PyMuPDF

load_dotenv()

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

if not OPENAI_API_KEY or not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise ValueError("Please set OPENAI_API_KEY, PINECONE_API_KEY, and PINECONE_INDEX_NAME in your .env")

openai.api_key = OPENAI_API_KEY

from pinecone import Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

def extract_text_from_file(file_path):
    try:
        if file_path.endswith(".pdf"):
            doc = fitz.open(file_path)
            return "\n".join(page.get_text() for page in doc)
        elif file_path.endswith(".docx"):
            doc = docx.Document(file_path)
            return "\n".join(para.text for para in doc.paragraphs)
        elif file_path.endswith(".doc"):
            raise ValueError(".doc files not supported. Please use .docx instead.")
        else:
            return ""
    except Exception as e:
        print(f"Error extracting text from file {file_path}: {e}")
        return ""

def extract_text_from_xlsx(xlsx_path):
    try:
        df = pd.read_excel(xlsx_path)
        return df.to_string(index=False)
    except Exception as e:
        print(f"Error extracting text from Excel file {xlsx_path}: {e}")
        return ""

def is_file_already_uploaded(chef_id, recipe_id):
    """
    Checks if any vectors exist in the index with matching chef_id and recipe_id by fetching first few vector IDs.
    """
    prefix = f"{chef_id}_{recipe_id}_"
    test_ids = [f"{chef_id}_{recipe_id}_{i}" for i in range(5)]
    resp = index.fetch(ids=test_ids)
    
    # resp.vectors is a dict keyed by vector_id
    if resp.vectors:
        return True
    return False

def chunk_text(text, max_length=1000):
    """
    Simple chunking by characters. Customize token-based chunking if needed.
    """
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

def embed_and_store(text, chef_id, recipe_id):
    chunks = chunk_text(text)
    vectors = []

    for i, chunk in enumerate(chunks):
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=chunk
        )
        embedding = response.data[0].embedding

        vector_id = f"{chef_id}_{recipe_id}_{i}"
        metadata = {
            "chef_id": chef_id,
            "recipe_id": recipe_id,
            "chunk_index": i,
            "text_snippet": chunk[:200]
        }
        vectors.append((vector_id, embedding, metadata))

    # Fetch existing vector IDs to avoid duplicates
    existing_resp = index.fetch(ids=[v[0] for v in vectors])
    existing_ids = set(existing_resp.vectors.keys())

    new_vectors = [v for v in vectors if v[0] not in existing_ids]

    if new_vectors:
        index.upsert(vectors=new_vectors)
        print(f"Upserted {len(new_vectors)} vectors for recipe '{recipe_id}' by chef '{chef_id}'.")
    else:
        print(f"All vectors for recipe '{recipe_id}' by chef '{chef_id}' are already uploaded.")

def process_and_store_file(file_path, chef_id, recipe_id):
    if is_file_already_uploaded(chef_id, recipe_id):
        print(f"Recipe '{recipe_id}' by chef '{chef_id}' already uploaded. Skipping.")
        return

    text = ""
    if file_path.endswith((".pdf", ".docx", ".doc")):
        text = extract_text_from_file(file_path)
    elif file_path.endswith(".xlsx"):
        text = extract_text_from_xlsx(file_path)
    else:
        print(f"Unsupported file type for '{file_path}'. Skipping.")
        return

    if not text.strip():
        print(f"No text extracted from '{file_path}'. Skipping.")
        return

    embed_and_store(text, chef_id, recipe_id)
    print(f"Finished processing file '{file_path}'.")

if __name__ == "__main__":
    # Example usage — replace with your file path and IDs
    process_and_store_file("sample_recipe.pdf", chef_id="chef123", recipe_id="recipe456")