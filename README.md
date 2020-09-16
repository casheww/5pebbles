# 5pebbles
A Discord bot written with discord.py that interacts with the Rain World Gamepedia. Unofficial, ofc.

If you'd like to add this bot to your server, you can use [this link](https://discord.com/api/oauth2/authorize?client_id=739950956313051219&permissions=67488832&scope=bot). This could probably be recycled for use with other Gamepedia based sites.

The default command prefix is `rain `, but this can be changed: `rain set_prefix <new>`.

### Notable commands
`search/s [limit] <query>` - searches the RW Gamepedia for results matching the query and returns them. Result limit is optional.

`page/p <query>` - tries to find a page with a title matching the query, and returns the summary and thumbnail (if available). The title of the returned embed also contains a hyperlink to the wiki page.

`creature/c <query>` - tries to find a Creature page with a title matching the query and and returns what creature stats and spawn info it can find. Similar to the `page` command. 

`region/r <query>` - sends the list of creatures from and a map of the Region, if found. Similar to the `creature` and `page` commands.

### TODO
- Command for fetching the source URLs for all of a page's images?
- Add discord.py flags ext for toggleable creature section of `region` cmd, etc.
- More obvious wiki page hyperlinks
- Fix `region` threat lists breaking when a list covers more than one difficulty
