import streamlit as st
import ai
import db

st.set_page_config(page_title="나만의 단어장", page_icon="📖", layout="centered")

tab_search, tab_vocab = st.tabs(["🔍 검색", "📚 내 단어장"])


# ── 검색 탭 ──────────────────────────────────────────────────────────────────
with tab_search:
    query = st.text_input(
        "검색",
        placeholder="한국어도 OK  ·  e.g.  너 지분있다  /  resilient  /  break a leg",
        label_visibility="collapsed",
        key="search_input",
    )

    if st.button("검색", type="primary", use_container_width=True) and query:
        with st.spinner("AI가 찾는 중..."):
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

        st.markdown(f"{r.get('meaning_ko', '')}")

        if r.get("alternatives"):
            st.markdown("**다른 표현** &nbsp; " + " · ".join(r["alternatives"]))

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
            with st.expander(f"**{w['word']}**  {w.get('part_of_speech', '')}"):
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
