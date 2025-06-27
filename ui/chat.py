import streamlit as st

def display_chat_history():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

def chat_interface():
    if not st.session_state.vectorstore:
        st.info("📥 Upload or link your source files first.")
        return

    if prompt := st.chat_input("Ask me about the code or content..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.spinner("🤖 Thinking..."):
            response = st.session_state.agent.run(
                prompt, content_type=st.session_state.content_type
            )

        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
