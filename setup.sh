python3 -m pip install -r requirements.txt
touch prefixes.db
python3 db_setup.py

echo "python packages installed and database setup done"

sudo cp rw_wiki_bot.service /etc/systemd/system/
echo "service file copied"
sudo systemctl daemon-reload
echo "systemctl daemon reloaded"
sudo systemctl enable rw_wiki_bot
echo "systemctl service enabled"
sudo systemctl start rw_wiki_bot
echo "systemctl setup done"

echo "reminder: I need a _keys.json file with a version string and Discord token"
