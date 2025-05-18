from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Page(BaseModel):
    page_id: str
    user_id: str
    user_name: str
    domain: str
    page_title: str
    created_at: datetime

class PageList(BaseModel):
    pages: List[Page]

class DomainList(BaseModel):
    domains: List[str]

class PageCount(BaseModel):
    domain: str
    count: int

class SinglePage(BaseModel):
    page: Page

class UserStat(BaseModel):
    user_id: str
    user_name: str
    count: int

class UserStatResponse(BaseModel):
    from_: str
    to: str
    users: List[UserStat]

class HourlyDomainStat(BaseModel):
    time_start: str
    time_end: str
    statistics: List[Dict[str, int]]

class BotStatItem(BaseModel):
    domain: str
    created_by_bots: int

class BotStats(BaseModel):
    time_start: str
    time_end: str
    statistics: List[BotStatItem]

class UserStat(BaseModel):
    user_id: str
    user_name: str
    page_titles: List[str]
    total: int

class TopUsersStat(BaseModel):
    time_start: str
    time_end: str
    top_users: List[UserStat]