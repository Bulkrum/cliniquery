import os
import ell
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlmodel import Field, SQLModel, Session, select
from dotenv import load_dotenv
import tqdm


load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

ell.init(store="./log")


class SpecificQuestion(BaseModel):
    category: str = Field(
        description='The `category` can be the following values: "Chief complaint", "Medical history", "Family history", "Allergy", "Surgical history", "Lifestyle", "Medication", and "Review of system'
    )
    keyword: str = Field(description="Keyword for the question.")
    question: str = Field(description="The actual question in Korean.")


class ListOfQuestions(BaseModel):
    questions: List[SpecificQuestion]


class Question(SQLModel, table=True):
    __tablename__ = "questions"
    id: Optional[int] = Field(
        None,
        description="Primary key for the questions table, auto-incremented.",
        primary_key=True,
    )
    diagnosis_code_id: Optional[int] = Field(
        None, description="Foreign key reference to diagnosis_codes table."
    )
    category: Optional[str] = Field(None, description="Category of the question.")
    keyword: Optional[str] = Field(None, description="Keyword for the question.")
    question: Optional[str] = Field(None, description="The actual question.")
    is_valid: Optional[bool] = Field(None, description="Validity flag of the question.")
    reason: Optional[str] = Field(
        None, description="Reason for the question being invalid (if applicable)."
    )


class DiagnosisCode(SQLModel, table=True):
    __tablename__ = "diagnosis_codes"
    id: int = Field(default=None, primary_key=True)
    usage_flag: Optional[str] = None
    usage_level: Optional[int] = None
    group_code: Optional[str] = None
    code_level_1: Optional[str] = None
    dx_kor_level_1: Optional[str] = None
    dx_en_level_1: Optional[str] = None
    code_level_2: Optional[str] = None
    dx_kor_level_2: Optional[str] = None
    dx_en_level_2: Optional[str] = None
    code_level_3: Optional[str] = None
    dx_kor_level_3: Optional[str] = None
    dx_en_level_3: Optional[str] = None
    code_level_4: Optional[str] = None
    dx_kor_level_4: Optional[str] = None
    dx_en_level_4: Optional[str] = None
    code_level_5: Optional[str] = None
    dx_kor_level_5: Optional[str] = None
    dx_en_level_5: Optional[str] = None
    code_level_6: Optional[str] = None
    dx_kor_level_6: Optional[str] = None
    dx_en_level_6: Optional[str] = None


prompt = """
I want to create a disease specific patient survey question for history and physical examination.

The disease database I have has the following table.

```sql
CREATE TABLE "public"."diagnosis_codes" (
    "id" int4 NOT NULL DEFAULT nextval('diagnosis_codes_id_seq'::regclass),
    "usage_flag" varchar,
    "usage_level" int4,
    "group_code" varchar,
    "code_level_1" varchar,
    "dx_kor_level_1" varchar,
    "dx_en_level_1" varchar,
    "code_level_2" varchar,
    "dx_kor_level_2" varchar,
    "dx_en_level_2" varchar,
    "code_level_3" varchar,
    "dx_kor_level_3" varchar,
    "dx_en_level_3" varchar,
    "code_level_4" varchar,
    "dx_kor_level_4" varchar,
    "dx_en_level_4" varchar,
    "code_level_5" varchar,
    "dx_kor_level_5" varchar,
    "dx_en_level_5" varchar,
    "code_level_6" varchar,
    "dx_kor_level_6" varchar,
    "dx_en_level_6" varchar,
    PRIMARY KEY ("id")
);
```

Here is an example of the following query.

```sql
SELECT *
from "public".diagnosis_codes
where dx_kor_level_3 like '%암%';
```

```json
[
  {
    "id": 1697,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.0-D01.4",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.1",
    "dx_kor_level_4": "직장구불결장접합부의 제자리암종",
    "dx_en_level_4": "Carcinoma in situ of rectosigmoid junction",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1698,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.0-D01.4",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.2",
    "dx_kor_level_4": "직장의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of rectum",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1699,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.0-D01.4",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.3",
    "dx_kor_level_4": "항문 및 항문관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of anus and anal canal",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1700,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.0-D01.4",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.4",
    "dx_kor_level_4": "기타 및 상세불명 부분의 장의 제자리암종",
    "dx_en_level_4": "Carcinoma in situ of other and unspecified parts of intestine",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1701,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1702,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "D01.50",
    "dx_kor_level_5": "간의 제자리암종",
    "dx_en_level_5": "Carcinoma in situ of liver",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1703,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "D01.51",
    "dx_kor_level_5": "담낭의 제자리암종",
    "dx_en_level_5": "Carcinoma in situ of gallbladder",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1704,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "D01.52",
    "dx_kor_level_5": "담관의 제자리암종",
    "dx_en_level_5": "Carcinoma in situ of bile ducts",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1705,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "D01.53",
    "dx_kor_level_5": "파터팽대의 제자리암종",
    "dx_en_level_5": "Carcinoma in situ of ampulla of Vater",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  },
  {
    "id": 1706,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.5",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.5",
    "dx_kor_level_4": "간, 담낭 및 담관의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of liver, gallbladder and bile ducts",
    "code_level_5": "D01.59",
    "dx_kor_level_5": "상세불명의 간담도계의 제자리암종",
    "dx_en_level_5": "Carcinoma in situ of hepatobiliary system, unspecified",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
  }
]
```

You will be receiving a row from the `diagnosis_codes` table. You need to create a list of questions that should be asked to the patient based on the diagnosis. The questions should be in Korean. Here is an example of the input and the output. The `category` can be the following values: "Chief complaint", "Medical history", "Family history", "Allergy", "Surgical history", "Lifestyle", "Medication", and "Review of system".

```input
{
    "id": 1698,
    "usage_flag": "1",
    "usage_level": 4,
    "group_code": "D01.0-D01.4",
    "code_level_1": "C00-D48",
    "dx_kor_level_1": "신생물(C00-D48)",
    "dx_en_level_1": "Neoplasms(C00-D48)",
    "code_level_2": "D00-D09",
    "dx_kor_level_2": "제자리신생물(D00-D09)",
    "dx_en_level_2": "In situ neoplasms(D00-D09)",
    "code_level_3": "D01",
    "dx_kor_level_3": "기타 및 상세불명의 소화기관의 제자리암종",
    "dx_en_level_3": "Carcinoma in situ of other and unspecified digestive organs",
    "code_level_4": "D01.2",
    "dx_kor_level_4": "직장의 제자리암종 ",
    "dx_en_level_4": "Carcinoma in situ of rectum",
    "code_level_5": "",
    "dx_kor_level_5": "",
    "dx_en_level_5": "",
    "code_level_6": "",
    "dx_kor_level_6": "",
    "dx_en_level_6": ""
}
```

```output
[
    {
        "category": "Medical history",
        "keyword": "colonoscopy",
        "question": "대장내시경 검사를 해보셨나요?"
    },
    {
        "category": "Medical history",
        "keyword": "colonoscopy",
        "question": "대장내시경 검사를 해보셨나요?"
    },
    {
        "category": "Review of system",
        "keyword": "Stool caliber change",
        "question": "대변 굵기 변화"
    },
    {
        "category": "Review of system",
        "keyword": "Anal pain",
        "question": "항문 통증"
    },
    {
        "category": "Review of system",
        "keyword": "Pruritis ani",
        "question": "항문 가려움"
    },
    {
        "category": "Review of system",
        "keyword": "Tenesmus",
        "question": "후중감(항문이나 직장에 무언가 남아있는 것 같은 불편한 느낌)"
    },
    {
        "category": "Review of system",
        "keyword": "Discharge(soiling)",
        "question": "대변이 묻어나오는 증상"
    },
    {
        "category": "Review of system",
        "keyword": "Prolapsed anal mass",
        "question": "항문 종괴 돌출"
    },
    {
        "category": "Review of system",
        "keyword": "Urinary incontinence",
        "question": "요실금"
    },
    {
        "category": "Review of system",
        "keyword": "Fecal incontinence",
        "question": "변실금"
    }
]
```

Avoid common questions that should be asked for every patient regardless of the diagnosis. For example, "Do you have any allergies?" or "Do you have any family history of diseases?" are not relevant to the diagnosis of "직장의 제자리암종". Here are some list of common questions that should be avoided.

Colonoscopy	대장내시경 검사를 해보셨나요?
Colonoscopy	마지막 대장내시경은 언제하셨나요?
Colonoscopy	마지막 대장내시경의 결과는 어땠나요?
Stool caliber change	대변 굵기 변화
Anal pain	항문 통증
Pruritis ani	항문 가려움
Tenesmus	후중감(항문이나 직장에 무언가 남아있는 것 같은 불편한 느낌)
Discharge(soiling)	대변이 묻어나오는 증상
Prolapsed anal mass	항문 종괴 돌출
Urinary incontinence	요실금
Fecal incontinence	변실금
Chief complaint	병원에 방문하게된 가장 큰 이유가 무엇인가요?
Duration	해당 증상은 언제부터 시작되었나요?
Hypertension	고혈압을 진단 받은 적이 있나요?
Diabetes mellitus	당뇨를 진단 받은 적이 있나요?
Hepatitis	간염을 진단 받은 적이 있나요?
Pulmonary tuberculosis	결핵을 진단 받은 적이 있나요?
Cerebrovascular accident(CVA)	뇌졸중을 진단 받은 적이 있나요?
Cardiovascular disease	심혈관 질환을 진단 받은 적이 있나요?
Others	이외에 의료진에게 알려주고 싶은 질환이 있나요?
Surgical history	수술을 받은 적이 있나요?
Surgical history	어떤 수술을 받으셨나요?
Surgical history	수술 받은 이유가 무엇인가요?
Surgical history	언제 수술을 받으셨나요?
Drug allergy	약물 알레르기가 있나요?
Food allergy	음식 알레르기가 있나요?
Current Medication	현재 복용 중이신 약이 있나요?
Past Medication(1year)	최근 1년간 처방받은 약을 알려주세요.
Family history	가족 병력이 있나요?
Family history	가족 병력에 대해 자세히 알려주세요.
Alcohol	음주를 하시나요?
Alcohol	1주일에 몇 회 하시나요?
Alcohol	어떤 종류의 술을 얼마만큼 마시는지 알려주세요.
Smoking	흡연을 하시나요?
Weight	체중이 어떻게 되시나요?
Weight change	최근 체중의 변화가 있었나요?
General weakness	전신 쇠약감
Easy fatigue	쉽게 피로해짐
Fever	열이 남
Chill	몸이 참
Headache	두통
Dizziness	어지러움
Insomnia	불면증
Cough	기침
Sputum	가래
Dyspnea	숨이 참
DOE	운동 시 숨이 참
Chest pain	가슴 통증
Palpitation	두근거림
Hemoptysis	객혈
Hematemesis	토혈
Anorexia	무기력증
Nausea	멀미
Vomiting	구토
Constipation	변비
Diarrhea	설사
Abdominal pain	복통
Abdominal discomfort	복부 불편감
Hematochezia	혈변
Melena	흑색변
Dysuria	소변 시 통증
Oliguria	소변량 감소
Hematuria	혈뇨
Poor oral intake	식욕부진
Others	기타 증상
"""


@ell.complex(model="gpt-4o-mini", response_format=ListOfQuestions)
def generate_question(diagnosis_code_str: str) -> ListOfQuestions:
    return [ell.system(prompt), ell.user(diagnosis_code_str)]


if __name__ == "__main__":
    with Session(engine) as session:
        statement = (
            select(DiagnosisCode)
            .where(DiagnosisCode.code_level_4 == "")
            .where(
                DiagnosisCode.id.not_in(select(Question.diagnosis_code_id).distinct())
            )
        )
        diagnosis = session.exec(statement).all()

    with Session(engine) as session:
        for d in tqdm.tqdm(diagnosis):
            questions = generate_question(d.model_dump_json())
            for sq in questions.parsed.questions:
                q = Question(
                    diagnosis_code_id=d.id,
                    category=sq.category,
                    keyword=sq.keyword,
                    question=sq.question,
                )
                session.add(q)
            session.commit()
