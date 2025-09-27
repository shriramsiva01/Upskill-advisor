from datetime import date
from database import SessionLocal, engine
import models
import pinecone_utils 
import json

# create tables if they don't exist
models.Base.metadata.create_all(bind=engine)

def ingestCourses(course: dict, index, embeddings):
    # Convert course to a single text string for embedding
    text_for_embedding = f"{course['title']} {' '.join(course['skills'])} {' '.join(course.get('outcomes', []))}"
    # Generate embedding vector
    vector = embeddings.embed_documents([text_for_embedding])[0]  # returns list, pick first
    # Upsert into Pinecone
    index.upsert([
    {
        "id": course["course_id"],
        "values": vector,  # list of floats
        "metadata": course  # full course dict
    }
    ])


if __name__ == "__main__":
    # Init Pinecone **once**
    pinecone_utils.init_pinecone()

    # Load courses
    with open("courses.json", "r") as f:
        courses = json.load(f)

    # Ingest all courses
    for course in courses:
        embeddings = pinecone_utils.init_embeddings()
        index = pinecone_utils.get_index()
        ingestCourses(course, index, embeddings)
        print(f"Ingested course {course['course_id']} - {course['title']}")
