import os
import time

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI


def main():
    load_dotenv()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("오류: .env에 OPENROUTER_API_KEY=... 를 먼저 넣어주세요.")

    llm = ChatOpenAI(
        model="nvidia/nemotron-3-super-120b-a12b:free",
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
        max_retries=0,
    )

    messages = [HumanMessage(content="청년 월세 지원이 뭔지 두 문장으로 알려줘")]
    for attempt in range(5):
        try:
            answer = llm.invoke(messages)
            print(answer.content)
            return
        except Exception as e:
            if attempt == 4:
                raise SystemExit(f"오류: 5회 재시도 후 실패했습니다.\n{e}")
            wait = 15 * (attempt + 1)
            print(f"일시적 오류(429 등)로 {wait}초 후 재시도합니다... ({attempt + 1}/5)")
            time.sleep(wait)


if __name__ == "__main__":
    main()
