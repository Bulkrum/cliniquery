from typing import Dict

from sqlmodel import Sequence, Session, create_engine, select

from models import Patient, Question


def load_patients(sqlite_name: str = "database.sqlite") -> Sequence[Patient]:
    sqlite_db = sqlite_name
    sqlite_url = f"sqlite:///{sqlite_db}"
    engine = create_engine(sqlite_url)
    session = Session(engine)

    query_for_patient = select(Patient)
    patients = session.exec(query_for_patient).all()

    session.close()

    return patients


def add_symptom(data: Dict, sqlite_name: str = "database.sqlite"):
    sqlite_db = sqlite_name
    sqlite_url = f"sqlite:///{sqlite_db}"
    engine = create_engine(sqlite_url)
    session = Session(engine)

    new_question = Question(**data)
    session.add(new_question)
    session.commit()
    session.close()


if __name__ == "__main__":
    add_symptom(
        {
            "symptom": "test",
            "category": "Medical history",
            "subcategory": "Cervical Cancer Screening",
            "question": "test",
            "question_korean": "test",
            "is_relevant": False,
            "source": "test",
            "labeler": "test",
        }
    )
