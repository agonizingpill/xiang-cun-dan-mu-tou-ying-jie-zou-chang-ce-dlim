import json
from sqlalchemy import func, select

from core.db import transaction
from domain.demo import FIXTURES

def seed():
    sizes = {}
    with transaction() as conn:
        for table, rows in FIXTURES:
            key = next(iter(table.primary_key.columns))
            for row in rows:
                present = conn.scalar(select(key).where(key == row[key.name]))
                if present is None:
                    conn.execute(table.insert().values(**row))
            sizes[table.name] = conn.scalar(select(func.count()).select_from(table))
    return sizes

if __name__ == '__main__':
    print(json.dumps(seed(), ensure_ascii=False, sort_keys=True))
