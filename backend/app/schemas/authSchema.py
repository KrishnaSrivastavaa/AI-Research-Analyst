from pydantic import BaseModel, EmailStr


class SignUp_Schema(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str
    avatar_url: str | None = None
    



class Signin_Schema(BaseModel):
    email: EmailStr 
    password: str 