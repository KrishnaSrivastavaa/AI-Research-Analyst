from fastapi import APIRouter, Depends, HTTPException
from app.schemas.authSchema import Signin_Schema, SignUp_Schema
from supabase import create_client
from app.core.configs import settings

supabase = create_client(settings.supabase_url, settings.supabase_key)


router = APIRouter()


@router.post("/signup")
async def signup(user: SignUp_Schema):

    response = supabase.auth.sign_up(
    {
        "email": user.email,
        "password": user.password,
        "options": {
            "data": {
                "name": user.name,
                "username": user.username,
                "avatar_url": user.avatar_url
                }
            }
        }
    )

    if not response.user:
        raise HTTPException(
            status_code=400,
            detail="Signup failed"
        )

    return {
        "message": "Signup successful",
        "user_id": response.user.id
    }


@router.post("/signin")
async def signin(user: Signin_Schema):

    try:

        response = supabase.auth.sign_in_with_password(
            {
                "email": user.email,
                "password": user.password,
            }
        )

        return {
            "message": "Signin successful",
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "user_id": response.user.id
        }

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )
