import os 
from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings import HuggingFaceEmbeddings
#from langchain.vectorstores import Pinecone

def init_pinecone():
    api_key =  "pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ"  
    pc = Pinecone(api_key=api_key)
    index_name = "courses"
    if index_name in pc.list_indexes().names():
        print(f"Deleting old index '{index_name}' with wrong dimension...")
        pc.delete_index(index_name)

    if index_name not in pc.list_indexes().names():
        pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    index = pc.Index(index_name)
    print(f"Created new index '{index_name}' with dimension 384")
    
def get_index():
    api_key =  "pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ"  
    index_name = "courses"
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    return index
    
def init_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings
    
    

