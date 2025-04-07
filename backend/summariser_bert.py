import pandas as pd
from tqdm import tqdm
import time
from transformers import pipeline

# ✅ Load BART summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

# ✅ Helper: Truncate text to ~750 tokens (safety buffer)
def truncate_text(text, max_words=750):
    return " ".join(text.split()[:max_words])

# ✅ Helper: Smart safe summary function
def safe_summarize(text, max_length=150, min_length=50):
    try:
        input_length = len(text.split())
        max_len = min(max_length, int(input_length * 0.6))
        max_len = max(min_length + 10, max_len)  # avoid too-short max_len
        summary = summarizer(text, max_length=max_len, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"❌ Error during summarization: {e}")
        return ""

# ✅ Generate agentic summary
def generate_agentic_summary(title, date, source, link, full_text):
    try:
        # ✅ Step 1: Truncate raw regulation content
        safe_content = truncate_text(full_text)

        # ✅ Step 2: First summarization step (pure summary)
        summary = safe_summarize(safe_content)

        # ✅ Step 3: Build agentic template with summary
        agentic_prompt = f"""
🔍 Regulation Summary:
{summary}

🌍 Impact Scope:
[To be manually added or inferred based on industry keywords]

🏢 Applicable Clients:
Based on the source: {source}, which types of companies should be alerted?

⚠️ Risk/Compliance Implications:
[Analyze legal exposure and compliance risks based on summary]

✅ Suggested Compliance Actions:
[Propose 2–3 realistic compliance actions companies should take.]

📅 Regulation Date: {date}
📝 Source: {link}

Regulatory Title: {title}

Full Regulation Text:
[Omitted for brevity]
"""
        # ✅ Step 4: Optional: Re-summarize the final agentic format (skipped to prevent long inputs)
        # agentic_summary = safe_summarize(agentic_prompt, max_length=200, min_length=80)

        return agentic_prompt.strip()

    except Exception as e:
        print(f"❌ Error in generating agentic summary: {e}")
        return ""

# ✅ Load dataset
df = pd.read_csv("preprocessed_regulations_pandas.csv")
df = df[df["full_content"].notna()].copy()

summaries = []

# ✅ Run summarization loop
for _, row in tqdm(df.iterrows(), total=len(df), desc="Agentic BART Summarization"):
    summary = generate_agentic_summary(
        title=row["title"],
        date=row["date"],
        source=row["source"],
        link=row["link"],
        full_text=row["full_content"]
    )
    summaries.append(summary)
    time.sleep(0.5)  # Avoid rate limits

# ✅ Save results
df["agentic_summary"] = summaries
df.to_csv("regulatory_agentic_summaries_bert.csv", index=False)
print("✅ Agentic summaries saved to regulatory_agentic_summaries_bert.csv")
