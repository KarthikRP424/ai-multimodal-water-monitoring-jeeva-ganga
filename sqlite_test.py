import pathlib, sqlite3, traceback, sys
db_path = pathlib.Path('backend/jeeva_ganga.db').resolve()
print('DB path:', db_path)
try:
    conn = sqlite3.connect(str(db_path))
    conn.execute('SELECT 1')
    print('✅ SQLite connection succeeded')
except Exception as e:
    print('❌ SQLite error:')
    traceback.print_exc()
finally:
    if 'conn' in locals():
        conn.close()
