__all__ = [
    'GuildSettings',
    'GuildSettingsList',
    'GUILD_SETTINGS'
]

GUILD_SETTINGS = (
    'prefix',
    'msg_join',
    'msg_leave',
    'channel_joinleave',
    'role_banned',
    'role_muted',
    'role_unverified'
)

DEFAULT_SETTINGS = {
    'prefix': "c.",
    'msg_join': "",
    'msg_leave': "",
    'channel_joinleave': -1,
    'role_banned': -1,
    'role_muted': -1,
    'role_unverified': -1
}

# TODO: generalize to Settings

class GuildSettings(object):
    def __init__(self, conn, guild_id):
        object.__setattr__(self, '_cache', {})
        object.__setattr__(self, '_conn', conn)
        object.__setattr__(self, 'id', guild_id)

        cur = self._conn.cursor()
        cur.execute(
            'INSERT OR IGNORE INTO guilds values(?, '
            + ', '.join([str(v), f'"{v}"'][isinstance(v, str)]
                        for _, v in DEFAULT_SETTINGS.items())
            + ')', (guild_id,)
        )
        self._conn.commit()

        cur.execute('SELECT * FROM guilds WHERE id=?', (guild_id,))
        fetch = cur.fetchone()

        for i in range(1, len(fetch)):
            self._cache[GUILD_SETTINGS[i-1]] = fetch[i]

    def __getattr__(self, key):
        if key in self._cache:
            return self._cache[key]

        raise AttributeError

    def __setattr__(self, key, value):
        if key not in self._cache:
            raise AttributeError

        if value is None:
            value = DEFAULT_SETTINGS[key]

        cur = self._conn.cursor()
        cur.execute(f'UPDATE guilds SET {key}=? WHERE id=?', (value, self.id))
        self._conn.commit()

        self._cache[key] = value

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        self.__setattr__(key, value)

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
                    channel_joinleave INTEGER,
                    role_banned INTEGER,
                    role_muted INTEGER,
                    role_unverified INTEGER)
                    """)

    def __getitem__(self, guild_id):
        if guild_id in self._guilds:
            return self._guilds[guild_id]

        self._guilds[guild_id] = GuildSettings(self._conn, guild_id)

        return self._guilds[guild_id]

