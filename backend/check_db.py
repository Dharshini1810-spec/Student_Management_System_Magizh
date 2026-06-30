import sqlite3
conn = sqlite3.connect('local_fallback.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print('notifications table exists:', 'notifications' in tables)
for t in tables:
    print(f'  {t}')
conn.close()
