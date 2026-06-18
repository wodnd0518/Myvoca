import json
import streamlit as st
from openai import OpenAI


def get_client() -> OpenAI:
    return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


SYSTEM_PROMPT = """Respond ONLY with this JSON. No text outside it.
{
  "word": "main English word/expression",
  "alternatives": ["other English way 1", "other English way 2"],
  "part_of_speech": "품사",
  "meaning_ko": "한국어 뜻 (1~2줄)",
  "examples": [
    {"en": "...", "ko": "..."},
    {"en": "...", "ko": "..."},
    {"en": "...", "ko": "..."},
    {"en": "...", "ko": "..."},
    {"en": "...", "ko": "..."}
  ],
  "synonyms": ["related English expression 1", "related English expression 2", "related English expression 3"],
  "context": "사용 상황·뉘앙스 (1~2문장, 한국어)",
  "tags": ["태그1", "태그2", "태그3"]
}
Rules:
- Korean input → "word": best English equivalent, "alternatives": 2~3 other English expressions, "meaning_ko": "원래표현 → 영어 의미"
- English input → "word": given expression, "alternatives": []
- "synonyms": English only, 2~3 related expressions
- "tags": 3~5 Korean tags, 1~4 chars, from: 비즈니스,일상,감정,관계,학문,여행,성격,자연,의학,법률,기술,스포츠,문화,숙어,구동사,형용사,동사,명사"""


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
