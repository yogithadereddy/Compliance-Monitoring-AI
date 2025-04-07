import os
import pandas as pd
from tqdm import tqdm
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

# ✅ Your Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyDV2bZEOXxchdyPUpYqs_kbhheiX4erzqw"

# ✅ Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.7)

# ✅ Define Agentic Prompt Template
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

# ✅ Build Chain
prompt = PromptTemplate.from_template(agentic_template)
chain = prompt | llm

# ✅ Load Data
df = pd.read_csv("preprocessed_regulations_pandas.csv")
df = df[df["full_content"].notna()].copy()

# ✅ Generate Summaries
summaries = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Gemini Agentic Summarization"):
    output = chain.invoke({
        "title": row["title"],
        "date": row["date"],
        "source": row["source"],
        "link": row["link"],
        "content": row["full_content"]
    })
    summaries.append(output)

# ✅ Save Output
df["agentic_summary"] = summaries
df.to_csv("regulatory_agentic_summaries_gemini.csv", index=False)
print("✅ Gemini-based summaries saved to regulatory_agentic_summaries_gemini.csv")
