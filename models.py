from datetime import datetime
from typing import List, Optional

from pytz import timezone
from pydantic import BaseModel
from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, SQLModel


KST = timezone("Asia/Seoul")


class Patient(SQLModel, table=True):
    __tablename__ = "patients"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field()
    patient_diagnosis: str = Field()
    clinical_assessment: str = Field()
    birthday: str = Field()
    weight: float = Field()
    medical_history: List[str] = Field(sa_column=Column(JSON))
    recent_weight_change: Optional[str] = Field()
    is_taking_drug_for_hypertension: bool = Field()
    is_taking_drug_for_diabetes_mellitus: bool = Field()
    is_surgical_history: bool = Field()
    is_food_allergy: bool = Field()
    is_drug_allergy: bool = Field()
    is_family_history: bool = Field()
    is_drinking_alcohol: bool = Field()
    is_smoking: bool = Field()
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))


class QuestionBase(BaseModel):
    symptom: str = Field(
        description="This column specifies the medical condition associated with the patient. It serves as a context for the questions and information gathered, for example, 'Type 2 diabetes mellitus' or 'Acute myocarditis'."
    )

    category: Optional[str] = Field(
        description='This column categorizes the type of information being gathered about the patient. Categories include "past medical history," "medications," "lifestyle," "family history," and "allergy". These categories help in organizing the data according to the nature of the medical inquiry.'
    )
    subcategory: Optional[str] = Field(
        description="This column pinpoints a more detailed aspect of the category. For instance, under the category 'past medical history,' the specific item might be 'family history of diabetes' or 'autoimmune diseases,' which helps focus the subsequent question on a particular detail relevant to the patient's condition or health history."
    )

    question: Optional[str] = Field(
        description='This column contains the specific questions posed to the patient, which relate to the diagnosis and specific item. Questions are tailored to extract precise and necessary information from the patient, such as "Do you have any history of autoimmune diseases?" or "Have you ever been diagnosed with human papillomavirus (HPV)?"'
    )

    question_korean: Optional[str] = Field(
        description="This is the Korean translation of the English questions in the previous column. This dual-language setup indicates that the data might be used in a bilingual medical setting, allowing for better communication with patients who prefer Korean."
    )


class QuestionBaseList(SQLModel):
    questions: List[QuestionBase]


class Question(QuestionBase, SQLModel, table=True):
    __tablename__ = "questions"
    id: Optional[int] = Field(default=None, primary_key=True)
    source: Optional[str] = Field(
        description="A field to store the origin of the question."
    )
    is_relevant: Optional[bool] = Field(
        description="A field to store the relevancy of the question."
    )
    labeler: Optional[str] = Field(
        description="A field to store the name of the person who labeled the question."
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(KST))


if __name__ == "__main__":
    from sqlmodel import create_engine

    sqlite_db = "database.sqlite"
    sqlite_url = f"sqlite:///{sqlite_db}"
    engine = create_engine(sqlite_url)
    SQLModel.metadata.create_all(engine)
