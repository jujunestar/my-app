import argparse
import json

POLICY_NAME = "청년월세지원 (국토부)"
CHECKED_DATE = "2026-08-13"
AGE_MIN = 19
AGE_MAX = 34
DEPOSIT_MAX_WON = 50000000


def _manwon(won: int) -> str:
    return f"{won // 10000:,}만원"


def judge(
    age: int,
    military_months: int,
    city: str,
    deposit_won: int,
    monthly_income_won: int | None = None,
) -> dict:
    del military_months

    reasons = []

    if AGE_MIN <= age <= AGE_MAX:
        reasons.append(
            f"[충족] 나이: 만 {age}세는 만 {AGE_MIN}~{AGE_MAX}세 범위 내 "
            f"(근거 항목: '만 19~34세', 확인일: {CHECKED_DATE})"
        )
    else:
        reasons.append(
            f"[미충족] 나이: 만 {age}세는 만 {AGE_MIN}~{AGE_MAX}세 범위 밖 "
            f"(근거 항목: '만 19~34세', 확인일: {CHECKED_DATE})"
        )

    if deposit_won <= DEPOSIT_MAX_WON:
        reasons.append(
            f"[충족] 보증금: {_manwon(deposit_won)} (한도 {_manwon(DEPOSIT_MAX_WON)} 이하) "
            f"(근거 항목: '무주택 + 보증금 5천만원 이하 + 월세 70만원 이하', 확인일: {CHECKED_DATE})"
        )
    else:
        reasons.append(
            f"[미충족] 보증금 기준 초과: {_manwon(deposit_won)} > {_manwon(DEPOSIT_MAX_WON)} 이하 "
            f"(근거 항목: '무주택 + 보증금 5천만원 이하 + 월세 70만원 이하', 확인일: {CHECKED_DATE})"
        )

    if monthly_income_won is not None:
        reasons.append(
            f"[확인 필요] 소득: 월 {_manwon(monthly_income_won)} — 기준중위소득 60% 이하는 "
            f"중위소득 표가 없어 코드로 확정 불가 "
            f"(근거 항목: '청년가구: 기준중위소득 60% 이하', 확인일: {CHECKED_DATE})"
        )
    else:
        reasons.append(
            f"[확인 필요] 소득: 입력 없음 — 소득 확인 전까지 확정 불가 "
            f"(근거 항목: '소득·재산 기준', 확인일: {CHECKED_DATE})"
        )

    failed = any(r.startswith("[미충족]") for r in reasons)
    if failed:
        verdict = "불가"
        verdict_reason = "요건 미충족 항목 있음 (위 [미충족] 사유 참조)"
    else:
        verdict = "조건부가능"
        verdict_reason = "소득·재산 기준 및 무주택·월세 요건의 확인이 남아 있음"

    notices = [
        "내 지자체 사업은 따로 확인해주세요.",
        "병역 개월 차감은 '청년미래적금' 규정이며 청년월세지원 원문에는 없어 이 판정에 적용하지 않았습니다.",
        f"무주택 여부, 월세 70만원 이하, 자산 기준도 확인 대상입니다 (확인일: {CHECKED_DATE}).",
    ]
    if city == "서울":
        notices.append("서울시 자체 사업(만 19~39세)은 지자체 분이므로 별도 확인 대상입니다.")

    return {
        "policy": POLICY_NAME,
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "reasons": reasons,
        "notices": notices,
        "checked_date": CHECKED_DATE,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="청년월세지원(국토부) 자격을 코드로 판정합니다.")
    parser.add_argument("age", type=int, help="만 나이")
    parser.add_argument("military_months", type=int, help="병역 기간(개월)")
    parser.add_argument("city", help="거주지")
    parser.add_argument("deposit", type=int, help="보증금(원)")
    parser.add_argument("monthly_income", type=int, nargs="?", default=None, help="월소득(원)")
    args = parser.parse_args()

    result = judge(args.age, args.military_months, args.city, args.deposit, args.monthly_income)
    print(json.dumps(result, ensure_ascii=False, indent=2))
