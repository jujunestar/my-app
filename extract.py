import argparse
import os
from typing import Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class YouthInfo(BaseModel):
    age: str = Field(default="", description="문장에 나온 만 나이(숫자). 없으면 빈 문자열")
    city: str = Field(default="", description="문장에 나온 거주지. 없으면 빈 문자열")
    military_months: Optional[int] = Field(
        default=None,
        description="병역 기간(개월). '24개월'→24. 없으면 None",
    )
    deposit_manwon: Optional[int] = Field(
        default=None,
        description="보증금(만원 단위 환산). '3천'→3000, '500만원'→500, '2억'→20000. 없으면 None",
    )
    monthly_income_manwon: Optional[int] = Field(
        default=None,
        description="월 소득(만원 단위 환산). '170만원'→170, '250'→250. 없으면 None",
    )
    is_student: Optional[bool] = Field(
        default=None,
        description="재학 여부. 재학·휴학·대학생이면 true, 졸업·비재학이면 false, 언급 없으면 None",
    )


def build_llm():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("오류: .env에 OPENROUTER_API_KEY=... 를 먼저 넣어주세요.")
    return ChatOpenAI(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        max_retries=0,
    )


def extract_values(sentence: str) -> YouthInfo:
    llm = build_llm()
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "너는 한국어 문장에서 정보를 뽑는 추출기다. "
                "나이, 거주지, 병역개월, 보증금, 월소득, 재학여부만 추출한다. "
                "보증금과 월소득은 만원 단위 정수로 환산한다. 예: '3천'→3000, '1000만원'→1000, '2억'→20000. "
                "문장에 없는 항목은 반드시 비워 둔다(문자열은 빈 문자열, 숫자·불리언은 None). "
                "값은 문장에 적힌 내용에서만 추출하고 추측하지 않는다.",
            ),
            ("human", "{sentence}"),
        ]
    )
    chain = prompt | llm.with_structured_output(YouthInfo)
    return chain.invoke({"sentence": sentence})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="문장에서 청년정책 판정 항목을 추출합니다.")
    parser.add_argument("sentence", help="분석할 문장")
    args = parser.parse_args()

    info = extract_values(args.sentence)
    print(info.model_dump_json(indent=2))
