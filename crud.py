# crud.py
from sqlalchemy.orm import Session
import models as models
from typing import Dict, List

def get_students(db:Session) -> Dict[str,int]:
    # Query DB  
    print("Fetching students from DB")
    rows = db.query(models.Student).all()
    return [{"id": r.student_id, "name": r.name} for r in rows]

def get_job_role(db:Session) -> Dict[str,int]:
    # Query DB  
    rows = db.query(models.Job).all()
    return [{"id": r.job_id, "title": r.title} for r in rows]

def get_student_info(db:Session, student_id: int):
    # Mock or fetch from DB
    r = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if not r:
        return None
    return {"id": r.student_id, "name": r.name,"current_role":r.role, "max_duration_weeks":r.max_duration_weeks,"budget":r.budget} 
    
def get_student_skills(db: Session, student_id: int) -> Dict[str,int]:
    # returns dict: {skill_name: level}
    rows = db.query(models.StudentSkill).join(models.Skill).filter(models.StudentSkill.student_id == student_id).all()
    return {r.skill.name: r.level for r in rows}

def get_job_requirements(db: Session, job_id: int) -> Dict[str,int]:
    # returns dict: {skill_name: required_level}
    rows = db.query(models.JobSkill).join(models.Skill).filter(models.JobSkill.job_id == job_id).all()
    return {r.skill.name: (r.required_level if r.required_level is not None else 0) for r in rows}

def get_courses_for_skill(db: Session, skill_name: str) -> List[dict]:
    skill = db.query(models.Skill).filter(models.Skill.name == skill_name).first()
    if not skill:
        return []
    rows = db.query(models.Course).filter(models.Course.skill_id == skill.skill_id).all()
    courses = []
    for c in rows:
        courses.append({
            "course_id": c.course_id,
            "title": c.title,
            "provider": c.provider,
            "description": c.description,
            "duration": c.duration,
            "cost": float(c.cost) if c.cost is not None else None,
            "level_gain": c.level_gain
        })
    return courses
