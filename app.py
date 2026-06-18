import re

import streamlit as st
import ai
import db


def _parse_line(line: str) -> dict | None:
    line = re.sub(r'^[\d\.\-\*\·\•]+\s*', '', line).strip()
    if not line:
        return None
    ko_pos = next((i for i, c in enumerate(line) if '가' <= c <= '힣'), -1)
    if ko_pos == -1:
        return {"word": line, "hint_ko": ""}
    if ko_pos == 0:
        en_pos = next((i for i, c in enumerate(line) if c.isascii() and c.isalpha()), -1)
        if en_pos == -1:
            return {"word": line, "hint_ko": ""}
        return {"word": line[en_pos:].strip(), "hint_ko": line[:en_pos].strip()}
    return {"word": line[:ko_pos].strip(), "hint_ko": line[ko_pos:].strip()}


def parse_bulk_text(text: str) -> list[dict]:
    return [e for line in text.splitlines() if (e := _parse_line(line)) and e["word"]]

st.set_page_config(page_title="나만의 단어장", page_icon="📖", layout="centered")

st.markdown("""
<style>
#MainMenu, header, footer { visibility: hidden; }
.block-container {
    padding-top: 0.75rem !important;
    padding-bottom: 2rem !important;
    max-width: 520px;
    margin: 0 auto;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--secondary-background-color);
    border-radius: 14px;
    padding: 4px;
    gap: 2px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 11px 20px !important;
    color: var(--text-color) !important;
    opacity: 0.55;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    background: var(--background-color) !important;
    color: #6366f1 !important;
    opacity: 1;
    box-shadow: 0 1px 6px rgba(0,0,0,0.15);
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none; }

/* ── Text Input ── */
.stTextInput [data-baseweb="input"] {
    height: 68px !important;
    border-radius: 14px !important;
    border: 2px solid rgba(128,128,128,0.2) !important;
    background: var(--secondary-background-color) !important;
    transition: all 0.2s;
}
.stTextInput [data-baseweb="input"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12) !important;
}
.stTextInput [data-baseweb="input"] input {
    font-size: 16px !important;
    padding: 0 18px !important;
    background: transparent !important;
    color: var(--text-color) !important;
}

/* ── Text Area ── */
.stTextArea textarea {
    font-size: 16px !important;
    border-radius: 14px !important;
    border: 2px solid rgba(128,128,128,0.2) !important;
    background: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
}
.stTextArea textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,0.12) !important;
}

/* ── Buttons ── */
.stButton > button {
    height: 68px !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    border-radius: 14px !important;
    width: 100%;
    transition: all 0.15s ease;
}
/* 검색탭: 버튼을 입력창 높이에 맞게 하단 정렬 */
[data-testid="column"] .stButton {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    height: 100%;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(99,102,241,0.45) !important;
}
.stButton > button[kind="secondary"] {
    border: 2px solid rgba(128,128,128,0.25) !important;
    background: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
}
.stButton > button[kind="secondary"]:hover {
    border-color: #6366f1 !important;
    color: #6366f1 !important;
}

/* ── Selectbox ── */
.stSelectbox [data-baseweb="select"] > div {
    border-radius: 14px !important;
    min-height: 54px !important;
    border: 2px solid rgba(128,128,128,0.2) !important;
    font-size: 15px !important;
    background: var(--secondary-background-color) !important;
}

/* ── Expander (단어 카드) ── */
details[data-testid="stExpander"] > summary {
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 14px 18px !important;
    border-radius: 14px !important;
    background: var(--secondary-background-color) !important;
    border: 1.5px solid rgba(128,128,128,0.15) !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}
/* 메모 미리보기 – summary p 내 italic(em) 요소를 오른쪽 끝으로 */
details[data-testid="stExpander"] > summary p {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    width: 100% !important;
    margin: 0 !important;
    gap: 8px !important;
}
details[data-testid="stExpander"] summary em,
details[data-testid="stExpander"] summary p em,
details[data-testid="stExpander"] summary div em,
details[data-testid="stExpander"] summary span em {
    font-style: normal !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #6366f1 !important;
    background: rgba(99,102,241,0.18) !important;
    border-radius: 6px !important;
    padding: 2px 8px !important;
    white-space: nowrap !important;
    max-width: 40% !important;
    display: inline-block !important;
}
details[data-testid="stExpander"][open] > summary {
    border-radius: 14px 14px 0 0 !important;
    border-bottom: none !important;
}
details[data-testid="stExpander"] > div:last-child {
    border: 1.5px solid rgba(128,128,128,0.15) !important;
    border-top: none !important;
    border-radius: 0 0 14px 14px !important;
    background: var(--background-color) !important;
    padding: 14px 18px !important;
}

/* ── Alert / Info ── */
[data-testid="stAlert"] {
    border-radius: 12px !important;
    font-size: 15px !important;
}

/* ── Divider ── */
hr { border-color: rgba(128,128,128,0.15) !important; margin: 1rem 0 !important; }
</style>
""", unsafe_allow_html=True)

tab_search, tab_vocab, tab_bulk = st.tabs(["🔍 검색", "📚 내 단어장", "📋 일괄 입력"])


# ── 검색 탭 ──────────────────────────────────────────────────────────────────
with tab_search:
    col_q, col_btn = st.columns([5, 1])
    with col_q:
        query = st.text_input(
            "검색",
            placeholder="한국어도 OK  ·  e.g.  너 지분있다  /  resilient  /  break a leg",
            label_visibility="collapsed",
            key="search_input",
        )
    with col_btn:
        search_clicked = st.button("검색", type="primary", use_container_width=True)

    if search_clicked and query:
        with st.spinner("AI가 찾는 중..."):
            try:
                result = ai.lookup_word(query)
                st.session_state["last_result"] = result
            except Exception as e:
                st.error(f"검색 실패: {e}")

    if "last_result" in st.session_state:
        r = st.session_state["last_result"]

        st.divider()

        st.markdown(f"## {r['word']}")

        st.markdown(f"{r.get('meaning_ko', '')}")

        if r.get("alternatives"):
            st.markdown("**다른 표현** &nbsp; " + " · ".join(r["alternatives"]))

        if r.get("synonyms"):
            st.markdown("**관련 영어 표현** &nbsp; " + " · ".join(r["synonyms"]))

        if r.get("context"):
            st.info(r["context"])

        if r.get("examples"):
            st.markdown("**예문**")
            for ex in r["examples"]:
                st.markdown(f"- {ex['en']}")
                st.caption(f"  {ex['ko']}")

        st.divider()

        auto_tags = r.get("tags") or []
        if auto_tags:
            st.caption("자동 태그  " + "  ".join(f"`{t}`" for t in auto_tags))

        memo = st.text_area(
            "메모 (선택)",
            placeholder="나만의 메모를 남겨보세요",
            key="memo_input",
        )

        if st.button("💾 저장", type="primary", use_container_width=True):
            try:
                db.save_word(r, memo, auto_tags)
                st.success(f"**{r['word']}** 저장 완료!")
                st.session_state.pop("last_result")
                st.session_state.pop("memo_input", None)
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")


# ── 단어장 탭 ────────────────────────────────────────────────────────────────
with tab_vocab:
    col_search, col_tag = st.columns([2, 1])
    with col_search:
        search_text = st.text_input(
            "단어 검색",
            placeholder="영어 또는 한국어로 검색",
            label_visibility="collapsed",
            key="vocab_search",
        )
    with col_tag:
        all_tags = db.fetch_all_tags()
        tag_options = ["전체 태그"] + all_tags
        selected_tag = st.selectbox("태그 필터", tag_options, label_visibility="collapsed", key="tag_filter")

    filter_tag = "" if selected_tag == "전체 태그" else selected_tag

    try:
        words = db.fetch_words(search=search_text, tag=filter_tag)
    except Exception as e:
        st.error(f"불러오기 실패: {e}")
        words = []

    if not words:
        st.caption("저장된 단어가 없습니다.")
    else:
        st.caption(f"총 {len(words)}개")

        for w in words:
            memo = w.get('memo', '') or ''
            memo_preview = ('  *' + memo[:22] + ('…' if len(memo) > 22 else '') + '*') if memo else ''
            with st.expander(f"**{w['word']}**{memo_preview}"):
                st.markdown(f"{w.get('meaning_ko', '')}")

                if w.get("alternatives"):
                    st.markdown("**다른 표현** &nbsp; " + " · ".join(w["alternatives"]))

                if w.get("synonyms"):
                    st.markdown("**유사 표현** &nbsp; " + " · ".join(w["synonyms"]))

                if w.get("context"):
                    st.info(w["context"])

                if w.get("examples"):
                    st.markdown("**예문**")
                    for ex in w["examples"]:
                        st.markdown(f"- {ex['en']}")
                        st.caption(f"  {ex['ko']}")

                if w.get("tags"):
                    st.caption("태그  " + "  ".join(f"`{t}`" for t in w["tags"]))

                if w.get("memo"):
                    st.markdown(f"**메모** &nbsp; {w['memo']}")

                st.caption(f"저장일: {str(w.get('created_at', ''))[:10]}")

                col_edit, col_del = st.columns([1, 1])
                with col_edit:
                    if st.button("✏️ 메모 수정", key=f"edit_{w['id']}"):
                        st.session_state[f"editing_{w['id']}"] = True
                with col_del:
                    if st.button("🗑️ 삭제", key=f"del_{w['id']}"):
                        db.delete_word(w["id"])
                        st.rerun()

                if st.session_state.get(f"editing_{w['id']}"):
                    new_memo = st.text_area(
                        "메모 수정",
                        value=w.get("memo", ""),
                        key=f"new_memo_{w['id']}",
                    )
                    new_tag_str = st.text_input(
                        "태그 수정 (쉼표로 구분)",
                        value=", ".join(w.get("tags") or []),
                        key=f"new_tags_{w['id']}",
                    )
                    if st.button("저장", key=f"save_edit_{w['id']}"):
                        updated_tags = [t.strip() for t in new_tag_str.split(",") if t.strip()]
                        db.update_memo_tags(w["id"], new_memo, updated_tags)
                        st.session_state.pop(f"editing_{w['id']}", None)
                        st.rerun()


# ── 일괄 입력 탭 ──────────────────────────────────────────────────────────────
with tab_bulk:
    st.caption("한 줄에 하나씩. 영어+한국어 또는 한국어+영어 순 모두 OK.")

    bulk_text = st.text_area(
        "일괄 입력",
        placeholder="Apple cider vinegar  사과식초\n일부러 그런거야  It was intentional\nIt bothers me.  그건 날 귀찮게 해.",
        height=220,
        label_visibility="collapsed",
        key="bulk_text",
    )

    if st.button("미리보기", use_container_width=True) and bulk_text:
        parsed = parse_bulk_text(bulk_text)
        if parsed:
            st.session_state["bulk_parsed"] = parsed
        else:
            st.warning("파싱된 항목이 없습니다. 형식을 확인해주세요.")

    if "bulk_parsed" in st.session_state:
        parsed = st.session_state["bulk_parsed"]
        st.caption(f"{len(parsed)}개 감지됨")
        st.dataframe(
            [{"영어 표현": e["word"], "한국어 힌트": e["hint_ko"]} for e in parsed],
            use_container_width=True,
            hide_index=True,
        )

        col_save, col_cancel = st.columns([3, 1])
        with col_cancel:
            if st.button("취소", use_container_width=True):
                st.session_state.pop("bulk_parsed", None)
                st.rerun()
        with col_save:
            if st.button("💾 AI 분석 & 저장", type="primary", use_container_width=True):
                with st.spinner(f"{len(parsed)}개 분석 중..."):
                    try:
                        results = ai.lookup_bulk(parsed)
                        for r in results:
                            db.save_word(r, "", r.get("tags", []))
                        st.success(f"{len(results)}개 저장 완료!")
                        st.session_state.pop("bulk_parsed", None)
                        st.rerun()
                    except Exception as e:
                        st.error(f"오류: {e}")
