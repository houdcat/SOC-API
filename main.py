from fastapi import FastAPI, HTTPException, Query
from typing import Optional
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="SOČ API",
    description="API pro správu a archivaci SOČ",
    version="1.1.0",
    docs_url="/api",
    openapi_url="/api/openapi.json"
)

participants = [
    {"id": 1, "name": "Jan Novák", "school": "SPŠE Praha", "contact": "jan.novak@email.cz", "grade": 3, "field": "Informatika"},
    {"id": 2, "name": "Eva Dvořáková", "school": "Gymnázium Brno", "contact": "eva.d@email.cz", "grade": 4, "field": "Chemie"},
]

works = [
    {"id": 1, "title": "Umělá inteligence ve vzdělávání", "field": "Informatika", "annotation": "Využití AI při vzdělávání studentů.", "advisor": "Mgr. Novotný", "school": "SPŠE Praha", "year": 2024, "participant_id": 1},
    {"id": 2, "title": "Vliv mikroplastů na životní prostředí", "field": "Chemie", "annotation": "Analýza znečištění mikroplasty v řekách.", "advisor": "RNDr. Černá", "school": "Gymnázium Brno", "year": 2023, "participant_id": 2},
]

results = [
    {"work_id": 1, "placement": 1, "advanced": True},
    {"work_id": 2, "placement": 2, "advanced": False},
]

@app.get("/")
def root():
    return {"message": "Dokumentace na /api"}


@app.get("/works", summary="Získání seznamu prací")
def get_works(
    keyword: Optional[str] = Query(None, description="Hledaný text v názvu práce"),
    field: Optional[str] = Query(None, description="Obor práce"),
    year: Optional[int] = Query(None, description="Rok SOČ"),
):
    """Vrátí seznam prací podle filtru."""
    results_list = works
    if keyword:
        results_list = [w for w in results_list if keyword.lower() in w["title"].lower()]
    if field:
        results_list = [w for w in results_list if w["field"].lower() == field.lower()]
    if year:
        results_list = [w for w in results_list if w["year"] == year]
    return results_list

@app.post("/works", summary="Přidání nové práce")
def add_work(work: dict):
    """Přidání práce podle"""
    new_id = max([w["id"] for w in works]) + 1 if works else 1
    work["id"] = new_id
    works.append(work)
    return {"message": "Práce byla úspěšně přidána.", "work": work}

@app.delete("/works/{work_id}", summary="Smazání práce")
def delete_work(work_id: int):
    """Odstraní práci podle ID"""
    for w in works:
        if w["id"] == work_id:
            works.remove(w)
            return {"message": "Práce byla odstraněna."}
    raise HTTPException(status_code=404, detail="Práce nebyla nalezena.")


@app.get("/participants", summary="Získání seznamu účastníků")
def get_participants():
    """Vrátí seznam všech účastníků"""
    return participants

@app.post("/participants", summary="Přidání účastníka")
def add_participant(participant: dict):
    """Přidá nového účastníka"""
    new_id = max([p["id"] for p in participants]) + 1 if participants else 1
    participant["id"] = new_id
    participants.append(participant)
    return {"message": "Účastník byl přidán.", "participant": participant}


@app.get("/results", summary="Výsledky SOČ")
def get_results():
    """Vrátí výsledky všech prací"""
    data = []
    for r in results:
        work = next((w for w in works if w["id"] == r["work_id"]), None)
        if work:
            data.append({
                "title": work["title"],
                "placement": r["placement"],
                "advanced": r["advanced"],
                "year": work["year"]
            })
    return data


@app.get("/export/csv", summary="Export dat do CSV")
def export_csv():
    """Export všech prací do CSV formátu"""
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "title", "field", "year", "school", "advisor"])
    writer.writeheader()
    for w in works:
        writer.writerow(w)
    output.seek(0)
    return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=works.csv"})
