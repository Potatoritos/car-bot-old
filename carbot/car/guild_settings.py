__all__ = [
    'SettingsMananger',
    'GuildSettings'
]

VALUES = (
    'prefix',
    'msg_join',
    'msg_leave',
    'role_banned',
    'role_muted',
    'role_unverified'
)

class GuildSettings(object):
    def __init__(self, conn, guild_id):
        object.__setattr__(self, '_cache', {})
        object.__setattr__(self, '_conn', conn)
        object.__setattr__(self, 'id', conn)

        cur = self._conn.cursor()
        cur.execute('INSERT OR IGNORE INTO guilds values(?, "c.", "", "", -1, -1, -1)', (guild_id,))
        self._conn.commit()

        cur.execute('SELECT * FROM guilds WHERE id=?', (guild_id,))
        fetch = cur.fetchone()

        for i in range(1, len(fetch)):
            self._cache[VALUES[i-1]] = fetch[i]

    def __getattr__(self, key):
        if key in self._cache:
            return self._cache[key]

        raise AttributeError

    def __setattr__(self, key, value):
        if key in self._cache:
            cur = self._conn.cursor()
            cur.execute(f'UPDATE guilds SET {key}=? WHERE id=?', (value, self.id))
            self._conn.commit()

            self._cache[key] = value

        else:
            raise AttributeError

class GuildSettingsList(object):
    def __init__(self, conn):
        self._guilds = {}
        self._conn = conn

        cur = self._conn.cursor()
        cur.execute("""
                    CREATE TABLE IF NOT EXISTS guilds(
                    id INTEGER PRIMARY KEY,
                    prefix TEXT,
                    msg_join TEXT,
                    msg_leave TEXT,
                    role_banned INTEGER,
                    role_muted INTEGER,
                    role_unverified INTEGER)
                    """)

    def __getitem__(self, guild_id):
        if guild_id in self._guilds:
            return self._guilds[guild_id]

        self._guilds[guild_id] = GuildSettings(self._conn, guild_id)

        return self._guilds[guild_id]
