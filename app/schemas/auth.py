from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayLoad(BaseModel):
    sub: str
