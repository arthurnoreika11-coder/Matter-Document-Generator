from pydantic import BaseModel, ConfigDict, EmailStr

class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

class WelcomeEmailSchema(StrictModel):
    email: EmailStr
    matter_reference: str
    client_name: str
    client_email: EmailStr

class CaseUpdateEmailSchema(StrictModel):
    email: EmailStr
    matter_reference: str
    client_name: str
    client_email: EmailStr
    case_update_summary: str