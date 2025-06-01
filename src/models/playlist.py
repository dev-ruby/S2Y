from pydantic import BaseModel


class PlaylistRequest(BaseModel):
    url: str
