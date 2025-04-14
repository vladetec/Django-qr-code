from ninja import ModelSchema, Schema
from .models import Links
from datetime import timedelta
from typing import Dict

class ShortenUrlIn(ModelSchema):
    expiration_time: int
    
    class Meta:
        model = Links
        fields = ['redirect_link', 'token', 'expiration_time', 'max_unique_cliques']
        
    def to_model_data(self):
        return {
            "redirect_link": self.redirect_link,
            "token": self.token,
            "expiration_time": timedelta(minutes=self.expiration_time),
            "max_unique_cliques": self.max_unique_cliques
        }
        
    @classmethod
    def from_model(cls, instance: Links):
        return cls(
            redirect_link=instance.redirect_link,
            token=instance.token,
            expiration_time=instance.expiration_time.seconds // 60,
            max_unique_cliques=instance.max_unique_cliques
        )

class UpdateLinkSchema(Schema):
    redirect_link: str | None = None
    token: str | None = None
    expiration_time: int | None = None
    max_unique_cliques: int | None = None
    
class StatisticsResponse(Schema):
    uniques_clicks: int
    total_clicks: int
    daily_clicks: Dict[str, int]