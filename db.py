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
        "examples": word_data.get("examples", []),
        "synonyms": word_data.get("synonyms", []),
        "context": word_data.get("context", ""),
        "memo": memo,
        "tags": tags,
    }).execute()


def fetch_words(search: str = "", tag: str = "") -> list[dict]:
    client = get_client()
    query = client.table("vocabulary").select("*").order("created_at", desc=True)

    if search:
        query = query.ilike("word", f"%{search}%")
    if tag:
        query = query.contains("tags", [tag])

    result = query.execute()
    return result.data


def fetch_all_tags() -> list[str]:
    client = get_client()
    result = client.table("vocabulary").select("tags").execute()
    tag_set = set()
    for row in result.data:
        if row.get("tags"):
            tag_set.update(row["tags"])
    return sorted(tag_set)


def delete_word(word_id: int) -> None:
    client = get_client()
    client.table("vocabulary").delete().eq("id", word_id).execute()


def update_memo_tags(word_id: int, memo: str, tags: list[str]) -> None:
    client = get_client()
    client.table("vocabulary").update({
        "memo": memo,
        "tags": tags,
    }).eq("id", word_id).execute()
