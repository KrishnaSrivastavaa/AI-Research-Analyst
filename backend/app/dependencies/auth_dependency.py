from supabase import create_client
from app.core.configs import settings
from fastapi import HTTPException, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


supabase = create_client(settings.supabase_url, settings.supabase_key)

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials =  Depends(security)):
    try: 
        jwt = credentials.credentials
        response = supabase.auth.get_claims(jwt)
        print(response)
        print(type(response))
        return response["claims"]

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )