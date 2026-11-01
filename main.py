import json
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse

app = FastAPI()

class Patient(BaseModel):

    id: Annotated[str, Field(..., description='ID of the patient', examples=['P001'])]
    name: Annotated[str, Field(..., description='Name of the patient')]
    city: Annotated[str, Field(..., description='City where the patient is living')]
    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description='Gender of the patient')]
    height: Annotated[float, Field(..., gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the patient in kgs')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'Normal'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None, description='Name of the patient')]
    city: Annotated[Optional[str], Field(None, description='City where the patient is living')]
    age: Annotated[Optional[int], Field(None, gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(None, description='Gender of the patient')]
    height: Annotated[Optional[float], Field(None, gt=0, description='Height of the patient in mtrs')]
    weight: Annotated[Optional[float], Field(None, gt=0, description='Weight of the patient in kgs')]

def load_data():
    with open('patients.json', 'r') as file:
        data = json.load(file)
        return data

def save_data(data):
    with open('patients.json', 'w') as f:
        json.dump(data, f)

#1
@app.get("/")
def hello():
    return {"message": "Patient Management System API"}


#2
@app.get("/about")
def about():
    return {"message": "Fully Functional API for Patient Management System using FastAPI and Python."}

#3
@app.get("/view")
def view():
    data = load_data()
    return data

#4

@app.get("/view/patient/{patient_id}")
def view_patient(patient_id: str = Path(..., description="The ID of the patient to retrieve", example="P001")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found.")

@app.get("/sort")
def sort_patients(sort_by : str = Query(..., description="sort on basis of height, weight or bmi"), order :str = Query('asc', description="order of sorting, can be 'asc' or 'desc'")):

    valid_fields = ['height', 'weight', 'bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Must be one of {valid_fields}.")

    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid order. Must be 'asc' or 'desc'.")

    data = load_data()

    sort_order = True if order == 'desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=sort_order)

    return sorted_data

#5
@app.post('/create')
def create_patient(patient: Patient):

    # load existing data
    data = load_data()

    # check if the patient already exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')

    # new patient add to the database
    data[patient.id] = patient.model_dump(exclude=['id'])

    # save into the json file
    save_data(data)

    return JSONResponse(status_code=201, content={'message':'patient created successfully'})

#6
@app.put('/edit/{patient_id}')
def edit_patient(patient_id: str, patient_update: PatientUpdate):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    existing_patient_info = data[patient_id]

    patient_update_dict = patient_update.model_dump(exclude_unset=True)

    for key, value in patient_update_dict.items():
        existing_patient_info[key] = value

    updated_patient_object = Patient(id=patient_id, **existing_patient_info)

    save_patient_dict = updated_patient_object.model_dump(exclude=['id'])

    data[patient_id] = save_patient_dict

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient updated successfully'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):

    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail='Patient not found')

    del data[patient_id]

    save_data(data)

    return JSONResponse(status_code=200, content={'message':'patient deleted successfully'})