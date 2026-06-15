import streamlit as st
import ai
import db

st.set_page_config(page_title="나만의 단어장", page_icon="📖", layout="centered")

st.title("📖 나만의 영어 단어장")

tab_search, tab_vocab = st.tabs(["🔍 검색", "📚 내 단어장"])


# ── 검색 탭 ──────────────────────────────────────────────────────────────────
with tab_search:
    st.subheader("단어 / 표현 검색")

    query = st.text_input(
        "영어 단어나 표현을 입력하세요",
        placeholder="e.g.  resilient  /  break a leg  /  pull strings",
        key="search_input",
    )

    if st.button("검색", type="primary", use_container_width=True) and query:
        with st.spinner("AI가 검색 중..."):
            try:
                result = ai.lookup_word(query)
                st.session_state["last_result"] = result
            except Exception as e:
                st.error(f"검색 실패: {e}")

    if "last_result" in st.session_state:
        r = st.session_state["last_result"]

        st.divider()
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## {r['word']}")
        with col2:
            st.caption(r.get("part_of_speech", ""))

        st.markdown(f"**뜻** &nbsp; {r.get('meaning_ko', '')}")

        if r.get("synonyms"):
            st.markdown("**유사 표현** &nbsp; " + " · ".join(r["synonyms"]))

        if r.get("context"):
            st.info(r["context"])

        if r.get("examples"):
            st.markdown("**예문**")
            for ex in r["examples"]:
                st.markdown(f"- {ex['en']}")
                st.caption(f"  {ex['ko']}")

        st.divider()
        st.markdown("#### 단어장에 저장")

        memo = st.text_area("메모 (선택)", placeholder="나만의 메모를 남겨보세요", key="memo_input")

        all_tags = db.fetch_all_tags()
        tag_input = st.text_input(
            "태그 (쉼표로 구분)",
            placeholder="e.g.  비즈니스, 일상, IELTS",
            key="tag_input",
        )
        new_tags = [t.strip() for t in tag_input.split(",") if t.strip()]

        if all_tags:
            st.caption("기존 태그: " + "  ".join(f"`{t}`" for t in all_tags))

        if st.button("💾 저장", type="primary", use_container_width=True):
            try:
                db.save_word(r, memo, new_tags)
                st.success(f"**{r['word']}** 저장 완료!")
                st.session_state.pop("last_result")
                st.session_state.pop("memo_input", None)
                st.session_state.pop("tag_input", None)
                st.rerun()
            except Exception as e:
                st.error(f"저장 실패: {e}")


# ── 단어장 탭 ────────────────────────────────────────────────────────────────
with tab_vocab:
    st.subheader("내 단어장")

    col_search, col_tag = st.columns([2, 1])
    with col_search:
        search_text = st.text_input("단어 검색", placeholder="검색할 단어 입력", key="vocab_search")
    with col_tag:
        all_tags = db.fetch_all_tags()
        tag_options = ["전체"] + all_tags
        selected_tag = st.selectbox("태그 필터", tag_options, key="tag_filter")

    filter_tag = "" if selected_tag == "전체" else selected_tag

    try:
        words = db.fetch_words(search=search_text, tag=filter_tag)
    except Exception as e:
        st.error(f"불러오기 실패: {e}")
        words = []

    if not words:
        st.info("저장된 단어가 없습니다. 검색 탭에서 단어를 추가해보세요!")
    else:
        st.caption(f"총 {len(words)}개")

        for w in words:
            with st.expander(f"**{w['word']}** &nbsp; {w.get('part_of_speech', '')}"):
                st.markdown(f"**뜻** &nbsp; {w.get('meaning_ko', '')}")

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
                    st.markdown("**태그** &nbsp; " + "  ".join(f"`{t}`" for t in w["tags"]))

                if w.get("memo"):
                    st.markdown(f"**메모** &nbsp; {w['memo']}")

                st.caption(f"저장일: {str(w.get('created_at', ''))[:10]}")

                col_edit, col_del = st.columns([1, 1])

                with col_edit:
                    if st.button("✏️ 메모/태그 수정", key=f"edit_{w['id']}"):
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
