from fastapi import FastAPI, UploadFile, File, Form,Body
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from starlette.responses import JSONResponse
from googleapiclient.http import MediaIoBaseUpload
import io
from pymongo import MongoClient
from datetime import datetime
from typing import List, Optional

app = FastAPI()

# MongoDB connection settings
mongo_client = MongoClient(
    "mongodb+srv://Anuradha_24:veX84lLLxoNu7KxJ@cluster0.f0a4v6c.mongodb.net/?retryWrites=true&w=majority")
db = mongo_client["userData"]
collection = db["Users"]

# Load credentials from the downloaded JSON file
credentials = service_account.Credentials.from_service_account_file("./googleauthkey1.json",
                                                                    scopes=[
                                                                        'https://www.googleapis.com/auth/spreadsheets',
                                                                        'https://www.googleapis.com/auth/drive']
                                                                    )

# Google Drive folder ID
folder_id = "1zvwHTvXWiNtqf_fKUXV1TT-bAWO_osT6"

# Google Sheets document ID
spreadsheet_id = "1ohoeiDUwStakeO6VtUnxwySL6zHvc_gyl6TjLI6dq5Q"
spreadsheet_id1 = "1DjP5PDdvtqecfh2YTXZHGDSQM5jgO_jUuIVBpBgLvWM"
cell_range = 'Sheet1!A2'

# Create a service object for the Google Sheets API
service = build('sheets', 'v4', credentials=credentials)


class Item(BaseModel):
    Dcontact: Optional[int] = None
    ParentName: Optional[str] = None
    ChildName: Optional[str] = None
    Gender: Optional[str] = None
    PContact: Optional[int] = None
    CAge: Optional[int] = None
    CHeight: Optional[int] = None
    Cweight: Optional[int] = None
    HCPName: Optional[str] = None
    ABMName: Optional[str] = None
    PharmaName: Optional[str] = None
    Quantity: Optional[int] = None
    child_stunted: Optional[str] = None
    child_wasted: Optional[str] = None
    child_underweight: Optional[str] = None
    cal_intake: Optional[int] = None
    protein_intake: Optional[int] = None
    micro_intake_z: Optional[int] = None
    micro_intake_i: Optional[int] = None
    micro_intake_v: Optional[int] = None
    calcium_intake: Optional[int] = None
    sugar_intake: Optional[int] = None
    child_picky: Optional[int] = None
    diet_details: Optional[str] = None
    diagnosis: Optional[str] = None
    present_symptoms: Optional[str] = None
    Hospital_adm_in_year: Optional[int] = None
    no_of_clinic_in_year: Optional[int] = None
    no_of_days_of_ab_school: Optional[int] = None


class UploadedImage(BaseModel):
    PUrl: Optional[str]
    PopUrl: Optional[str]


@app.post("/upload-data")
async def upload_data(
        Dcontact: Optional[int] = Form(None),
        ParentName: Optional[str] = Form(None),
        ChildName: Optional[str] = Form(None),
        Gender: Optional[str] = Form(None),
        PContact: Optional[int] = Form(None),
        CAge: Optional[int] = Form(None),
        CHeight: Optional[int] = Form(None),
        Cweight: Optional[int] = Form(None),
        Pimage: Optional[UploadFile] = File(None),
        HCPName: Optional[str] = Form(None),
        ABMName: Optional[str] = Form(None),
        PharmaName: Optional[str] = Form(None),
        Quantity: Optional[int] = Form(None),
        Popimage: Optional[UploadFile] = File(None),
        child_stunted: Optional[str] = Form(None),
        child_wasted: Optional[str] = Form(None),
        child_underweight: Optional[str] = Form(None),
        cal_intake: Optional[int] = Form(None),
        protein_intake: Optional[int] = Form(None),
        micro_intake_z: Optional[int] = Form(None),
        micro_intake_i: Optional[int] = Form(None),
        micro_intake_v: Optional[int] = Form(None),
        calcium_intake: Optional[int] = Form(None),
        sugar_intake: Optional[int] = Form(None),
        child_picky: Optional[str] = Form(None),
        diet_details: Optional[str] = Form(None),
        diagnosis: Optional[str] = Form(None),
        present_symptoms: Optional[str] = Form(None),
        Hospital_adm_in_year: Optional[int] = Form(None),
        no_of_clinic_in_year: Optional[int] = Form(None),
        no_of_days_of_ab_school: Optional[int] = Form(None)
):
    # Read the contents of the uploaded image file
    Pimage_data = await Pimage.read() if Pimage is not None else None
    Popimage_data = await Popimage.read() if Popimage is not None else None

    # Upload the image to Google Drive
    drive_service = build('drive', 'v3', credentials=credentials)
    file_id = None
    file_id1 = None

    if Pimage_data is not None:
        file_metadata = {
            'name': Pimage.filename,
            'parents': [folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(Pimage_data), mimetype=Pimage.content_type)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

    if Popimage_data is not None:
        file_metadata1 = {
            'name': Popimage.filename,
            'parents': [folder_id]
        }
        media1 = MediaIoBaseUpload(io.BytesIO(Popimage_data), mimetype=Popimage.content_type)
        file1 = drive_service.files().create(body=file_metadata1, media_body=media1, fields='id').execute()
        file_id1 = file1.get('id')

    cheightm2 = (CHeight / 100) ** 2 if CHeight is not None else None
    bmi = round((Cweight / cheightm2), 2) if Cweight is not None and cheightm2 is not None else None
    timestamp = datetime.now().isoformat()

    # Populate "null" instead of skipping empty values
    values = [
        [
            timestamp, Dcontact, ParentName, ChildName, Gender,
            PContact, CAge, CHeight, Cweight, bmi, file_id,
            HCPName, ABMName, PharmaName, Quantity, file_id1,
            child_stunted, child_wasted, child_underweight, cal_intake,
            protein_intake, micro_intake_z, micro_intake_i, micro_intake_v,
            calcium_intake, sugar_intake, child_picky, diet_details,
            diagnosis, present_symptoms, Hospital_adm_in_year,
            no_of_clinic_in_year, no_of_days_of_ab_school
        ]
    ]
    body = {
        'values': values
    }
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    return JSONResponse({"message": "Data and Image uploaded successfully"})


class Register(BaseModel):
    Name: str
    PhoneNumber: int
    Password: str
    City: str
    Team: str


@app.post("/Register")
async def register_data(register: Register):
    item_data = {
        "Name": register.Name,
        "PhoneNumber": register.PhoneNumber,
        "Password": register.Password,
        "City": register.City,
        "Team": register.Team
    }

    # Insert the item into the MongoDB collection
    result = collection.insert_one(item_data)

    # Return the inserted document ID
    return {"message": "Item created", "item_id": str(result.inserted_id)}


class UserDetails(BaseModel):
    Name: str
    PhoneNumber: int
    Password: str
    City: str
    Team: str


@app.post("/GetUserDetails")
async def Get_details(phone: int):
    result = collection.find({"PhoneNumber": phone})
    data = [UserDetails(**data) for data in result]
    return data

@app.post("/login")
async def Get_details(phone: int = Body(...), password: str = Body(...)) :

    result = list(collection.find({"PhoneNumber": phone, "Password": password}))
    if len(result) == 0:
        return {'Message': 'Incorrect Phone Number or Password'}
    else:
        return {'Message': 'Welcome to the app'}

@app.post("/CheckUserExist")
async def check_details(phone: int):
    result = list(collection.find({"PhoneNumber": phone}))

    # Check if the result is empty
    if len(result) == 0:
        return {'Message': 'User not found'}
    else:
        return {'Message': 'Welcome to the app'}


@app.get("/viewallusers")
async def view_all_users():
    result = collection.find({}, {"_id": 0})  # Exclude the _id field
    return list(result)


@app.delete("/deleteuser")
async def delete_user(phone: int):
    result = collection.delete_one({"PhoneNumber": phone})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}


class History(BaseModel):
    PContact: int
    ChildName: str



@app.post("/history")
async def get_records_by_phone_number(request_body: dict = Body(...)) -> List[History]:
    phone_number = request_body.get("phone_number")
    # Retrieve the data from the Google Sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range='Sheet1'
    ).execute()

    values = result.get('values', [])

    variables = values[0] if values else []

    # Filter records by phone number
    filtered_records = [
        dict(zip(variables, row))
        for row in values[1:]
        if row and str(row[variables.index("Dcontact")]) == phone_number
    ]

    # Sort records by timestamp in descending order
    sorted_records = sorted(filtered_records, key=lambda x: x.get("TimeStamp", ""), reverse=True)

    # Select the top 20 records
    top_records = sorted_records[:20]

    # Create instances of History model
    records = [
        History(**record)  # Adjust the fields as per your sheet's structure
        for record in top_records
    ]

    return records


class Uplaoddatatest(BaseModel):
    ParentName: str


@app.post("/upload-data-test")
async def upload_data_test(uplaod: Uplaoddatatest,

                           ):
    # Read the contents of the uploaded image file
    # Read the contents of the uploaded image file
    # Read the contents of the uploaded image file

    values = [
        [
            uplaod.ParentName
        ]





        
    ]
    body = {
        'values': values
    }
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    return JSONResponse({"message": "Data  uploaded successfully"})
class PhoneNumber(BaseModel):
    phone_number: int
@app.post("/check_phone_number")
async def check_phone_number(phone_number: PhoneNumber):
    result = collection.find_one({"PhoneNumber": phone_number.phone_number})
    if result:
        return {"message": "Login Successful"}
    else:
        return {"message": "User not Registered"}