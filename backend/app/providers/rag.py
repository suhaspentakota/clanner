import chromadb
from app.providers.openai import openai_embed

chroma_client = chromadb.PersistentClient(path="data/chroma")
COLLECTION_NAME = "clanner"

def ingest_documents(folder="data/documents"):
    import os
    docs=[]; metas=[]; ids=[]
    for fname in os.listdir(folder):
        if fname.endswith((".txt",".md")):
            with open(os.path.join(folder,fname),"r",encoding="utf-8") as f:
                content=f.read()
            docs.append(content); metas.append({"filename":fname}); ids.append(fname)
    if not docs: return 0
    embeddings=openai_embed(docs)
    col=chroma_client.get_or_create_collection(COLLECTION_NAME)
    col.add(documents=docs,metadatas=metas,ids=ids,embeddings=embeddings)
    return len(docs)

def retrieve(query,k=3):
    col=chroma_client.get_or_create_collection(COLLECTION_NAME)
    query_embed=openai_embed([query])[0]
    res=col.query(query_embeddings=[query_embed],n_results=k,include=["documents","metadatas"])
    return [d for d in res["documents"][0]]
