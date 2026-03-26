from fastapi import APIRouter, Depends, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.connection import get_db
import pandas as pd
from src.model.predict import predict_all   # USE MODEL

router = APIRouter()

# CREATE NEW TICKET (MODEL BASED)
@router.post("/new-ticket")
def create_ticket(
    customer_name: str = Form(...),
    product: str = Form(...),
    issue: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # AI MODEL (FINAL)
        sentiment, priority, response = predict_all(issue)

        # DATABASE INSERT
        query = text("""
            INSERT INTO tickets (
                customer_name,
                product_purchased,
                ticket_description,
                ticket_type,
                ticket_priority,
                sentiment,
                suggested_response,
                is_high_priority
            ) VALUES (
                :customer_name,
                :product,
                :issue,
                :type,
                :priority,
                :sentiment,
                :response,
                :is_high_priority
            )
        """)

        db.execute(query, {
            "customer_name": customer_name,
            "product": product,
            "issue": issue,
            "type": "Customer Query",
            "priority": priority,
            "sentiment": sentiment,
            "response": response, 
            "is_high_priority": 1 if priority.lower() in ["high", "critical"] else 0
        })

        db.commit()

        return {
            "message": "Ticket created successfully",
            "sentiment": sentiment,
            "priority": priority,
            "response": response
        }

    except Exception as e:
        return {"error": str(e)}


# GET ALL TICKETS
@router.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):

    result = db.execute(text("SELECT * FROM tickets LIMIT 1000"))
    
    rows = result.fetchall()
    columns = result.keys()

    data = []
    for row in rows:
        record = {}
        for i, col in enumerate(columns):
            value = row[i]

            # Fix NaN safely
            if isinstance(value, float) and pd.isna(value):
                value = None

            record[col] = value
        
        data.append(record)

    return data


# COUNT
@router.get("/count")
def count(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT COUNT(*) FROM tickets"))
    return {"total_rows": result.scalar()}

# DEBUG COLUMNS
@router.get("/debug-columns")
def debug_columns(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM tickets LIMIT 1"))
    return list(result.keys())

# DROP TABLE
@router.get("/drop-table")
def drop_table(db: Session = Depends(get_db)):
    db.execute(text("DROP TABLE IF EXISTS tickets"))
    db.commit()
    return {"message": "Table dropped"}


# INSIGHTS API
@router.get("/insights")
def get_insights(db: Session = Depends(get_db)):
    try:
        total = db.execute(text("SELECT COUNT(*) FROM tickets")).scalar()

        high_priority = db.execute(
            text("SELECT COUNT(*) FROM tickets WHERE is_high_priority = 1")
        ).scalar()

        return {
            "total_tickets": int(total or 0),
            "high_priority": int(high_priority or 0),
            "avg_resolution_time": 0,   # TEMP FIX
            "avg_satisfaction": 0       # TEMP FIX
        }

    except Exception as e:
        return {"error": str(e)}


# SENTIMENT DISTRIBUTION
@router.get("/sentiment")
def sentiment_analysis(db: Session = Depends(get_db)):

    result = db.execute(text("""
        SELECT sentiment, COUNT(*) 
        FROM tickets 
        GROUP BY sentiment
    """))

    data = {row[0]: row[1] for row in result}

    return data


# RESPONSE GENERATOR
@router.post("/suggest-response")
def suggest_response(text: str):
    sentiment, priority, response = predict_all(text)

    return {
        "sentiment": sentiment,
        "priority": priority,
        "suggested_response": response
    }