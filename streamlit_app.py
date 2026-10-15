"""Streamlit chat UI.  Run:  streamlit run streamlit_app.py"""
import streamlit as st

from app.assistant import ShoppingAssistant

st.set_page_config(page_title="Grounded Shopping Assistant", page_icon="🛍️")


@st.cache_resource
def get_bot() -> ShoppingAssistant:
    return ShoppingAssistant()


bot = get_bot()

st.title("🛍️ Grounded Shopping Assistant")
st.caption("Every price, spec and policy comes straight from the catalogue. "
           "If the catalogue doesn't say it, I won't either.")

EXAMPLES = [
    "Show me laptops under ₹60,000",
    "Compare Nimbus Air 14 and Nimbus Pro 16",
    "Which smartwatch has the longest battery life?",
    "What is your return policy?",
    "Does Aurelia Quiet 700 have GPS?",
    "Is the Sony WH-1000XM5 available?",
    "Is it cheaper on Amazon?",
]

with st.sidebar:
    st.header("Try these")
    clicked = None
    for ex in EXAMPLES:
        if st.button(ex, use_container_width=True):
            clicked = ex
    st.divider()
    st.write(f"Catalogue: **{len(bot.cat.products)} products**, {len(bot.cat.categories)} categories")
    with st.expander("Browse catalogue"):
        st.dataframe(
            [{"SKU": p["sku"], "Name": p["name"], "Category": p["category"],
              "Price (₹)": p["price"], "Stock": p["stock"], "Rating": p["rating"]} for p in bot.cat.products],
            hide_index=True,
        )
    if st.button("Clear chat"):
        st.session_state.pop("history", None)
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["text"])
        if msg.get("meta"):
            st.caption(msg["meta"])

prompt = st.chat_input("Ask about a product, price, stock or policy…") or clicked
if prompt:
    st.session_state.history.append({"role": "user", "text": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    ans = bot.ask(prompt)
    badge = {"refuse": "⛔ Declined: not supported by the catalogue",
             "no_match": "ℹ️ No matching product in the catalogue",
             "clarify": "❓ Need clarification", "answer": "✅ Grounded in catalogue"}[ans.kind]
    meta = badge + (f" · sources: {', '.join(ans.sources)}" if ans.sources else "")
    with st.chat_message("assistant"):
        st.markdown(ans.text.replace("₹", "\\₹"))
        st.caption(meta)
        if ans.claims:
            with st.expander("Verified claims"):
                st.dataframe([{"SKU": c.sku, "Field": c.field, "Value": str(c.value)} for c in ans.claims],
                             hide_index=True)
    st.session_state.history.append({"role": "assistant", "text": ans.text.replace("₹", "\\₹"), "meta": meta})
