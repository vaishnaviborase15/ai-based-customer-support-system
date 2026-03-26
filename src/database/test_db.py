from sqlalchemy import create_engine

DATABASE_URL = "postgresql://support_system_zqqv_user:4TZQBDlkV9azUaKBppicWnyRyKimLVOO@dpg-d72ihi99fqoc73aa2nbg-a.singapore-postgres.render.com/support_system_zqqv"

engine = create_engine(DATABASE_URL)

try:
    conn = engine.connect()
    print("✅ Database Connected Successfully!")
    conn.close()
except Exception as e:
    print("❌ Connection Failed:", e)