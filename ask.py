import argparse
import json
import re

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

from extract import build_llm, extract_values
from rules import judge


@tool
def judge_youth_rent(
    age: int,
    military_months: int,
    city: str,
    deposit_won: int,
    monthly_income_won: int | None = None,
) -> dict:
    """청년월세지원(국토부) 자격 판정. 만 나이, 병역개월, 거주지, 보증금(원), 월소득(원)으로 판정 결과를 돌려준다."""
    return judge(age, military_months, city, deposit_won, monthly_income_won)


SYSTEM_PROMPT = (
    "너는 청년 주거 지원 안내자다. "
    "판정, 금액, 조건은 반드시 judge_youth_rent 도구의 결과에 적힌 것만 사용한다. "
    "도구 결과에 없는 수치나 조건을 절대 말하지 않는다. "
    "최종 답은 사람이 읽을 한국어 문장으로 정리하고, "
    "판정(가능/불가/조건부가능)과 사유, 근거 정책 항목명과 확인일을 반드시 포함한다."
)


def _digits(value) -> int | None:
    m = re.search(r"\d+", str(value))
    return int(m.group()) if m else None


def prepare_inputs(info) -> dict | None:
    age = _digits(info.age)
    city = (info.city or "").strip()
    military_months = info.military_months if info.military_months is not None else 0
    deposit_won = info.deposit_manwon * 10000 if info.deposit_manwon is not None else None
    income_won = info.monthly_income_manwon * 10000 if info.monthly_income_manwon is not None else None

    missing = []
    if age is None:
        missing.append("나이")
    if not city:
        missing.append("거주지")
    if deposit_won is None:
        missing.append("보증금")
    if missing:
        print(f"판정에 필요한 정보가 없습니다: {', '.join(missing)}")
        print("나이, 거주지, 보증금, 월소득을 알려주시면 판정해 드립니다.")
        return None
    return {
        "age": age,
        "military_months": military_months,
        "city": city,
        "deposit_won": deposit_won,
        "monthly_income_won": income_won,
    }


def run_agent(sentence: str, inputs: dict, info_json: str) -> str:
    llm = build_llm()
    llm_with_tools = llm.bind_tools([judge_youth_rent])
    human = (
        f"{sentence}\n\n"
        f"사용자 문장에서 추출한 값(JSON):\n{info_json}\n\n"
        "위 값을 인자로 judge_youth_rent 도구를 호출해 판정을 받으세요."
    )
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human)]

    for _ in range(3):
        ai = llm_with_tools.invoke(messages)
        messages.append(ai)
        calls = getattr(ai, "tool_calls", None)
        if not calls:
            return str(ai.content)
        for call in calls:
            result = judge_youth_rent.invoke(call)
            if isinstance(result, ToolMessage):
                messages.append(result)
            else:
                payload = json.dumps(result, ensure_ascii=False) if isinstance(result, dict) else str(result)
                messages.append(ToolMessage(content=payload, tool_call_id=call["id"]))
    raise RuntimeError("도구 호출 후 최종 답을 얻지 못했습니다.")


def phrase_directly(inputs: dict) -> str:
    result = judge(**inputs)
    llm = build_llm()
    human = (
        "다음 판정 결과(JSON)만 근거로 사람이 읽을 한국어 답을 작성하세요. "
        "결과에 없는 금액이나 조건을 추가하지 마세요.\n\n"
        + json.dumps(result, ensure_ascii=False, indent=2)
    )
    answer = llm.invoke([SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=human)])
    return str(answer.content)


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="문장으로 청년월세지원 자격을 묻고 답합니다.")
    parser.add_argument("sentence", help="사용자 문장")
    args = parser.parse_args()

    info = extract_values(args.sentence)
    info_json = info.model_dump_json(indent=2)
    print("[추출값]", info_json)

    inputs = prepare_inputs(info)
    if inputs is None:
        raise SystemExit(1)

    try:
        answer = run_agent(args.sentence, inputs, info_json)
    except Exception:
        answer = phrase_directly(inputs)

    print("\n[답변]")
    print(answer)


if __name__ == "__main__":
    main()
