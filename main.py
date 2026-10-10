
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

# ---------------- Q10: Student API ----------------

CSV_FILE = Path(__file__).parent / "q-fastapi.csv"

with open(CSV_FILE, newline="", encoding="utf-8-sig") as file:
    students = [
        {
            "studentId": int(row["studentId"]),
            "class": row["class"],
        }
        for row in csv.DictReader(file)
    ]


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


# ---------------- Q11: Sentiment Analysis ----------------

class SentimentRequest(BaseModel):
    sentences: list[str] = Field(...)


POSITIVE_WORDS = set("""
good great excellent amazing awesome fantastic wonderful best brilliant
love loved lovely loving like liked enjoy enjoyed happy glad delighted
pleased beautiful perfect nice positive outstanding superb success
successful winner win recommend helpful useful impressive incredible
exciting fun favorite satisfied better improve improved improvement
thank thanks grateful appreciate adorable cool sweet smile smiling
hope hopeful lucky fortunate proud confident easy peaceful comfortable
convenient valuable worthwhile fast reliable fresh tasty delicious
friendly kind generous honest trust trusted inspiring joyful cheerful
thrilled excited marvelous magnificent fabulous splendid beneficial
effective efficient affordable attractive clean clear bright calm
strong powerful pleasant enjoyable fascinating interesting wonderful
positive agree amazing adorable gorgeous fantastic lovely excellent
terrific remarkable exceptional impressive masterpiece masterpiece
delightful charming amusing hilarious funny entertaining engaging
enjoyable rewarding achievement achievement brilliant creative smart
clever beautiful pretty wonderful reliable safe secure convenient
recommend recommended outstanding perfect flawless awesome fantastic
best ever happy joy joyfully loved adore adored adore likeable
satisfied success winning winner positive optimistic enthusiastic
motivated passionate proud grateful thankful fantastic phenomenal
superb top-notch good-quality easy simple smooth comfortable
impressed impressed impressed satisfied satisfied worthwhile
""".split())

NEGATIVE_WORDS = set("""
bad terrible horrible awful worst hate hated hates dislike disliked
sad angry upset disappointed disappointing poor annoying boring
frustrating frustrate frustration fail failed failure lose lost broken
useless difficult problem issue error wrong mistake painful pain hurt
hurts unhappy miserable depressed anxious worried scary afraid fearful
nervous stressful stress tired exhausted sick ill ugly dirty disgusting
nasty rude cruel unfair dangerous risky damage damaged expensive
overpriced slow unreliable inconvenient uncomfortable unpleasant negative
reject rejected decline declined impossible weak stupid foolish tragedy
tragic disaster disastrous unfortunate unlucky complaint complain complaints
sucks waste wasted worthless regret regretful mad furious irritated
irritating horrible terrible unacceptable dissatisfied corrupt fraud scam
cheated cheating loss losing missed missing late delay delayed trouble
confusing confused confusion frustrating frustratingly horrible dreadful
pathetic disappointing disappointing frustrating awful disgusting
annoyed annoying awful sucks suck disappointing disappointed sad sadness
angry anger hate hatred failure failed fail miserable depressed awful
poorly badly worse worst terrible horrible useless boring tedious
mediocre disappointing frustrating inconvenient disappointing
unfortunately unfortunately problem problems difficult painful
unhappy dissatisfied unsatisfied inferior inferiorly defective defect
broken damaged fail failed losing loser unlucky hopeless hopelessness
fear fearsome worried worry worrying stressful stressed exhausted
annoyed annoyed upsetting upsettingly irritating irritatingly
""".split())

NEGATIONS = {
    "not", "no", "never", "neither", "nor", "hardly", "barely",
    "isn't", "wasn't", "weren't", "don't", "doesn't", "didn't",
    "can't", "cannot", "couldn't", "won't", "wouldn't", "shouldn't",
    "aint", "ain't", "without"
}

INTENSIFIERS = {
    "very": 1.5,
    "really": 1.5,
    "extremely": 2.0,
    "absolutely": 2.0,
    "so": 1.3,
    "too": 1.2,
    "incredibly": 1.8,
    "super": 1.5,
    "quite": 1.2,
    "totally": 1.5,
    "highly": 1.5,
    "exceptionally": 1.8,
    "utterly": 1.8,
    "remarkably": 1.5,
}

POSITIVE_PHRASES = [
    "looking forward", "can't wait", "cannot wait",
    "well done", "good job", "thank you", "love it",
    "love this", "works perfectly", "highly recommend",
    "exceeded expectations", "better than expected",
    "worth every penny", "made my day", "pleased with",
    "easy to use", "great experience", "very happy",
    "really good", "really great", "pretty good",
    "not bad", "not disappointed", "no problem",
    "nothing wrong", "best ever", "works great",
    "feel good", "feeling good", "well worth",
]

NEGATIVE_PHRASES = [
    "fed up", "waste of time", "waste of money",
    "not worth", "never again", "very disappointed",
    "not happy", "not good", "not great", "not satisfied",
    "not working", "doesn't work", "does not work",
    "didn't work", "did not work", "can't recommend",
    "cannot recommend", "poor quality", "worst experience",
    "really bad", "really terrible", "very bad",
    "very poor", "very frustrating", "so disappointed",
    "not impressed", "no good", "broke down",
    "fell apart", "completely useless", "highly disappointed",
]


def analyze_sentiment(sentence: str) -> str:
    text = sentence.lower().replace("’", "'")

    # Normalize common contractions.
    text = re.sub(r"\bwon't\b", "will not", text)
    text = re.sub(r"\bcan't\b", "can not", text)
    text = re.sub(r"\bcannot\b", "can not", text)
    text = re.sub(r"\bain't\b", "is not", text)
    text = re.sub(r"\bisn't\b", "is not", text)
    text = re.sub(r"\baren't\b", "are not", text)
    text = re.sub(r"\bwasn't\b", "was not", text)
    text = re.sub(r"\bweren't\b", "were not", text)
    text = re.sub(r"\bdon't\b", "do not", text)
    text = re.sub(r"\bdoesn't\b", "does not", text)
    text = re.sub(r"\bdidn't\b", "did not", text)
    text = re.sub(r"\bcouldn't\b", "could not", text)
    text = re.sub(r"\bwouldn't\b", "would not", text)
    text = re.sub(r"\bshouldn't\b", "should not", text)

    positive_score = 0.0
    negative_score = 0.0

    # Phrase matching captures expressions that individual words miss.
    for phrase in POSITIVE_PHRASES:
        if phrase in text:
            positive_score += 2.0

    for phrase in NEGATIVE_PHRASES:
        if phrase in text:
            negative_score += 2.0

    # Emojis and emoticons.
    if any(x in sentence for x in ("😊", "😃", "😄", "😁", "😍", "❤️", "❤", "👍", "🎉", "🙂")):
        positive_score += 2.0

    if any(x in sentence for x in ("😢", "😭", "😡", "😠", "👎", "💔", "😞", "☹", "🙁")):
        negative_score += 2.0

    words = re.findall(r"[a-z]+(?:'[a-z]+)?", text)
    negate_count = 0
    multiplier = 1.0

    for word in words:
        if word in NEGATIONS:
            negate_count = 3
            continue

        if word in INTENSIFIERS:
            multiplier = INTENSIFIERS[word]
            continue

        score = 0.0

        if word in POSITIVE_WORDS:
            score = 1.0
        elif word in NEGATIVE_WORDS:
            score = -1.0

        if score != 0:
            if negate_count > 0:
                score *= -1

            score *= multiplier

            if score > 0:
                positive_score += score
            else:
                negative_score += abs(score)

            multiplier = 1.0

        if negate_count > 0:
            negate_count -= 1

    # Handle repeated punctuation as a mild intensity signal.
    if "!" in sentence:
        if positive_score > negative_score:
            positive_score += 0.25
        elif negative_score > positive_score:
            negative_score += 0.25

    if positive_score > negative_score:
        return "happy"

    if negative_score > positive_score:
        return "sad"

    return "neutral"


def make_results(request: SentimentRequest):
    return {
        "results": [
            {
                "sentence": sentence,
                "sentiment": analyze_sentiment(sentence),
            }
            for sentence in request.sentences
        ]
    }


@app.post("/sentiment")
async def batch_sentiment(request: SentimentRequest):
    return make_results(request)


# Also support evaluators that POST directly to the base URL.
@app.post("/")
async def sentiment_root(request: SentimentRequest):
    return make_results(request)


@app.get("/")
def home():
    return {"message": "Student and sentiment APIs are running"}
