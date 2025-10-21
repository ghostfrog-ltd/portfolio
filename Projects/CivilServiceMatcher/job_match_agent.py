from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import asyncio

# Initialize the model and prompt chain
llm = ChatOpenAI(model="gpt-4")
star_prompt = ChatPromptTemplate.from_template("""
You're a Civil Service career coach. Based on the job description and candidate CV,
write a STAR example showing how the candidate meets one of the listed responsibilities.

Job:
{job_description}

CV:
{cv_text}

Respond in STAR format (Situation, Task, Action, Result).
""")

chain = star_prompt | llm

# Async pipeline
async def run_async_langgraph_pipeline(cv_text, jobs):
    jobs = jobs[:10]  # Limit for performance

    async def generate_star(job):
        print(f"[DEBUG] Generating STAR for: {job['title']}")
        response = await chain.ainvoke({
            "job_description": job['summary'],
            "cv_text": cv_text
        })
        return {
            "title": job['title'],
            "link": job['link'],
            "summary": job['summary'],
            "star": response.content
        }

    tasks = [generate_star(job) for job in jobs]
    return await asyncio.gather(*tasks)
