import streamlit as st
import requests

GROK_API_URL = "https://api.x.ai/v1/chat/completions"

SYSTEM_PROMPT = """You are NutriBot, a friendly diet assistant specializing in South Indian diabetic nutrition. Help users with meal suggestions, glycemic index info, portion sizes, and healthy cooking tips for South Indian foods. Keep responses concise and practical. Always remind users to consult their doctor for medical decisions."""


def get_grok_response(messages: list, api_key: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "grok-4-latest",
        "messages": messages,
        "max_tokens": 512,
        "temperature": 0.7
    }
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError:
        code = response.status_code
        body = ""
        try:
            body = response.json().get("error", {}).get("message", "")
        except:
            pass
        return f"⚠️ API error {code}: {body}"
    except requests.exceptions.Timeout:
        return "⚠️ Request timed out. Please try again."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"


def render_floating_chatbot(api_key: str):
    if "show_chat" not in st.session_state:
        st.session_state.show_chat = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Toggle button top-right
    col1, col2, col3 = st.columns([5, 1, 1])
    with col3:
        label = "✕ Close" if st.session_state.show_chat else "🤖 NutriBot"
        if st.button(label, key="chat_toggle", use_container_width=True):
            st.session_state.show_chat = not st.session_state.show_chat
            st.rerun()

    if not st.session_state.show_chat:
        return

    st.markdown("---")

    # Message history
    if not st.session_state.chat_messages:
        st.markdown(
            "<p style='color:#6b7280;font-size:0.85rem;text-align:center;padding:0.5rem;'>"
            "👋 Hi! Ask me anything about South Indian diabetic nutrition."
            "</p>", unsafe_allow_html=True
        )
        st.markdown("**💡 Quick questions:**")
        qs = [
            "Is idli good for diabetics?",
            "Best low-GI South Indian breakfast?",
            "How much rice can a diabetic eat?",
            "Are millets better than white rice?"
        ]
        c1, c2 = st.columns(2)
        for i, q in enumerate(qs):
            col = c1 if i % 2 == 0 else c2
            with col:
                if st.button(q, key=f"qs_{i}", use_container_width=True):
                    st.session_state.chat_messages.append({"role": "user", "content": q})
                    with st.spinner("NutriBot is thinking..."):
                        msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.chat_messages
                        reply = get_grok_response(msgs, api_key)
                    st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                    st.rerun()
    else:
        for msg in st.session_state.chat_messages:
            if msg["role"] == "user":
                st.markdown(f"""
                <div style="background:#e8f5e9;border-radius:14px 14px 4px 14px;
                    padding:8px 14px;margin:6px 0 6px 60px;
                    font-size:0.88rem;border:1px solid #c8e6c9;color:#1a1a1a;">
                    <b style="color:#1a6b3c;">You:</b><br>{msg['content']}
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background:#f9f9f9;border-radius:14px 14px 14px 4px;
                    padding:8px 14px;margin:6px 60px 6px 0;
                    font-size:0.88rem;border:1px solid #e0e0e0;color:#1a1a1a;">
                    <b style="color:#1a6b3c;">🤖 NutriBot:</b><br>{msg['content']}
                </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    user_input = st.text_input(
        "message", label_visibility="collapsed",
        placeholder="Type your question here...",
        key="nutri_chat_input"
    )
    btn_col1, btn_col2 = st.columns([4, 1])
    with btn_col1:
        if st.button("Send ➤", key="nutri_send", use_container_width=True, type="primary"):
            if user_input.strip():
                st.session_state.chat_messages.append({"role": "user", "content": user_input.strip()})
                with st.spinner("Thinking..."):
                    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.chat_messages
                    reply = get_grok_response(msgs, api_key)
                st.session_state.chat_messages.append({"role": "assistant", "content": reply})
                st.rerun()
            else:
                st.warning("Please type something first.")
    with btn_col2:
        if st.button("🗑️ Clear", key="nutri_clear", use_container_width=True):
            st.session_state.chat_messages = []
            st.rerun()

    st.markdown("---")
