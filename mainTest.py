from fastapi import FastAPI, UploadFile, File, Form,Body
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pydantic import BaseModel
from starlette.responses import JSONResponse
from googleapiclient.http import MediaIoBaseUpload
import io
from pymongo import MongoClient
from datetime import datetime
from typing import List, Optional, Union
import config
# Create the FastAPI app
app = FastAPI(docs_url=None, redoc_url=None)


# Create a service object for the Google Sheets API
service = build('sheets', 'v4', credentials=config.credentials)


class Item(BaseModel):
    Dcontact: Optional[Union[int, str]] = None
    ParentName: Optional[Union[int, str]] = None
    ChildName: Optional[Union[int, str]] = None
    Gender: Optional[Union[int, str]] = None
    PContact: Optional[Union[int, str]] = None
    CAge: Optional[Union[int, str]] = None
    CHeight: Optional[Union[int, str]] = None
    Cweight: Optional[Union[int, str]] = None
    HCPName: Optional[Union[int, str]] = None
    ABMName: Optional[Union[int, str]] = None
    PharmaName: Optional[Union[int, str]] = None
    Quantity: Optional[Union[int, str]] = None
    child_stunted: Optional[Union[int, str]] = None
    child_wasted: Optional[Union[int, str]] = None
    child_underweight: Optional[Union[int, str]] = None
    cal_intake: Optional[Union[int, str]] = None
    protein_intake: Optional[Union[int, str]] = None
    micro_intake_z: Optional[Union[int, str]] = None
    micro_intake_i: Optional[Union[int, str]] = None
    micro_intake_v: Optional[Union[int, str]] = None
    calcium_intake: Optional[Union[int, str]] = None
    sugar_intake: Optional[Union[int, str]] = None
    child_picky: Optional[Union[int, str]] = None
    diet_details: Optional[Union[int, str]] = None
    diagnosis: Optional[Union[int, str]] = None
    present_symptoms: Optional[Union[int, str]] = None
    Hospital_adm_in_year: Optional[Union[int, str]] = None
    no_of_clinic_in_year: Optional[Union[int, str]] = None
    no_of_days_of_ab_school: Optional[Union[int, str]] = None



class UploadedImage(BaseModel):
    PUrl: Optional[str]
    PopUrl: Optional[str]


@app.post("/upload-data")
async def upload_data(
        Dcontact: Optional[Union[int, str]] = Form(None),
        ParentName: Optional[Union[int, str]] = Form(None),
        ChildName: Optional[Union[int, str]] = Form(None),
        Gender: Optional[Union[int, str]] = Form(None),
        PContact: Optional[Union[int, str]] = Form(None),
        CAge: Optional[Union[int, str]] = Form(None),
        CHeight: Optional[Union[int, str]] = Form(None),
        Cweight: Optional[Union[int, str]] = Form(None),
        Pimage: Optional[UploadFile] = File(None),
        HCPName: Optional[Union[int, str]] = Form(None),
        ABMName: Optional[Union[int, str]] = Form(None),
        PharmaName: Optional[Union[int, str]] = Form(None),
        Quantity: Optional[Union[int, str]] = Form(None),
        Popimage: Optional[UploadFile] = File(None),
        child_stunted: Optional[Union[int, str]] = Form(None),
        child_wasted: Optional[Union[int, str]] = Form(None),
        child_underweight: Optional[Union[int, str]] = Form(None),
        cal_intake: Optional[Union[int, str]] = Form(None),
        protein_intake: Optional[Union[int, str]] = Form(None),
        micro_intake_z: Optional[Union[int, str]] = Form(None),
        micro_intake_i: Optional[Union[int, str]] = Form(None),
        micro_intake_v: Optional[Union[int, str]] = Form(None),
        calcium_intake: Optional[Union[int, str]] = Form(None),
        sugar_intake: Optional[Union[int, str]] = Form(None),
        child_picky: Optional[Union[int, str]] = Form(None),
        diet_details: Optional[Union[int, str]] = Form(None),
        diagnosis: Optional[Union[int, str]] = Form(None),
        present_symptoms: Optional[Union[int, str]] = Form(None),
        Hospital_adm_in_year: Optional[Union[int, str]] = Form(None),
        no_of_clinic_in_year: Optional[Union[int, str]] = Form(None),
        no_of_days_of_ab_school: Optional[Union[int, str]] = Form(None)
):
    # Read the contents of the uploaded image file
    Pimage_data = await Pimage.read() if Pimage is not None else None
    Popimage_data = await Popimage.read() if Popimage is not None else None

    # Upload the image to Google Drive
    drive_service = build('drive', 'v3', credentials=config.credentials)
    file_id = None
    file_id1 = None

    if Pimage_data is not None:
        file_metadata = {
            'name': Pimage.filename,
            'parents': [config.folder_id]
        }
        media = MediaIoBaseUpload(io.BytesIO(Pimage_data), mimetype=Pimage.content_type)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

    if Popimage_data is not None:
        file_metadata1 = {
            'name': Popimage.filename,
            'parents': [config.folder_id]
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
        spreadsheetId=config.spreadsheet_id,
        range=config.cell_range,
        valueInputOption='RAW',
        body=body
    ).execute()

    return JSONResponse({"message": "Data and Image uploaded successfully"})



class Register(BaseModel):
    Name: str
    PhoneNumber: str
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
    result = config.collection.insert_one(item_data)

    # Return the inserted document ID
    return {"message": "Item created", "item_id": str(result.inserted_id)}


class UserDetails(BaseModel):
    Name: str
    PhoneNumber: str
    Password: str
    City: str
    Team: str


@app.post("/GetUserDetails")
async def Get_details(phone: str):
    result = config.collection.find({"PhoneNumber": phone})
    data = [UserDetails(**data) for data in result]
    return data

@app.post("/login")
async def Get_details(phone: str = Body(...), password: str = Body(...)) :

    result = list(config.collection.find({"PhoneNumber": phone, "Password": password}))
    if len(result) == 0:
        return {'Message': 'Incorrect Phone Number or Password'}
    else:
        return {'Message': 'Welcome to the app'}

@app.post("/CheckUserExist")
async def check_details(phone: str):
    result = list(config.collection.find({"PhoneNumber": phone}))

    # Check if the result is empty
    if len(result) == 0:
        return {'Message': 'User not found'}
    else:
        return {'Message': 'Welcome to the app'}


@app.get("/viewallusers")
async def view_all_users():
    result = config.collection.find({}, {"_id": 0})  # Exclude the _id field
    return list(result)


@app.delete("/deleteuser")
async def delete_user(phone: str):
    result = config.collection.delete_one({"PhoneNumber": phone})
    if result.deleted_count:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found"}





class History(BaseModel):
    PContact: Union[int, str]
    ChildName: str

@app.post("/history", response_model=List[History])
async def get_records_by_phone_number(phone_number: str = Body(...)):
    # Retrieve the data from the Google Sheet
    result = service.spreadsheets().values().get(
        spreadsheetId=config.spreadsheet_id,
        range='Sheet1'  # Replace with the actual sheet name or range containing the data
    ).execute()

    values = result.get('values', [])

    if not values or len(values) < 2:
        return []

    variables = values[0]

    # Find the index of "Dcontact" in the header row
    try:
        dcontact_index = variables.index("Dcontact")
    except ValueError:
        # "Dcontact" field not found in the header row
        return []

    # Filter records by phone number
    filtered_records = [
        dict(zip(variables, row))
        for row in values[1:]
        if row and len(row) > dcontact_index and str(row[dcontact_index]) == phone_number
    ]

    # Sort records by timestamp in descending order
    sorted_records = sorted(filtered_records, key=lambda x: x.get("TimeStamp", ""), reverse=True)

    # Select the top 20 records
    top_records = sorted_records[:20]

    # Create instances of History model
    records = [History(**record) for record in top_records]

    return records

class PhoneNumber(BaseModel):
    phone_number: str
@app.post("/check_phone_number")
async def check_phone_number(phone_number: PhoneNumber):
    result = config.collection.find_one({"PhoneNumber": phone_number.phone_number})
    if result:
        return {"message": "Login Successful"}
    else:
        return {"message": "User not Registered"}