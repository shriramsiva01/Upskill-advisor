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

