# models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from database import Base
from typing import List, Dict, Optional

class Student(Base):
    __tablename__ = "student"
    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    enrollment_date = Column(Date, nullable=True)
    max_duration_weeks = Column(Integer, nullable=False, default=24)
    budget = Column(DECIMAL(10,2), nullable=False, default=1000.0)
    role = Column(String(50), nullable=False) 
    skills = relationship("StudentSkill", back_populates="student", cascade="all, delete-orphan")

class Skill(Base):
    __tablename__ = "skill"
    skill_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

class StudentSkill(Base):
    __tablename__ = "student_skill"
    student_id = Column(Integer, ForeignKey("student.student_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), primary_key=True)
    level = Column(Integer, nullable=False)
    student = relationship("Student", back_populates="skills")
    skill = relationship("Skill")

class Job(Base):
    __tablename__ = "job"
    job_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)
    jd_text = Column(Text, nullable=True)

class JobSkill(Base):
    __tablename__ = "job_skill"
    job_id = Column(Integer, ForeignKey("job.job_id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), primary_key=True)
    required_level = Column(Integer, nullable=True)
    job = relationship("Job", backref="job_skills")
    skill = relationship("Skill")

class Course(Base):
    __tablename__ = "course"
    course_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)       # store in hours or weeks
    cost = Column(DECIMAL(10,2), nullable=True)
    level_gain = Column(Integer, nullable=True)     # expected skill level improvement
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), nullable=False)
    prerequisites= Column(String(200), nullable=False)
    outcomes= Column(String(200), nullable=False)
    skill = relationship("Skill")
