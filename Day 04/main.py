
from fastapi import FastAPI

app = FastAPI(title="AapdaMitra API", version="1.0.0")


@app.get("/")
def home():
    return {"message": "Welcome to AapdaMitra"}


@app.get("/health")
def health():
    return {"status": "AapdaMitra is running"}


@app.get("/questions")
def get_questions():
    return {
        "message": "AapdaMitra sample user questions",
        "questions": [
            "What should I do during a flood?",
            "What precautions should I take during heavy rainfall?",
            "How can I stay safe during an earthquake?",
            "What should I keep in an emergency kit?",
            "What should I do if my house gets flooded?",
            "Is the bridge near my village currently open or closed?",
            "What should I do if I see a landslide?",
            "How can I help an injured person during a disaster?",
            "Where should I go during an emergency evacuation?",
            "What emergency items should I carry while evacuating?"
        ]
    }


@app.get("/questions/q6")
def question_six():
    return {
        "question": "Is the bridge near my village currently open or closed?",
        "answer": "I don't have verified live bridge-status information. Please contact local disaster management authorities before travelling."
    }
