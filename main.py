


from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,

    allow_methods=["*"],
    allow_headers=["*"],
)



# Webhook to receive data
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()  # Extract JSON payload
        extracted_data = data.get("extracted_data", {})  # Extract `extracted_data`

        if not extracted_data:
            raise HTTPException(status_code=400, detail="No extracted_data found in request")

        # Log the extracted data (you can modify this to store/process it)
        logging.info(f"Received extracted_data: {extracted_data}")
        print(extracted_data)
        return {"message": "Webhook received successfully", "extracted_data": extracted_data}

    except Exception as e:
        logging.exception("Error in processing webhook")
        raise HTTPException(status_code=500, detail=str(e))
