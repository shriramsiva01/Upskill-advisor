# main.py
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from fastapi.responses import Response
import models as models, crud
from database import get_db, engine
import pinecone_utils
import re
import time
from pinecone_utils import get_courses_for_skill
# ensure tables exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Upskill Advisor (dev)")
    
# Development CORS - allow frontend dev origin(s)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/students", tags=["Students"], summary="Get all students")
def students(db: Session = Depends(get_db)):
    """
    Returns a list of all students.
    """
    return crud.get_students(db)

@app.get("/job_roles",  tags=["Jobs"], summary="Get all job roles")
def job_roles(db: Session = Depends(get_db)):
    """
    Returns a list of all job roles.
    """
    return crud.get_job_role(db)

@app.get("/student_info", tags=["Students"], summary="Get student information")
def student_info(student_id: int, db: Session = Depends(get_db)):
    """
    Returns information about students providing details on their current role, the time and cost they can spare to upgrade.
    """
    info = crud.get_student_info(db, student_id)
    if not info:
        raise HTTPException(status_code=404, detail="Student not found")
    return {
        "student_name": info.get("name"),
        "role": info.get("role"),
        "max_duration_weeks": info.get("max_duration_weeks"),
        "budget": info.get("budget"),
    }

@app.api_route("/skill_gap/{student_id}/{job_id}", methods=["GET", "POST"], tags=["Skill Gap"],
    summary="Get skill gap for a student for a specific job")
def skill_gap(student_id: int, job_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Calculates the skill gap for a student for a specific job.
    """
    print(f"Received {request.method} /skill_gap/{student_id}/{job_id}")
    student_skills = crud.get_student_skills(db, student_id)
    student_info = crud.get_student_info(db, student_id)
    job_reqs = crud.get_job_requirements(db, job_id)
    skill_gap_list = []
    for skill, required in job_reqs.items():
        current = student_skills.get(skill, 0)
        gap = required - current
        skill_gap_list.append({
            "skill": skill,
            "student_level": current,
            "required_level": required,
            "gap": gap
        })
    return {
        "student_id": student_id,
        "student_name": student_info["name"] if student_info else None,
        "job_id": job_id,
        "skill_gap": skill_gap_list
    }
    


def format_llm_reasoning(raw_text: str) -> str:
    # Remove "Based on the provided data" section if too long
    raw_text = re.sub(r"Based on the provided data:.*?(?=\d\.)", "", raw_text, flags=re.S)

    # Replace * with bullets
    formatted = raw_text.replace("* ", "• ")

    # Optionally shorten intro phrases
    formatted = formatted.replace("In summary, I recommend", "Recommended")

    return formatted.strip()
    
def compute_topk_coverage(job_requirements: dict, recommendations: list, k: int = 3) -> float:
    """Compute Top-K Skill Coverage metric using course 'skills' lists."""
    jd_skills = set(job_requirements.keys())
    if not jd_skills:
        return 0.0

    # Take the first K recommended courses
    topk_courses = recommendations[:k]

    # Collect all skills these courses cover
    topk_skills = set()
    for course in topk_courses:
        for s in course.get("skills", []):   # 'skills' is a list
            topk_skills.add(str(s))          # force into string, safe

    return round(len(jd_skills & topk_skills) / len(jd_skills), 3)
    
    
# accept GET and POST so method mismatches don't cause errors
@app.api_route("/advise/{student_id}/{job_id}", methods=["GET", "POST"], tags=["Advice"],
    summary="Get personalized advice for a student for a job")
def advise(student_id: int, job_id: int, request: Request, db: Session = Depends(get_db)):
    """
    Returns personalized advice for a student to bridge the skill gap for a job leveraging Llama3 local LLM.
    """
    start_time = time.perf_counter()   # ✅ start timer

    print(f"Received {request.method} /advise/{student_id}/{job_id}")
    student_skills = crud.get_student_skills(db, student_id)
    student_info = crud.get_student_info(db, student_id)
    job_reqs = crud.get_job_requirements(db, job_id)

    if not job_reqs:
        raise HTTPException(status_code=404, detail="Job or job skills not found")

    embeddings = pinecone_utils.init_embeddings()
    index = pinecone_utils.get_index()
    
    recommendations = []
    for skill, required in job_reqs.items():
        current = student_skills.get(skill, 0)
        gap = required - current
        if gap > 0:
            # Retrieve candidate courses that teach this skill
            #query_text = f"{skill} level {gap}"  # simple semantic query
            query_text = f"{skill}"  # simple semantic query

            query_vector = embeddings.embed_query(query_text)
            print(f"Querying Pinecone for skill '{skill}' gap {gap}")
            # Query Pinecone for top 5 matching courses
            results = index.query(
                vector=query_vector,
                top_k=5,
                include_metadata=True
            )
            print(f"Skill '{skill}' gap {gap}, found {len(results['matches'])} courses")
            # Filter by student's available time and budget
            suitable_courses = [
                r.metadata for r in results["matches"]
                if r.metadata["duration_weeks"] <= student_info["max_duration_weeks"]
                #and r.metadata["cost"] <= student_info["budget"]
            ]

            # Add to recommendations
            recommendations.extend(suitable_courses)

    print(recommendations)
    '''
    all_courses = []
    for skill, target in job_reqs.items():
        current = student_skills.get(skill, 0)
        gap = target - current
        if gap > 0:
            # Retrieve candidate courses that teach this skill
            print(f"Getting courses for skill from pinecone")
            courses = get_courses_for_skill(skill, index, embeddings)
            for c in courses:
                c["score"] = round((c["level_gain"] or 1) / ((c["duration"] or 1) * float(c["cost"] or 1)), 6)
                all_courses.append(c)

    unique_courses = {c["course_id"]: c for c in all_courses}.values()
    course_path = list(unique_courses)
    '''
    
    coverage_at3 = compute_topk_coverage(job_reqs, recommendations, k=3)
    llm_start_time = time.perf_counter()   # ✅ start timer
    # LLM reasoning is optional; don't fail if not configured
    llm_text = "LLM not configured or failed"
    try:
        from langchain_community.chat_models import ChatOllama
        from langchain.prompts import ChatPromptTemplate
        llm = ChatOllama(model="llama3")
        prompt = ChatPromptTemplate.from_template(
            "The student has the following skills: {student}. "
            "The target job requires: {job}. "
            "We analyzed the gaps and found these detailed course recommendations per skill: {recommendations}. "
            #"The overall course path we can take is: {course_path}. "
            "Suggest the best sequence of courses from the overall path that will efficiently close the gaps, "
            "minimizing cost and time, and explain why."
        )

        print("LLM initialized")
        chain = prompt | llm
        
        print(f"Invoking LLM with student skills {student_skills}, job {job_reqs}, courses {recommendations}")
        # try synchronous invoke; if async in your environment you'll need to await
        llm_resp = chain.invoke({
            "student": student_skills,
            "job": job_reqs,
            #"course_path": course_path,
            "recommendations": recommendations
        })
        llm_text = getattr(llm_resp, "content", str(llm_resp))
        print("LLM response received - evaluating coverage metric")
        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)   # in milliseconds
        llm_latency_ms = round((end_time - llm_start_time) * 1000, 2)
        result= {
        "student": {"id": student_id, "skills": student_skills},
        "job": {"id": job_id, "required_skills": job_reqs},
        "course_path": recommendations if recommendations else [],
        "llm_reasoning": format_llm_reasoning(llm_text),
        "top3_coverage metric": coverage_at3,
        "backend_latency_ms": latency_ms,
        "llm_latency_ms": llm_latency_ms
        }
        #print("LLM response:", format_llm_reasoning(llm_text))
    except Exception as e:
        print("LLM disabled or error:", e)

    return result




'''
@app.get("/report/{student_id}/{job_id}")
def report_pdf(student_id: int, job_id: int, db: Session = Depends(get_db)):
    student_skills = crud.get_student_skills(db, student_id)
    job_reqs = crud.get_job_requirements(db, job_id)
    if not job_reqs:
        raise HTTPException(status_code=404, detail="Job or job skills not found")

    recommendations = []
    for skill, required in job_reqs.items():
        current = student_skills.get(skill, 0)
        gap = required - current
        if gap > 0:
            courses = crud.get_courses_for_skill(db, skill)
            for c in courses:
                dur = c.get("duration") or 1
                cost = c.get("cost") or 1.0
                lg = c.get("level_gain") or 1
                try:
                    c["score"] = round((lg) / (dur * float(cost)), 6)
                except Exception:
                    c["score"] = 0.0
            recommendations.append({"skill": skill, "gap": gap, "courses": courses})

    # PDF creation
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750
    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Upskill Advisor - Recommendation Report")
    y -= 30
    c.setFont("Helvetica", 12)
    c.drawString(40, y, f"Student ID: {student_id}")
    y -= 20

    c.drawString(40, y, "Student Skills:")
    y -= 18
    for k, v in student_skills.items():
        c.drawString(50, y, f"- {k}: {v}")
        y -= 14
        if y < 80:
            c.showPage(); y = 750

    y -= 6
    c.drawString(40, y, "Job Requirements:")
    y -= 18
    for k, v in job_reqs.items():
        c.drawString(50, y, f"- {k}: {v}")
        y -= 14
        if y < 80:
            c.showPage(); y = 750

    y -= 6
    c.drawString(40, y, "Recommendations:")
    y -= 18
    for rec in recommendations:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(45, y, f"{rec['skill']} (Gap: {rec['gap']})")
        y -= 16
        c.setFont("Helvetica", 10)
        for course in rec.get("courses", []):
            line = f" - {course.get('title','')} ({course.get('provider','')}) | dur: {course.get('duration')} | cost: {course.get('cost')} | score: {course.get('score')}"
            c.drawString(55, y, line[:120])
            y -= 12
            if y < 80:
                c.showPage(); y = 750

    c.showPage()
    c.save()
    buffer.seek(0)
    return Response(content=buffer.read(), media_type="application/pdf")
    '''
