

import csv
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
            student
            for student in students
            if student["class"] in wanted_classes
        ]
    else:
        result = students

    return {"students": result}


@app.get("/")
def home():
    return {"message": "Student API is running"}
