# 5pebbles
A Discord bot written with discord.py that interacts with the Rain World Gamepedia. Unofficial, ofc.

If you'd like this bot to your server, you can use [this link](https://discord.com/api/oauth2/authorize?client_id=739950956313051219&permissions=67488832&scope=bot).

The default command prefix is `rain `, but this can be changed: `rain set_prefix <new>`.

### Notable commands
`search [limit] <query>` - searches the RW Gamepedia for results matching the query and returns them. Result limit is optional.

`page <query>` - tries to find a page with a title matching the query, and returns the summary and thumbnail (if available). The title of the returned embed also contains a hyperlink to the wiki page.
