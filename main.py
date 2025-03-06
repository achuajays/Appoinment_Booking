from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncpg
import logging
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # Replace with your PostgreSQL connection URL

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database connection pool
async def init_db():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS webhook_data (
                id SERIAL PRIMARY KEY,
                date TEXT NOT NULL,
                reason TEXT NOT NULL,
                patient_id TEXT NOT NULL
            )
        """)
        await conn.close()
    except Exception as e:
        logging.error(f"Database initialization error: {e}")

@app.on_event("startup")
async def startup():
    await init_db()

# Webhook to receive data
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()  # Extract JSON payload
        extracted_data = data.get("extracted_data", {})  # Extract `extracted_data`

        if not extracted_data:
            raise HTTPException(status_code=400, detail="No extracted_data found in request")

        date = extracted_data.get("date")
        reason = extracted_data.get("reason")
        patient_id = extracted_data.get("patient_id")

        if not (date and reason and patient_id):
            raise HTTPException(status_code=400, detail="Missing required fields")

        # Save to PostgreSQL
        conn = await asyncpg.connect(DATABASE_URL)
        await conn.execute(
            "INSERT INTO webhook_data (date, reason, patient_id) VALUES ($1, $2, $3)",
            date, reason, patient_id
        )
        await conn.close()

        logging.info(f"Saved to database: {extracted_data}")
        return {"message": "Webhook received and data saved", "extracted_data": extracted_data}

    except Exception as e:
        logging.exception("Error in processing webhook")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
