__all__ = [
    'SettingsMananger',
    'GuildSettings'
]

class SettingsManager(object):
    def __init__(self, conn):
        self._guilds = {}
        self._conn = conn

        cur = self._conn
        cur.execute(
            'CREATE TABLE IF NOT EXISTS guilds (',
            'id INTEGER PRIMARY KEY, ',
            'prefix TEXT',
            ''
        )

    def __getitem__(self, guild_id):
        if guild_id in guilds:
            return self._guilds[guild_id]

        self._guilds[guild_id] = GuildSettings(self._conn, guild_id)

        return self._guilds[guild_id]

class GuildSettings(object):
    def __init__(self, conn, guild_id):
        self.id = guild_id
        self._conn = conn
        self._cache = {
             'prefix': 'c.'
        }

        cur = self._conn.cursor()
        cur.execute(f'CREATE TABLE IF NOT EXISTS {self.id}')

    def set(self, **settings):
        
