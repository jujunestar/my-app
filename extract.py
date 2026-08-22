import argparse
import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field


class YouthInfo(BaseModel):
    age: str = Field(default="", description="문장에 나온 만 나이(숫자). 없으면 빈 문자열")
    city: str = Field(default="", description="문장에 나온 거주지. 없으면 빈 문자열")


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
                "나이와 거주지만 추출하고, 문장에 없는 항목은 반드시 빈 문자열로 채운다. "
                "값은 문장에 적힌 그대로 추출하고 추측하지 않는다.",
            ),
            ("human", "{sentence}"),
        ]
    )
    chain = prompt | llm.with_structured_output(YouthInfo)
    return chain.invoke({"sentence": sentence})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="문장에서 나이와 거주지를 추출합니다.")
    parser.add_argument("sentence", help="분석할 문장")
    args = parser.parse_args()

    info = extract_values(args.sentence)
    print(info.model_dump_json(indent=2))
