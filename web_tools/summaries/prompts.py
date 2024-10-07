DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant. You help users generate a summary structure by calling the Summary Data function."
DEFAULT_USER_PROMPT_TEMPLATE = "Generate a FAQ section with a title  and a description. The summary is {content}. Generate a Summary Data with a title  and a short description and a list of authors"



SYSTEM_PROMPT_SUMMARY = """
you are a professional summarization expert. Your task is to condense web articles for an executive with techbackground. I provide you with the content of a web article. 
"""

USER_PROMPT_SUMMARY = """
<web-article> 
{content}
 </web-article> 


You task is to produce a summary with the following structure: 
1. Title & Source and all mentioned Authors. 
2. Executive Summary 
3. Concise definitions can be added here if the key takeaway includes technical terms. 
4. Core Insights 
	- Use inline definitions for any complex terms. Example: "Technological Integration: Leveraging AI (artificial intelligence) for predictive analytics helps anticipate disruptions." 
5. Actionable Recommendations 
	- Define terms as needed, but keep explanations brief and relevant to the recommendation. 
6. Relevant Data/Facts (Optional) 
7. Glossary (Optional) - Use this section if multiple complex terms are used.

Be exact and concise in your summary. I will be reviewed by a professional in the field.

"""


SYSTEM_PROMPT_CRITIC = """
You are a professional copy writer and summarization reviewer with years of experience. Your task is to analyse a webarticle and it summary for correctness. I provide you the original webarticle and the summary produced by a summarization expert.
"""

USER_PROMPT_CRITIC = """
I provide you with a summary of a web article.
<webarticle> 
{content}
</webarticle> 

<summary> 
{summary}
</summary> 

<old_critic>
{critic}
</old_critic>
 
You are provided with a web article and its corresponding summary and an old critic. Your task is to analyze the summary based on the following criteria:

High-level concepts should be clearly presented.
Technical jargon should be included when necessary and appropriate to the context.
Your job is NOT to rewrite the summary but to suggest improvements where needed. Provide your suggestions using the format below.

If imrprovements are needed, provide suggestions.

### Title & Source
- **Current**: "How 20 Minutes Empowers Journalists and Boosts Audience Engagement with Generative AI on Amazon Bedrock" by Aurélien Capdecomme, Bertrand d'Aure, and Pascal Vogel | Published on 21 May 2024 | Amazon Bedrock Blog
- **Improvement**: This section is accurate and needs no revision.

### Executive Summary
- **Current**: 20 Minutes, a leading French media organization with 19 million monthly readers, has implemented Amazon Bedrock's generative AI as part of their "AI by design" strategy. In 2023, they focused on three main AI applications: automating repetitive tasks for journalists, streamlining the republishing of news agency dispatches, and ensuring detailed brand safety assessments for advertisers.
- **Improvement**: Include that 20 Minutes has been actively using machine learning and AI for several years and that they have adopted an AI by design strategy to evaluate AI applications for new technology products.

In case no improvements are needed, provide the following response:"SATISFIED" in uppercase letters.

"""



SYSTEM_PROMPT_REVISE = """
You are a professional copy writer and summarization expert with years of experience. Your task is to revise an existing summary.
"""

USER_PROMPT_REVISE = """
I provide you with a summary of a web article.
<webarticle> 
{content}
</webarticle> 

<summary> 
{summary}
</summary> 

Next I provide you with a correction suggestions.
<suggestions>
{critic}
</suggestions>
 
Rewrite the summary to address the critic.
Follow the structure of the summary: 
1. Title & Source 2. 
2. Executive Summary 
3. Concise definitions can be added here if the key takeaway includes technical terms. 
4. Core Insights 
	- Use inline definitions for any complex terms. Example: "Technological Integration: Leveraging AI (artificial intelligence) for predictive analytics helps anticipate disruptions." 
5. Actionable Recommendations 
	- Define terms as needed, but keep explanations brief and relevant to the recommendation. 
6. Relevant Data/Facts (Optional) 
7. Glossary (Optional) - Use this section if multiple complex terms are used.

Be exact and concise in your summary. I will be reviewed by a professional in the field.
Avoid citations
"""


SYSTEM_PROMPT_GROUNDING = """
You are a professional summarization reviewer and advanced copy writer. 
"""

USER_PROMPT_GROUNDING = """
<webarticle> 
{content}
</webarticle> 

<summary> 
{summary}
</summary> 
 
Your task is to insert citations into the provided summary. place citations inside the executive summary and the core insights place sources brackets for example [1], [2] etc. Each of the citation corresponds to an UNMODIFIED sentence within the original article. It is required that the citations are numbered without any 
the citations are listed in a new chapter citations at the end of the summary. The citations need to BE EXACTT paraphrases from the original content.
"""