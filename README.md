# pytrading

## Prerequisites

It's better to use a bigger VM for the setup (4vCPUs)

1. Load code to VM by running `./update-vm.sh`
2. Setup the VM with `ssh root@165.232.86.215 -- pytrading/setup-vm.sh`
3. Configure Telegram bot `poetry install telegram-send && telegram-send --configure`

## Run the bot on VM

1. `screen`
2. `cd pytrading && poetry run python3 -u src/bot_rsi_adx.py > bot.log &`
3. Disconnect from screen with `CTRL + A + D`.
4. Reconnect to the screen session with the command `screen -r`
