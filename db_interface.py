import json

# - - - - - -
#   JSON stuffed into an SQL database... the perfect bodge
# - - - - - -


async def get_guild_data(db, guild_id: int):
    """ returns dict with guild data """

    async with db.cursor() as c:
        await c.execute('SELECT * FROM guilds WHERE guild=?', [guild_id])
        guild_data = await c.fetchall()

        try:
            return json.loads(guild_data[0][1])
        except IndexError:
            return []


async def get_all_guilds(db):

    async with db.cursor() as c:

        await c.execute('SELECT * FROM guilds')
        data = await c.fetchall()

        return data


async def dump_guild_data(db, guild_id: int, info):

    data = await get_guild_data(db, guild_id)

    info = json.dumps(info)

    async with db.cursor() as c:

        if data:
            await c.execute('UPDATE guilds SET data=? WHERE guild=?;',
                            [info, guild_id])

        else:
            await c.execute('INSERT INTO guilds VALUES (?, ?);', [guild_id, info])
    await db.commit()


async def delete_guild(db, guild_id: int):
    async with db.cursor() as c:
        await c.execute('DELETE FROM guilds WHERE guild=?;', [guild_id])
    await db.commit()
