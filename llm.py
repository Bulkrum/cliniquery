import json
import os
from typing import List, Optional

import ell
import tqdm
from dotenv import load_dotenv
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlmodel import Field, Session, SQLModel, select

load_dotenv()

DB_URL = os.getenv("DB_URL")
engine = create_engine(DB_URL)

# ell.init(store="./log")


class SpecificQuestion(BaseModel):
    category: str = Field(
        description='The `category` can be the following values: "Chief complaint", "Medical history", "Family history", "Allergy", "Surgical history", "Lifestyle", "Medication", and "Review of system'
    )
    keyword: str = Field(description="Keyword for the question.")
    question: str = Field(description="The actual question in Korean.")


class ListOfQuestions(BaseModel):
    questions: List[SpecificQuestion]


class Question(BaseModel):
    question_kor: str
    groupCodeId: str
    categoryId: str
    isAppropriate: bool = Field(default=False)
    isAIGenerated: bool = Field(default=False)


class Category(BaseModel):
    id: str = Field(default=None)
    name_kor: str = Field(default=None)
    name_eng: str = Field(default=None)


class GroupCode(BaseModel):
    id: str = Field(default=None)
    code: str = Field(default=None)
    name: str = Field(default=None)
    kor_name: str = Field(default=None)
    eng_name: str = Field(default=None)
    department: str = Field(default=None)


prompt = f"""
I want to create a disease specific patient survey question for history and physical examination.

The disease data I have has the following schema.

```json
{str(GroupCode.model_json_schema())}
```

Here is an example of the data.


```json
[
    {{
        "id": "2735303c-fbe5-4f30-8761-39b4b752b34b",
        "code": "A19",
        "name": "A19",
        "kor_name": "좁쌀결핵",
        "eng_name": "Miliary tuberculosis",
        "department": "UNASSIGNED"
    }},
    {{
        "id": "9e7aa9cf-78a0-40e8-981d-ebe8427d5218",
        "code": "A18",
        "name": "A18",
        "kor_name": "기타 기관의 결핵",
        "eng_name": "Tuberculosis of other organs",
        "department": "UNASSIGNED"
    }},
    {{
        "id": "ba30d79b-0d7c-4395-ab84-b082ede9862a",
        "code": "A18.4",
        "name": "A18.4",
        "kor_name": "피부 및 피하조직의 결핵",
        "eng_name": "Tuberculosis of skin and subcutaneous tissue",
        "department": "UNASSIGNED"
    }}
]
```

You will be receiving a data from the `groupCode`. You need to create a list of questions that should be asked to the patient based on the diagnosis. The questions should be in Korean. Here is an example of the input and the output. The `category` can be the following values: "Chief complaints", "Past medical history", "Family history", "Allergy", "Past surgical history", "Lifestyle", "Medication", and "Review of system".

```input
{{
    "id": "e72f8df4-7134-4f2c-921c-51b37edfd247",
    "code": "C19-C20",
    "name": "C19-C20",
    "kor_name": "직장구불결장접합부의 악성 신생물, 직장의 악성 신생물",
    "eng_name": "Malignant neoplasm of rectosigmoid junction, Malignant neoplasm of rectum",
    "department": "UNASSIGNED"
}}
```

```output
[
    {{
        "category": "Past medical history",
        "keyword": "colonoscopy",
        "question": "대장내시경 검사를 해보셨나요?"
    }},
    {{
        "category": "Past medical history",
        "keyword": "colonoscopy",
        "question": "대장내시경 검사를 해보셨나요?"
    }},
    {{
        "category": "Review of system",
        "keyword": "Stool caliber change",
        "question": "대변 굵기 변화"
    }},
    {{
        "category": "Review of system",
        "keyword": "Anal pain",
        "question": "항문 통증"
    }},
    {{
        "category": "Review of system",
        "keyword": "Pruritis ani",
        "question": "항문 가려움"
    }},
    {{
        "category": "Review of system",
        "keyword": "Tenesmus",
        "question": "후중감(항문이나 직장에 무언가 남아있는 것 같은 불편한 느낌)"
    }},
    {{
        "category": "Review of system",
        "keyword": "Discharge(soiling)",
        "question": "대변이 묻어나오는 증상"
    }},
    {{
        "category": "Review of system",
        "keyword": "Prolapsed anal mass",
        "question": "항문 종괴 돌출"
    }},
    {{
        "category": "Review of system",
        "keyword": "Urinary incontinence",
        "question": "요실금"
    }},
    {{
        "category": "Review of system",
        "keyword": "Fecal incontinence",
        "question": "변실금"
    }}
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


def get_categories() -> List[Category]:
    import requests

    url = "https://vexam.rnd.zarathu.com/api/rest/v1/question/category"

    payload = {}
    headers = {"x-api-key": "zCVwmOBR1pMY/Iva+xZndQr2PQ+RLSm+V8t221nGjMw="}

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.text)
    output = []
    for d in data["data"]:
        output.append(Category(**d))
    return output


def get_group_codes() -> List[GroupCode]:
    import requests

    url = "https://vexam.rnd.zarathu.com/api/rest/v1/groupCode"

    payload = {}
    headers = {"x-api-key": "zCVwmOBR1pMY/Iva+xZndQr2PQ+RLSm+V8t221nGjMw="}

    response = requests.request("GET", url, headers=headers, data=payload)

    data = json.loads(response.text)
    output = []
    for d in data["data"]:
        output.append(GroupCode(**d))
    return output


if __name__ == "__main__":
    print(get_group_codes())
    print(get_categories())
