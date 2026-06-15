import json
import streamlit as st
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


SYSTEM_PROMPT = """You are an English dictionary assistant.
When given an English word or expression, respond ONLY with a JSON object in this exact format:
{
  "word": "the word or expression as given",
  "part_of_speech": "품사 (e.g. 명사, 동사, 형용사, 숙어 등)",
  "meaning_ko": "한국어 뜻 (핵심 의미 1~2줄)",
  "examples": [
    {"en": "example sentence 1", "ko": "한국어 번역 1"},
    {"en": "example sentence 2", "ko": "한국어 번역 2"}
  ],
  "synonyms": ["synonym1", "synonym2", "synonym3"],
  "context": "이 표현이 주로 쓰이는 상황이나 뉘앙스 설명 (1~2문장)",
  "tags": ["태그1", "태그2", "태그3"]
}

Rules for "tags":
- Generate 3 to 5 Korean tags that best categorize this word.
- Combine the word itself and its meaning/context to pick relevant tags.
- Choose from categories like: 비즈니스, 일상, 감정, 관계, 학문, 여행, 음식, 시간, 성격, 자연, 의학, 법률, 기술, 스포츠, 문화, 숙어, 구동사, 형용사, 동사, 명사 — or create a fitting Korean tag if none apply.
- Tags must be short (1~4 characters), specific, and useful for filtering.
Do not include any text outside the JSON."""


def lookup_word(word: str) -> dict:
    client = get_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": word.strip()},
        ],
        response_format={"type": "json_object"},
        temperature=0.3,
    )
    return json.loads(response.choices[0].message.content)
