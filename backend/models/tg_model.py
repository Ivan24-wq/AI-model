from pydantic import BaseModel

class TgReg(BaseModel):
    user_id: int
    first_name: str | None
    last_name: str | None
    username: str | None