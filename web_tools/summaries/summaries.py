from typing import List, TypedDict, Union

import openai
from openai import AsyncOpenAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from langgraph.graph import END, START, StateGraph

from web_tools.summaries.prompts import (
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_USER_PROMPT_TEMPLATE,
    SYSTEM_PROMPT_SUMMARY,
    USER_PROMPT_SUMMARY,
    SYSTEM_PROMPT_CRITIC,
    USER_PROMPT_CRITIC,
    SYSTEM_PROMPT_REVISE,
    USER_PROMPT_REVISE,
    SYSTEM_PROMPT_GROUNDING,
    USER_PROMPT_GROUNDING,
)
from web_tools.summaries.models import SummaryData


content_web = """
How 20 Minutes empowers journalists and boosts audience engagement with generative AI on Amazon Bedrock by Aurélien Capdecomme, Bertrand d'Aure, and Pascal Vogel | on 21 MAY 2024 | in Amazon Bedrock, Customer Solutions, Generative AI, Media & Entertainment | Permalink | Comments | Share This post is co-written with Aurélien Capdecomme and Bertrand d’Aure from 20 Minutes. With 19 million monthly readers, 20 Minutes is a major player in the French media landscape. The media organization delivers useful, relevant, and accessible information to an audience that consists primarily of young and active urban readers. Every month, nearly 8.3 million 25–49-year-olds choose 20 Minutes to stay informed. Established in 2002, 20 Minutes consistently reaches more than a third (39 percent) of the French population each month through print, web, and mobile platforms. As 20 Minutes’s technology team, we’re responsible for developing and operating the organization’s web and mobile offerings and driving innovative technology initiatives. For several years, we have been actively using machine learning and artificial intelligence (AI) to improve our digital publishing workflow and to deliver a relevant and personalized experience to our readers. With the advent of generative AI, and in particular large language models (LLMs), we have now adopted an AI by design strategy, evaluating the application of AI for every new technology product we develop. One of our key goals is to provide our journalists with a best-in-class digital publishing experience. Our newsroom journalists work on news stories using Storm, our custom in-house digital editing experience. Storm serves as the front end for Nova, our serverless content management system (CMS). These applications are a focus point for our generative AI efforts. In 2023, we identified several challenges where we see the potential for generative AI to have a positive impact. These include new tools for newsroom journalists, ways to increase audience engagement, and a new way to ensure advertisers can confidently assess the brand safety of our content. To implement these use cases, we rely on Amazon Bedrock. Amazon Bedrock is a fully managed service that offers a choice of high-performing foundation models (FMs) from leading AI companies like AI21 Labs, Anthropic, Cohere, Meta, Stability AI, and Amazon Web Services (AWS) through a single API, along with a broad set of capabilities you need to build generative AI applications with security, privacy, and responsible AI. This blog post outlines various use cases where we’re using generative AI to address digital publishing challenges. We dive into the technical aspects of our implementation and explain our decision to choose Amazon Bedrock as our foundation model provider. Identifying challenges and use cases Today’s fast-paced news environment presents both challenges and opportunities for digital publishers. At 20 Minutes, a key goal of our technology team is to develop new tools for our journalists that automate repetitive tasks, improve the quality of reporting, and allow us to reach a wider audience. Based on this goal, we have identified three challenges and corresponding use cases where generative AI can have a positive impact. The first use case is to use automation to minimize the repetitive manual tasks that journalists perform as part of the digital publishing process. The core work of developing a news story revolves around researching, writing, and editing the article. However, when the article is complete, supporting information and metadata must be defined, such as an article summary, categories, tags, and related articles. While these tasks can feel like a chore, they are critical to search engine optimization (SEO) and therefore the audience reach of the article. If we can automate some of these repetitive tasks, this use case has the potential to free up time for our newsroom to focus on core journalistic work while increasing the reach of our content. The second use case is how we republish news agency dispatches at 20 Minutes. Like most news outlets, 20 Minutes subscribes to news agencies, such as the Agence France-Presse (AFP) and others, that publish a feed of news dispatches covering national and international news. 20 Minutes journalists select stories relevant to our audience and rewrite, edit, and expand on them to fit the editorial standards and unique tone our readership is used to. Rewriting these dispatches is also necessary for SEO, as search engines rank duplicate content low. Because this process follows a repeatable pattern, we decided to build an AI-based tool to simplify the republishing process and reduce the time spent on it. The third and final use case we identified is to improve transparency around the brand safety of our published content. As a digital publisher, 20 Minutes is committed to providing a brand-safe environment for potential advertisers. Content can be classified as brand-safe or not brand-safe based on its appropriateness for advertising and monetization. Depending on the advertiser and brand, different types of content might be considered appropriate. For example, some advertisers might not want their brand to appear next to news content about sensitive topics such as military conflicts, while others might not want to appear next to content about drugs and alcohol. Organizations such as the Interactive Advertising Bureau (IAB) and the Global Alliance for Responsible Media (GARM) have developed comprehensive guidelines and frameworks for classifying the brand safety of content. Based on these guidelines, data providers such as the IAB and others conduct automated brand safety assessments of digital publishers by regularly crawling websites such as 20minutes.fr and calculating a brand safety score. However, this brand safety score is site-wide and doesn’t break down the brand safety of individual news articles. Given the reasoning capabilities of LLMs, we decided to develop an automated per-article brand safety assessment based on industry-standard guidelines to provide advertisers with a real-time, granular view of the brand safety of 20 Minutes content. Our technical solution At 20 Minutes, we’ve been using AWS since 2017, and we aim to build on top of serverless services whenever possible. The digital publishing frontend application Storm is a single-page application built using React and Material Design and deployed using Amazon Simple Storage Service (Amazon S3) and Amazon CloudFront. Our CMS backend Nova is implemented using Amazon API Gateway and several AWS Lambda functions. Amazon DynamoDB serves as the primary database for 20 Minutes articles. New articles and changes to existing articles are captured using DynamoDB Streams, which invokes processing logic in AWS Step Functions and feeds our search service based on Amazon OpenSearch. We integrate Amazon Bedrock using AWS PrivateLink, which allows us to create a private connection between our Amazon Virtual Private Cloud (VPC) and Amazon Bedrock without traversing the public internet. 20 Minutes architecture diagramWhen working on articles in Storm, journalists have access to several AI tools implemented using Amazon Bedrock. Storm is a block-based editor that allows journalists to combine multiple blocks of content, such as title, lede, text, image, social media quotes, and more, into a complete article. With Amazon Bedrock, journalists can use AI to generate an article summary suggestion block and place it directly into the article. We use a single-shot prompt with the full article text in context to generate the summary. Storm CMS also gives journalists suggestions for article metadata. This includes recommendations for appropriate categories, tags, and even in-text links. These references to other 20 Minutes content are critical to increasing audience engagement, as search engines rank content with relevant internal and external links higher. To implement this, we use a combination of Amazon Comprehend and Amazon Bedrock to extract the most relevant terms from an article’s text and then perform a search against our internal taxonomic database in OpenSearch. Based on the results, Storm provides several suggestions of terms that should be linked to other articles or topics, which users can accept or reject. 20 Minutes summary generation feature News dispatches become available in Storm as soon as we receive them from our partners such as AFP. Journalists can browse the dispatches and select them for republication on 20minutes.fr. Every dispatch is manually reworked by our journalists before publication. To do so, journalists first invoke a rewrite of the article by an LLM using Amazon Bedrock. For this, we use a low-temperature single-shot prompt that instructs the LLM not to reinterpret the article during the rewrite, and to keep the word count and structure as similar as possible. The rewritten article is then manually edited by a journalist in Storm like any other article. To implement our new brand safety feature, we process every new article published on 20minutes.fr. Currently, we use a single shot prompt that includes both the article text and the IAB brand safety guidelines in context to get a sentiment assessment from the LLM. We then parse the response, store the sentiment, and make it publicly available for each article to be accessed by ad servers. Lessons learned and outlook When we started working on generative AI use cases at 20 Minutes, we were surprised at how quickly we were able to iterate on features and get them into production. Thanks to the unified Amazon Bedrock API, it’s easy to switch between models for experimentation and find the best model for each use case. For the use cases described above, we use Anthropic’s Claude in Amazon Bedrock as our primary LLM because of its overall high quality and, in particular, its quality in recognizing French prompts and generating French completions. Because 20 Minutes content is almost exclusively French, these multilingual capabilities are key for us. We have found that careful prompt engineering is a key success factor and we closely adhere to Anthropic’s prompt engineering resources to maximize completion quality. Even without relying on approaches like fine-tuning or retrieval-augmented generation (RAG) to date, we can implement use cases that deliver real value to our journalists. Based on data collected from our newsroom journalists, our AI tools save them an average of eight minutes per article. With around 160 pieces of content published every day, this is already a significant amount of time that can now be spent reporting the news to our readers, rather than performing repetitive manual tasks. The success of these use cases depends not only on technical efforts, but also on close collaboration between our product, engineering, newsroom, marketing, and legal teams. Together, representatives from these roles make up our AI Committee, which establishes clear policies and frameworks to ensure the transparent and responsible use of AI at 20 Minutes. For example, every use of AI is discussed and approved by this committee, and all AI-generated content must undergo human validation before being published. We believe that generative AI is still in its infancy when it comes to digital publishing, and we look forward to bringing more innovative use cases to our platform this year. We’re currently working on deploying fine-tuned LLMs using Amazon Bedrock to accurately match the tone and voice of our publication and further improve our brand safety analysis capabilities. We also plan to use Bedrock models to tag our existing image library and provide automated suggestions for article images. Why Amazon Bedrock? Based on our evaluation of several generative AI model providers and our experience implementing the use cases described above, we selected Amazon Bedrock as our primary provider for all our foundation model needs. The key reasons that influenced this decision were: Choice of models: The market for generative AI is evolving rapidly, and the AWS approach of working with multiple leading model providers ensures that we have access to a large and growing set of foundational models through a single API. Inference performance: Amazon Bedrock delivers low-latency, high-throughput inference. With on-demand and provisioned throughput, the service can consistently meet all of our capacity needs. Private model access: We use AWS PrivateLink to establish a private connection to Amazon Bedrock endpoints without traversing the public internet, ensuring that we maintain full control over the data we send for inference. Integration with AWS services: Amazon Bedrock is tightly integrated with AWS services such as AWS Identity and Access Management (IAM) and the AWS Software Development Kit (AWS SDK). As a result, we were able to quickly integrate Bedrock into our existing architecture without having to adapt any new tools or conventions. Conclusion and outlook In this blog post, we described how 20 Minutes is using generative AI on Amazon Bedrock to empower our journalists in the newsroom, reach a broader audience, and make brand safety transparent to our advertisers. With these use cases, we’re using generative AI to bring more value to our journalists today, and we’ve built a foundation for promising new AI use cases in the future. To learn more about Amazon Bedrock, start with Amazon Bedrock Resources for documentation, blog posts, and more customer success stories.
"""

content = """
Greetings Cohere Community,

With each upgrade, AI models become more advanced. Take our latest Command R models, for example; they offer significant improvements in coding, math, and latency. With every new update, it makes you wonder: how good are large language models (LLMs) at reasoning?

For businesses, LLM reasoning is essential because it allows AI to tackle more than just basic tasks. With advanced reasoning, models can manage complex processes that involve decision-making like automating workflows, analyzing data trends, and supporting strategic decisions. This makes them especially useful tools in fields like finance, healthcare, and legal, where getting things right really matters.

What is LLM reasoning?

LLM reasoning is a skill that models are increasingly being trained to perform. It refers to the ability of AI models to logically process information, break down complex problems, and make decisions based on context and patterns. This is a step-change from traditional LLM retrieval and response.

Cohere Co-Founder and CEO Aidan Gomez describes reasoning as, “crucial to intelligence … It's not a discrete 'does it have this capability or not'; it's a continuum of how robust the reasoning engine inside these models is.”

Modern LLMs are becoming more adept and can now perform mathematical reasoning, predictive logic, and autonomous multi-agent reasoning. One of the most exciting advancements is the ability to simulate a kind of inner monologue, where models can walk through their decision-making processes. This is a key step toward robust reasoning, although training data for this is rare and can be difficult to create. Overall, different types of reasoning are essential to LLM intelligence, and ongoing research is continually expanding our understanding of their potential.

Why is LLM reasoning important?

LLMs with strong reasoning skills are incredibly valuable for businesses. Right now, everyone’s talking about how to make them work for their specific needs. We’re stepping into an era where AI can take on specialized, complex tasks in more personalized and domain-specific ways.

Reasoning also helps build trust with users. Just like how citations add transparency to retrieval-augmented generation (RAG) systems, as models get better at explaining their thought process through complex problems, people can rely on them for more accurate and context-aware results.

What is Cohere’s approach?

Cohere's approach to LLM development is deeply rooted in real-world practicality, with a strong focus on creating models that solve immediate business challenges.  Recent improvements in model design and training methods are changing the way LLMs tackle reasoning tasks.

One breakthrough is to train the model to break down complex problems and elicit reasoning, for example through chain-of-thought (CoT). There is growing evidence that this works on human-created data, but also on synthetically-created data, which enables LLMs to learn how to reason through a broader array of problems. This way, LLMs solve a problem in a step-by-step fashion.

What’s next?

Over the next year, we’re excited to see LLM reasoning make big strides, helping to create specialized AI models that businesses can really put to use. At the same time, we’ll be tackling important challenges like data security, fairness, and reliability, so that industries like finance, healthcare, and legal can fully benefit from these advancements.

For more insights on Enterprise AI, check out our latest articles or read on for this month’s highlights and upcoming events.

Whats new-1
Product

Our enterprise-grade AI models are better than ever with improved versions of Command R and Command R+. Plus, you can now use our models on Slack with the newly launched Cohere AI app for Slack.

For Business

This month, we spoke with several customers on how they are transforming work with enterprise AI. Learn how Oracle and Johnson Lambert use Cohere models.

Developers

Setting safety guardrails just got a whole lot easier. With our Chat endpoint, you can now choose between different modes to meet your specific safety requirements. Have questions? Get answers in our next Developer Office Hours on Oct 21st, 1:00 p.m. EDT, on Discord!

Research

Building off the success of Aya, Cohere For AI launched Expedition Aya, a six-week, open-build challenge to connect researchers worldwide and support new multilingual research initiatives. Join us in celebrating the five projects that were honored with the top recognition.

Company

Watch Cohere’s Co-Founder and CEO Aidan Gomez and Oracle’s Miranda Nash discuss how our partnership is helping enterprises leverage the power of AI at Oracle CloudWorld 2024. And check out how we continue to grow solutions for global customers in our collaboration with consulting firm Nomura Research Institute (NRI).

Read more
Whats next
Upcoming events with Cohere

Oct 2 [Online] We've launched a new course on building production-ready RAG with Cohere models in collaboration with Weights & Biases and Weaviate. Join us at 9:30 a.m. EDT, on Discord and meet the experts behind the course.
Oct 15 [Online] Join Cohere For AI and Professor Zhijing Jin from the University of Toronto for a discussion on LLM reasoning and cooperation.
Oct 15 [Online] Join Cohere For AI to explore a day in the life of an ML engineer in computer vision, presented by Cisco’s Nahid Alam.
Oct 18 [Online] Shout out to all developers! Join us on X Spaces at 1:00 p.m. EDT. Cohere’s Sandra Kublik will be interviewing research and product teams behind the latest releases from Cohere.
For all upcoming events, explore cohere.com/events.
"""


# If you are satisfied with the summary ONLY answer "SATISFIED" otherwise suggest improvements in the format specified above.


model = "gpt-4o-mini"


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        error : Binary flag for control flow to indicate whether test error was tripped
        messages : With user question, error messages, reasoning
        generation : Code solution
        iterations : Number of tries
    """

    messages: List
    summary: str
    content: str
    critic: str
    grounded_summary: str
    revise_iterations: int
    summary_preview: Union[SummaryData, None]


def write_summary(state: GraphState) -> str:
    print("write_summary: XXX")
    content = state["content"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_SUMMARY),
            ("user", USER_PROMPT_SUMMARY),
        ],
    )

    chain = prompt | ChatOpenAI(model=model) | StrOutputParser()

    result = chain.invoke({"content": content})
    # print(result)
    state["summary"] = result
    return state


def ground_summary(state: GraphState) -> str:
    # print('ground_summary: XXX')
    content = state["content"]
    summary = state["summary"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_GROUNDING),
            ("user", USER_PROMPT_GROUNDING),
        ],
    )

    chain = prompt | ChatOpenAI(model=model) | StrOutputParser()

    result = chain.invoke({"content": content, "summary": summary})
    # print(result)
    state["grounded_summary"] = result
    return state


def critic_summary(state: GraphState) -> str:
    # print('critic_summary: XXX')
    content = state["content"]
    summary = state["summary"]
    critic = state["critic"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_CRITIC),
            ("user", USER_PROMPT_CRITIC),
        ],
    )

    chain = prompt | ChatOpenAI(model=model) | StrOutputParser()

    result = chain.invoke({"content": content, "summary": summary, "critic": critic})
    # print(result)
    state["critic"] = result
    return state


def revise_summary(state: GraphState) -> str:
    # print('revise_summary: XXX')
    content = state["content"]
    summary = state["summary"]
    critic = state["critic"]
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT_REVISE),
            ("user", USER_PROMPT_REVISE),
        ],
    )

    chain = prompt | ChatOpenAI(model=model) | StrOutputParser()

    result = chain.invoke({"content": content, "summary": summary, "critic": critic})
    state["revise_iterations"] += 1
    state["summary"] = result
    return state


def should_continue(state: GraphState) -> str:
    print("should_continue: XXX")
    if state["revise_iterations"] == 1:
        return "grounding"
    if "SATISFIED" in state["critic"]:
        print("satisfied: XXX")
        return "grounding"
    else:
        return "reviser"


# client = openai.OpenAI()
# system_message = system_prompt
# user_message = user_prompt.format(content=content)

# messages = [
#     {"role": "system", "content": system_message},
#     {"role": "user", "content": user_message},
# ]

# completion = client.chat.completions.create(
#     model="gpt-4o",
#     messages=messages
# )

# print(completion.choices[0].message.content)


# llm = ChatOpenAI( model="gpt-4o")

# new_prompt = (
#     SystemMessage(content=system_message) + HumanMessage(content=user_message)
# )

# print(new_prompt.format_messages(content=content))

# chain = new_prompt | llm
# result = chain.invoke()
# print(result)


async def generate_summary_data(state: GraphState) -> Union[SummaryData, None]:
    try:
        summary = state["grounded_summary"]
        client: AsyncOpenAI = openai.AsyncOpenAI()
        system_message = DEFAULT_SYSTEM_PROMPT
        user_message = DEFAULT_USER_PROMPT_TEMPLATE.format(content=summary)

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]

        completion = await client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages,
            tools=[
                openai.pydantic_function_tool(SummaryData),
            ],
        )
        result = completion.choices[0].message.tool_calls[0].function.parsed_arguments
        print(result)
        state["summary_preview"] = result
        return state
    except Exception as e:
        print(e)
        state["summary_preview"] = None
        return state


# Define a new graph
workflow = StateGraph(GraphState)

# Define the two nodes we will cycle between
workflow.add_node("writer_", write_summary)
workflow.add_node("critic_", critic_summary)
workflow.add_node("reviser", revise_summary)
workflow.add_node("grounding", ground_summary)
workflow.add_node("summary_data", generate_summary_data)


# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.add_edge(START, "writer_")
workflow.add_edge("writer_", "critic_")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "critic_",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
    {
        "grounding": "grounding",
        "reviser": "reviser",
    },
)
workflow.add_edge("reviser", "critic_")
workflow.add_edge("grounding", "summary_data")
workflow.add_edge("summary_data", END)

# workflow.add_edge("rivers", "critic")


summary_agent = workflow.compile()


# solution = app.invoke({"content": content, "summary": "" , "critic": "", "grounded_summary": ""})
# print(solution)

# for chunk in summary_agent.stream({"content": content_web, "summary": "" , "critic": "", "grounded_summary": ""}, stream_mode="updates"):
#     for node, values in chunk.items():
#         print('-----------------')
#         print(f"Receiving update from node: '{node}'")
#         print(values)
#         print("\n\n")


# with open('output.json', 'w') as f:
#     f.write(solution["grounded_summary"])
#     f.close()
