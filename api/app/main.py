from fastapi import FastAPI, Query
from app.cassandra_client import get_session
from typing import List
from app.models import (
    DomainList, PageList, PageCount, SinglePage, UserStatResponse, HourlyDomainStat, BotStats, TopUsersStat, UserStat, BotStatItem
)
from datetime import datetime, timedelta

app = FastAPI()
session = get_session()

@app.get("/domains/", response_model=DomainList)
def list_domains():
    query = "SELECT DISTINCT domain FROM pages_by_domain;"
    rows = session.execute(query)
    return {"domains": [row["domain"] for row in rows]}

@app.get("/pages/user/{user_id}", response_model=PageList)
def get_pages_by_user(user_id: str):
    query = "SELECT * FROM pages_by_user WHERE user_id = %s LIMIT 100;"
    rows = session.execute(query, (user_id,))
    return {"pages": list(rows)}

@app.get("/pages/domain/{domain}", response_model=PageCount)
def count_pages_by_domain(domain: str):
    query = "SELECT COUNT(*) FROM pages_by_domain WHERE domain = %s;"
    row = session.execute(query, (domain,)).one()
    return {"domain": domain, "count": row["count"]}

@app.get("/pages/id/{page_id}", response_model=SinglePage)
def get_page_by_id(page_id: str):
    query = "SELECT * FROM pages_by_id WHERE page_id = %s;"
    row = session.execute(query, (page_id,)).one()
    return {"page": row}

@app.get("/stats/time-range/", response_model=UserStatResponse)
def stats_time_range(
    from_hour: str = Query(..., example="2024-12-01-10"),
    to_hour: str = Query(..., example="2024-12-01-14")
):
    from_dt = datetime.strptime(from_hour, "%Y-%m-%d-%H")
    to_dt = datetime.strptime(to_hour, "%Y-%m-%d-%H")

    hours = []
    current = from_dt
    while current <= to_dt:
        hours.append(current.strftime("%Y-%m-%d-%H"))
        current += timedelta(hours=1)

    placeholders = ", ".join(["%s"] * len(hours))
    query = f"SELECT date_hour, user_id, user_name FROM pages_by_time WHERE date_hour IN ({placeholders});"
    rows = session.execute(query, tuple(hours))

    users = {}
    for row in rows:
        uid = row["user_id"]
        uname = row["user_name"]
        if uid in users:
            users[uid]["count"] += 1
        else:
            users[uid] = {"user_id": uid, "user_name": uname, "count": 1}

    return {"from_": from_hour, "to": to_hour, "users": list(users.values())}

@app.get("/reports/domains-by-hour", response_model=List[HourlyDomainStat])
def get_domains_by_hour():
    query = "SELECT * FROM precomputed_domains_by_hour;"
    rows = session.execute(query)
    buckets = {}
    for row in rows:
        key = (row.time_start, row.time_end)
        if key not in buckets:
            buckets[key] = {}
        buckets[key][row.domain] = buckets[key].get(row.domain, 0) + row.count

    response = []
    for (start, end), domain_counts in sorted(buckets.items()):
        statistics = [{domain: count} for domain, count in domain_counts.items()]
        response.append({"time_start": start, "time_end": end, "statistics": statistics})
    return response

@app.get("/reports/bots", response_model=BotStats)
def get_bots_report():
    query = "SELECT * FROM precomputed_bots_stats;"
    rows = session.execute(query)
    result = {}
    for row in rows:
        if "time_start" not in result:
            result["time_start"] = row.time_start
            result["time_end"] = row.time_end
            result["statistics"] = []
        result["statistics"].append({"domain": row.domain, "created_by_bots": row.created_by_bots})
    return result

@app.get("/reports/top-users", response_model=TopUsersStat)
def get_top_users():
    query = "SELECT * FROM precomputed_top_users;"
    rows = session.execute(query)
    users = []
    time_start = None
    time_end = None
    for row in rows:
        users.append({
            "user_id": row.user_id,
            "user_name": row.user_name,
            "page_titles": row.page_titles,
            "total": row.total
        })
        time_start = row.time_start
        time_end = row.time_end
    return {"time_start": time_start, "time_end": time_end, "top_users": users}