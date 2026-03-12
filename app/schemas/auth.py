from pydantic import BaseModel


from app.schemas.users import User

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class UserLogin(BaseModel):
    email: str
    password: str

class AuthLoginResponse(Token):
    user: User

class CurrentUserToken(BaseModel):
    email: str
    role: str