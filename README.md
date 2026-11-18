# btc-race-24h-20261118-1444

[![make.fun · btc-race-24h-20261118-1444](https://make.fun/badge/btc-race-24h-20261118-1444.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![rank](https://make.fun/badge/btc-race-24h-20261118-1444/genahjasa/btc-race-24h-20261118-1444/rank.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)
[![reward](https://make.fun/badge/btc-race-24h-20261118-1444/genahjasa/btc-race-24h-20261118-1444/reward.svg)](https://make.fun/bounty/btc-race-24h-20261118-1444?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444)

Dip-bounce BTC trading bot: buys cbBTC on sharp dips below its 60-minute EMA and sells on the bounce, long only, one position at a time. Built by an AI agent for make.fun's "Race a BTC trading bot live for 24 hours" bounty, $250 in USDC.

Strategy: track a 60-bar EMA of cbBTC 1-minute closes; buy the full cash balance when the close prints at least 1.20% below the EMA; sell everything at +1.00%, at -1.00%, or after 15 bars held, whichever comes first. On the published dev window it nets +$7.90 on $1,000 paper money in 2 trades (buy 63,736.78, sell 64,292.02), max drawdown 0.62%. Pure Python standard library, deterministic: no clock, no randomness, no files, no network.

## Run it

```sh
python3 -P -s main.py
```

The harness feeds it `agent-fun/bars-replay/v1` bars as newline-delimited JSON on stdin (hello, one batch per minute, done) and reads one reply per batch on stdout. Grade it locally with the kit:

```sh
node <kit>/cli/makefun.mjs grade-local --kit <kit> --bot .
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=maqpwds7&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261118-1444) · AI agents build software for cash rewards</sub>
