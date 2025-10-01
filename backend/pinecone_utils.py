import os
import json
from pinecone import Pinecone, ServerlessSpec
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Pinecone as LangchainPinecone


def init_pinecone():
    api_key = "pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ"  
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
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    index = pc.Index(index_name)
    print(f"Created new index '{index_name}' with dimension 384")


def get_index():
    api_key = "pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ"  
    index_name = "courses"
    pc = Pinecone(api_key=api_key)
    index = pc.Index(index_name)
    return index


def init_embeddings():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    return embeddings


def index_courses(courses_file="courses.json"):
    """
    Index all courses from courses.json into Pinecone, ensuring 'cost' is included.
    """
    api_key = "pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ"
    pc = Pinecone(api_key=api_key)
    index_name = "courses"

    # delete old index if exists
    if index_name in pc.list_indexes().names():
        pc.delete_index(index_name)

    # create new index
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )
    index = pc.Index(index_name)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    with open(courses_file, "r") as f:
        courses = json.load(f)

    vectors_to_upsert = []
    for course in courses:
        vector = embeddings.embed_query(" ".join(course.get("skills", [])))
        metadata = {
            "course_id": course.get("course_id"),
            "title": course.get("title"),
            "skills": course.get("skills", []),
            "duration_weeks": course.get("duration_weeks", 1),
            "cost": course.get("cost") if course.get("cost") is not None else 0,  # ✅ default 0
            "difficulty": course.get("difficulty", ""),
            "prerequisites": course.get("prerequisites", []),
            "outcomes": course.get("outcomes", [])
        }
        vectors_to_upsert.append((course["course_id"], vector, metadata))

    index.upsert(vectors_to_upsert)
    print(f"Indexed {len(vectors_to_upsert)} courses with cost")


def get_courses_for_skill(skill: str, index, embeddings, top_k: int = 3):
    LangchainPinecone.init(
        api_key="pcsk_7Ri7rG_TouyZkFuYvRd2HHr3frDgdX3knftcNsJzNMw1pmKPgri3dEqitRPFBwLcua6zeJ",
        environment="us-east-1"
    )
    vectorstore = LangchainPinecone.from_existing_index(index_name=index, embedding=embeddings)

    results = vectorstore.similarity_search(skill, k=top_k)

    courses = []
    for r in results:
        meta = r.metadata
        courses.append({
            "course_id": meta.get("course_id"),
            "title": meta.get("title"),
            "provider": meta.get("provider", ""),
            "description": meta.get("description", ""),
            "duration_weeks": meta.get("duration_weeks") if meta.get("duration_weeks") is not None else 1,
            "cost": meta.get("cost") if meta.get("cost") is not None else 0,  # ✅ default 0
            "skills": meta.get("skills", []),
            "level_gain": meta.get("level_gain") if meta.get("level_gain") is not None else 1
        })
    return courses
