# pytrading

## Prerequisites

Install ta-lib on your machine;

For Linux run:

```sh
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz \
  && sudo tar -xzf ta-lib-0.4.0-src.tar.gz \
  && sudo rm ta-lib-0.4.0-src.tar.gz \
  && cd ta-lib/ \
  && sudo ./configure --prefix=/usr \
  && sudo make \
  && sudo make install \
  && cd ~ \
  && sudo rm -rf ta-lib/
```

## Running the bot

Run bot with:

```sh
poetry run python3 src/bot_rsi_adx.py
```

Run and write output in a file:

```sh
poetry run python3 -u src/bot_rsi_adx.py > bot.log
```

Run bot on VM:

```sh
ssh root@<vm_ip> -- cd /home/pytrading && poetry run src/bot_rsi_adx.py
```

## To do:

- Add Telegram bot when orders are sent, also send a message every N minutes to make sure the bot is alive
- Script to deploy quickly when making new changes
