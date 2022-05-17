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

## Clean VM and send project

```sh
ssh root@<vm_ip> -- rm -rf pytrading
```

```sh
scp -r pytrading root@<vm_ip>:
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
ssh root@<vm_ip> -- cd /home/pytrading && poetry run python3 -u src/bot_rsi_adx.py > bot.log &
```

## Setup Telegram bot

```sh
poetry install telegram-send && telegram-send --configure
```
