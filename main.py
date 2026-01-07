import os
import mysql.connector
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=os.getenv("MYSQLPORT")
    )

@app.post("/submit-report")
async def handle_form(initials: str = Form(...), batch: str = Form(...), description: str = Form(...)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Save Patient and Product info
        cursor.execute("INSERT INTO Patients (PatientInitials) VALUES (%s)", (initials,))
        p_id = cursor.lastrowid
        cursor.execute("INSERT INTO Products (ProductName, BatchNumber) VALUES ('HIUS', %s)", (batch,))
        prod_id = cursor.lastrowid
        cursor.execute("INSERT INTO AdverseEvents (EventVerbatim) VALUES (%s)", (description,))
        ev_id = cursor.lastrowid

        # 2. Create the ICSR Link with the Case Number format from SOP
        case_no = f"RMP/HIUS/26/{p_id}" 
        cursor.execute("INSERT INTO ICSR_Reports (CaseNumber, PatientID, ProductID, EventID) VALUES (%s, %s, %s, %s)",
                       (case_no, p_id, prod_id, ev_id))
        conn.commit()
        return HTMLResponse(content=f"<h2>Success! Report {case_no} recorded.</h2>")
    finally:
        cursor.close()
        conn.close()
if __name__ == "__main__":
    import uvicorn
    import os
    # Railway provides the port number via an environment variable named 'PORT'
    port = int(os.environ.get("PORT", 8000))
    # This starts the server on the correct port so your website can connect
    uvicorn.run(app, host="0.0.0.0", port=port)
