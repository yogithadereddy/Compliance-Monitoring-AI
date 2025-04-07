from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import PromptTemplate
import pandas as pd
from tqdm import tqdm
import time

# ✅ Init Ollama LLM
llm = ChatOllama(model="mistral", temperature=0.7)

# ✅ Agentic-style prompt template
agentic_template = """
You are a regulatory compliance assistant.

Summarize the regulation in a structured agentic format:

🔍 Regulation Summary:
Summarize the core content of the regulation in 2–3 concise paragraphs.

🌍 Impact Scope:
Identify sectors, industries, and regions likely affected.

🏢 Applicable Clients:
Based on the source: {source}, which types of companies should be alerted?

⚠️ Risk/Compliance Implications:
Describe risks and compliance needs based on this law.

✅ Suggested Compliance Actions:
Propose 2–3 realistic compliance actions companies should take.

📅 Regulation Date: {date}
📝 Source: {link}

Regulatory Title: {title}

Full Regulation Text:
{content}
"""

prompt = PromptTemplate(
    input_variables=["title", "date", "source", "link", "content"],
    template=agentic_template
)

# ✅ Chain setup
chain = prompt | llm

# ✅ Load and limit your dataset to first 20 valid rows
df = pd.read_csv("preprocessed_regulations_pandas.csv")
df = df[df["full_content"].notna()].head(20).copy()  # 👈 Only 20 rows

summaries = []

# ✅ Run summarization
for _, row in tqdm(df.iterrows(), total=len(df), desc="Ollama Agentic Summarization"):
    try:
        result = chain.invoke({
            "title": row["title"],
            "date": row["date"],
            "source": row["source"],
            "link": row["link"],
            "content": row["full_content"]
        })
        summaries.append(result.content)
        time.sleep(1)  # Optional: Helps manage CPU load
    except Exception as e:
        print(f"❌ Error processing row: {e}")
        summaries.append("")

# ✅ Save results
df["agentic_summary"] = summaries
df.to_csv("regulatory_agentic_summaries_ollama_20rows.csv", index=False)
print("✅ 20 Ollama-based summaries saved to regulatory_agentic_summaries_ollama_20rows.csv")
