from sqlalchemy import create_engine, text


DATABASE_URL = "postgresql://hardwood_db_user:6SwoA3SSO1whjFA91GFokx5qcQDjbLRM@dpg-d1jhds6mcj7s739rkf8g-a.virginia-postgres.render.com/hardwood_db"

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT NOW();"))
        for row in result:
            print("Connected successfully! Current time:", row[0])
except Exception as e:
    print("Connection failed:", e)