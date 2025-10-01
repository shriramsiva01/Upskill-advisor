# crud.py
from sqlalchemy.orm import Session
#import models as models
from models import Student, Skill, StudentSkill, Job, JobSkill, Course
from typing import Dict, List

def get_students(db:Session) -> Dict[str,int]:
    # Query DB  
    print("Fetching students from DB")
    rows = db.query(Student).all()
    return [{"id": r.student_id, "name": r.name} for r in rows]

def get_job_role(db:Session) -> Dict[str,int]:
    # Query DB  
    rows = db.query(Job).all()
    return [{"id": r.job_id, "title": r.title} for r in rows]

def get_student_info(db:Session, student_id: int):
    # Mock or fetch from DB
    r = db.query(Student).filter(Student.student_id == student_id).first()
    if not r:
        return None
    return {"id": r.student_id, 
            "name": r.name,
            "role":r.role, 
            "max_duration_weeks":r.max_duration_weeks,
            "budget":r.budget} 
    
def get_student_skills(db: Session, student_id: int) -> Dict[str,int]:
    # returns dict: {skill_name: level}
    rows = db.query(StudentSkill).join(Skill).filter(StudentSkill.student_id == student_id).all()
    return {r.skill.name: r.level for r in rows}

def get_job_requirements(db: Session, job_id: int) -> Dict[str,int]:
    # returns dict: {skill_name: required_level}
    rows = db.query(JobSkill).join(Skill).filter(JobSkill.job_id == job_id).all()
    return {r.skill.name: (r.required_level if r.required_level is not None else 0) for r in rows}

# crud.py

def get_courses_for_skill(db: Session, skill_name: str) -> list[dict]:
    # Get the skill object first
    skill = db.query(Skill).filter(Skill.name == skill_name).first()
    if not skill:
        return []

    # Query all courses linked to this skill
    courses = db.query(Course).filter(Course.skill_id == skill.skill_id).all()

    result = []
    for c in courses:
        result.append({
            "id": c.course_id,
            "title": c.title,
            "provider": c.provider or "",
            "duration": c.duration or 1,      # default to 1 if None
            "cost": float(c.cost or 0.0),     # default to 0.0
            "level_gain": c.level_gain or 1,  # default to 1
        })
    return result


