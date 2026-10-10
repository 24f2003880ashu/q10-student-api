
import csv
import re
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Q10: Load student data
CSV_FILE = Path(__file__).parent / "q-fastapi.csv"

with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    students = [
        {
            "studentId": int(row["studentId"]),
            "class": row["class"],
        }
        for row in csv.DictReader(file)
    ]


# Q10: Student API
@app.get("/api")
def get_students(
    class_: list[str] | None = Query(default=None, alias="class")
):
    if class_:
        wanted_classes = set(class_)
        result = [
            student for student in students
            if student["class"] in wanted_classes
        ]
    else:
        result = students

    return {"students": result}


# Q11: Batch sentiment API
class SentimentRequest(BaseModel):
    sentences: list[str] = Field(...)


POSITIVE = set("""
good great excellent amazing awesome fantastic wonderful best brilliant
love loved lovely like liked enjoy enjoyed happy glad delighted pleased
beautiful perfect nice positive outstanding superb success successful
win winner recommend helpful useful impressive incredible exciting fun
favorite satisfied satisfiedness better improve improved improvement
thank thanks grateful appreciate adorable cool sweet smile smiling
hope hopeful lucky fortunate proud confidence confident easy easygoing
peaceful comfortable convenient valuable worth fast reliable fresh
tasty delicious awesome friendly kind generous honest trust trusted
incredible inspiring inspiringly joyful cheerful thrilled excited
marvelous magnificent fabulous splendid positive benefit beneficial
effective efficient affordable attractive clean clear bright calm
strong powerful impressive pleasant enjoyable fascinating interesting
yay hooray excellent superb fantastic yes
""".split())

NEGATIVE = set("""
bad terrible horrible awful worst hate hated dislike disliked sad
angry upset disappointed disappointing poor annoying annoying
boring frustrating frustratingly frustrating disappointed regret
fail failed failure lose lost broken useless uselessness difficult
hard problem issue error wrong mistake painful pain hurt hurts
unhappy unhappy miserable depressed anxious worried scary afraid
fearful nervous stressful stress tired exhausted sick ill ugly
dirty disgusting nasty rude cruel unfair dangerous risky damage
damaged annoying annoying expensive overpriced slow unreliable
inconvenient uncomfortable unpleasant negative reject rejected
decline declined impossible impossiblely weak stupid foolish
annoyed annoyed frustrating frustratingly tragedy tragic disaster
disasterous unfortunate unlucky sadly unfortunately sadly
never no not nothing neither nor barely hardly rarely without
complaint complain complaints hate hates sucks sucks disappointing
waste wasted worthless boring boringly worst awful dreadful
pathetic failure failed fail bad worse worst regret regretful
mad furious irritated irritating horrible terrible disgusting
unacceptable dissatisfied dissatisfiedness broken corrupt fraud
scam cheated cheating loss lose losing missed missing late
delay delayed difficult confusing confused confusion issue
problem trouble difficult annoying frustrating fear worry worried
""".split())

NEGATIONS = {
    "not", "no", "never", "neither", "nor", "hardly", "barely",
    "isn't", "wasn't", "weren't", "don't", "doesn't", "didn't",
    "can't", "cannot", "couldn't", "won't", "wouldn't", "shouldn't"
}

INTENSIFIERS = {
    "very": 1.5, "really": 1.5, "extremely": 2.0,
    "absolutely": 2.0, "so": 1.4, "too": 1.3,
    "incredibly": 1.8, "super": 1.5, "quite": 1.2
}


def analyze_sentiment(sentence: str) -> str:
    text = sentence.lower().replace("’", "'")
    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text)

    positive_score = 0.0
    negative_score = 0.0
    negate_next = 0
    multiplier = 1.0

    for i, word in enumerate(words):
        if word in NEGATIONS:
            negate_next = 3
            continue

        if word in INTENSIFIERS:
            multiplier = INTENSIFIERS[word]
            continue

        score = 0.0
        if word in POSITIVE:
            score = 1.0
        elif word in NEGATIVE:
            score = -1.0

        if score:
            if negate_next > 0:
                score *= -1
            score *= multiplier

            if score > 0:
                positive_score += score
            else:
                negative_score += abs(score)

            multiplier = 1.0

        if negate_next > 0:
            negate_next -= 1

    # Handle common expressions
    if any(p in text for p in (
        "looking forward", "can't wait", "well done",
        "highly recommend", "good job", "thank you"
    )):
        positive_score += 2

    if any(p in text for p in (
        "fed up", "waste of time", "not worth",
        "very disappointed", "not happy", "never again"
    )):
        negative_score += 2

    if positive_score > negative_score:
        return "happy"
    if negative_score > positive_score:
        return "sad"
    return "neutral"


@app.post("/sentiment")
async def batch_sentiment(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": analyze_sentiment(sentence),
            }
            for sentence in request.sentences
        ]
    }


@app.get("/")
def home():
    return {"message": "Student and sentiment APIs are running"}
