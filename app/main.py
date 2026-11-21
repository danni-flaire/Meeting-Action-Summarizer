import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from schema import MeetingInput, ActionItem, MeetingOutput
from groq import Groq
import json


app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://meeting-action-summarizer.vercel.app" # Replace with your actual Vercel URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/extract", response_model=MeetingOutput)
async def extract_memo(payload: MeetingInput):
    raw_text = payload.transcript
    completion = client.chat.completions.create(
    model="qwen/qwen3.8-27b",
    messages=[
            {
                "role": "system", 
                "content": (
                    "You are an expert executive assistant and technical project manager. "
                    "Analyze raw meeting transcripts and output a JSON object with three keys: "
                    "'meeting_summary' (string), 'key_decisions' (array of strings), "
                    "and 'action_items' (array of objects containing 'task', 'owner', and 'deadline')."
                )
            },
            {
                "role": "user", 
                "content": f"Here is the meeting transcript:\n\n{raw_text}"
            }],
    temperature=0.6,
    max_completion_tokens=2048,
    top_p=0.8,
    reasoning_effort="high",
    stop=None,
    response_format={"type": "json_object"}
)
    ai_response_string = completion.choices[0].message.content
    parsed_data = json.loads(ai_response_string)
    return parsed_data