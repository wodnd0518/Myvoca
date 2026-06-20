import streamlit as st
from supabase import create_client, Client


def get_client() -> Client:
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def save_word(word_data: dict, memo: str, tags: list[str]) -> None:
    client = get_client()
    client.table("vocabulary").insert({
        "word": word_data["word"],
        "part_of_speech": word_data.get("part_of_speech", ""),
        "meaning_ko": word_data.get("meaning_ko", ""),
        "alternatives": word_data.get("alternatives", []),
        "examples": word_data.get("examples", []),
        "synonyms": word_data.get("synonyms", []),
        "context": word_data.get("context", ""),
        "memo": memo,
        "tags": tags,
    }).execute()


def fetch_words(search: str = "") -> list[dict]:
    client = get_client()
    result = client.table("vocabulary").select("*").order("created_at", desc=True).execute()
    data = result.data
    if search:
        s = search.lower()
        data = [
            r for r in data
            if s in (r.get("word") or "").lower()
            or s in (r.get("meaning_ko") or "").lower()
            or any(s in t.lower() for t in (r.get("tags") or []))
        ]
    return data


def delete_word(word_id: int) -> None:
    client = get_client()
    client.table("vocabulary").delete().eq("id", word_id).execute()


def update_memo_tags(word_id: int, memo: str, tags: list[str]) -> None:
    client = get_client()
    client.table("vocabulary").update({
        "memo": memo,
        "tags": tags,
    }).eq("id", word_id).execute()


def save_qa(question: str, answer: str) -> None:
    client = get_client()
    client.table("qa_history").insert({
        "question": question,
        "answer": answer,
    }).execute()


def fetch_qa() -> list[dict]:
    client = get_client()
    result = client.table("qa_history").select("*").order("created_at", desc=True).execute()
    return result.data
