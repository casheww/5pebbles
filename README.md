# 5pebbles
A Discord bot written with discord.py that interacts with the Rain World Gamepedia. Unofficial, ofc.

If you'd like to add this bot to your server, you can use [this link](https://discord.com/api/oauth2/authorize?client_id=739950956313051219&permissions=67488832&scope=bot). This could probably be recycled for use with other Gamepedia based sites.

The default command prefix is `rain ` (note the space), but this can be changed: ```rain set_prefix `new `​```.
Note that if you want the bot to listen for "prefix command" with a space, you must include a space inside the backticks.

### Notable commands
`search/s [limit] <query>` - searches the RW Gamepedia for results matching the query and returns them. Result limit is optional.

`page/p <query>` - tries to find a page with a title matching the query, and returns the summary and thumbnail (if available). The title of the returned embed also contains a hyperlink to the wiki page.

`creature/c <query>` - tries to find a Creature page with a title matching the query and and returns what creature stats and spawn info it can find. Similar to the `page` command. 

`region/r [-t] <query>` - sends a map of the Region. Similar to the `creature` and `page` commands. The `-t` flag toggles whether the region's threats are displayed.

`rwtext <text>` - generates an image of the input text made up of the text used for Rain World's region names. In the Rain World discord, this command is restricted to staff, so invite to your own server for use if you do not fall into this category. 
