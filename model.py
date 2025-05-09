import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

load_dotenv()
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

model = SentenceTransformer("intfloat/e5-large-v2")

def embed(text: str):
    return model.encode(text).tolist()

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("cocktails-index")