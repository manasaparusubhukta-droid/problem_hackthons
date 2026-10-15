# 🛍️ Grounded Shopping Assistant

A product-discovery chatbot over a **fixed catalogue** that answers natural shopper questions and **refuses when the catalogue doesn't support the answer**. No invented products, prices or return policies.

> A hallucinated price is a legal and trust problem, not a cosmetic one. So the language model is never the source of a fact.

## How it stays honest

```
question ─► parse ─► route ─► retrieve / filter ─► build answer from catalogue values (+ claims)
                                                        │
                                          verify every claim against the catalogue
                                                        │
                              pass ─► answer (optionally rephrased by an LLM, then re-verified)
                              fail ─► refuse
```

| Layer | What it does |
|---|---|
| `app/intent.py` | Deterministic query understanding: category, brand, price range, RAM, noise-cancelling, policy topics, and **unsupported topics** (competitor prices, discounts, delivery to a pincode, compatibility, reviews, health advice). |
| `app/retrieval.py` | BM25 retrieval plus hard filters (price, stock, category). |
| `app/assistant.py` | Builds answers from catalogue values only. Prices are inserted from data, never typed by a model. Every statement carries a `Claim(sku, field, value)`. |
| `app/verify.py` | Re-checks every claim, every ₹ amount and every product name against the catalogue. Any mismatch discards the draft. |
| `app/refusal.py` | Designed refusals that say what *can* be answered. |
| `app/llm.py` | **Optional.** Claude can rephrase an already-verified answer; the result is re-verified and falls back to the template if any number or name changes. |

Policy answers quote `data/policies.md` verbatim.

## Quick start

```bash
git clone <your-repo-url> && cd grounded-shopping-assistant
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py                          # web UI at http://localhost:8501
# or terminal chat:
python -m app.cli
```

Works fully offline with no API key. To let Claude rephrase verified answers:

```bash
export USE_LLM=1 ANTHROPIC_API_KEY=sk-ant-...
```

## Try these

| Question | Behaviour |
|---|---|
| Show me laptops under ₹60,000 | Filters the catalogue and lists matches with real prices |
| Compare Nimbus Air 14 and Nimbus Pro 16 | Side-by-side from catalogue fields |
| What is your return policy? | Quotes the policy text verbatim |
| laptops under 20000 | Says none exist; shows closest options, clearly labelled |
| Does Aurelia Quiet 700 have GPS? | **Refuses**: GPS isn't listed; shows what is |
| Is the Sony WH-1000XM5 available? | **Refuses**: not in the catalogue |
| Is it cheaper on Amazon? | **Refuses**: out of scope |

## Evaluation

```bash
python -m unittest discover -s tests -t .     # unit tests (or: pytest)
python -m eval.run_eval                        # metrics on eval/questions.json
```

Reports kind accuracy, correct-refusal rate, false-refusal rate, content accuracy and a **hallucination count that must be 0**. The question set covers answerable, unanswerable, adversarial and policy questions. Add your own to `eval/questions.json`.

## Use your own catalogue

Replace `data/catalogue.json` (same fields: `sku, name, category, brand, price, stock, rating, description, specs{}`) and `data/policies.md` (one `## section` per policy). To support new categories or spec names, extend `CATEGORY_SYNONYMS` / `ATTRIBUTES` in `app/intent.py` and `SPEC_META` in `app/catalogue.py`.

## Deploy (free public URL)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io), click **New app**, pick the repo, and set the main file to `streamlit_app.py`.
3. (Optional) add `USE_LLM` and `ANTHROPIC_API_KEY` under **Secrets**.

## Limitations and next steps

- Query understanding is rule-based, so it is auditable but won't catch every phrasing. Next step: an LLM intent parser whose output is validated against the same schema.
- The sample catalogue is fictional (20 products, INR).
- Swap BM25 for embeddings plus a reranker when the catalogue grows.
