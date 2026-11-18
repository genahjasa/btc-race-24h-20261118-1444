"""Dip-bounce bot for make.fun's "Race a BTC trading bot live for 24 hours"
(btc-race-24h-20261118-1444), protocol agent-fun/bars-replay/v1.

Strategy: capitulation-bounce mean reversion, long only, one position at a time.
  - Track a 60-bar EMA of cbBTC closes.
  - Buy the whole cash balance when the close prints at least 1.20% below the
    EMA (a sharp dip: on the dev window such dips bounce ~+0.8-1.3% within
    15 minutes), provided no trade exited in the last 30 bars and at least
    20 bars of the window remain.
  - Sell everything when the position is up 1.00%, down 1.00%, or has been
    held 15 bars -- whichever comes first. No re-entry until the dip
    condition fires again.

Costs of a full-size round trip are ~26 bps (4 bps fee + 2 bps slippage per
side, plus price impact against the pool depth), so the 1.00% target leaves
a wide margin over costs. Pure Python standard library, deterministic: the
only state is the EMA and a few counters, no clock, no randomness, no files,
no network. Two runs on the same bars produce the same orders.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
EMA_BARS = 60
DIP_BPS = 120            # buy when close is this far below the 60-bar EMA
TARGET_BPS = 100         # take profit at +1.00% vs cost
STOP_BPS = 100           # stop out at -1.00% vs cost
HOLD_BARS = 15           # ... or after 15 bars held, whichever comes first
MAX_SLIPPAGE_BPS = 100   # 1% past the decision close; fills are at next open
COOLDOWN_BARS = 30       # bars to wait after an exit before a new entry
WINDOW_BARS = 1440       # 1-minute bars in the window
NO_BUY_AFTER_SEQ = WINDOW_BARS - 20  # need time for the bounce to play out


class Bot:
    def __init__(self):
        self.ema = None
        self.hold_bars = 0
        self.last_exit_seq = -10 ** 9

    def on_batch(self, state, batch):
        # Fold this batch's bars into the EMA (one bar per batch here).
        for bar in batch["bars"]:
            c = int(bar["c"])
            if self.ema is None:
                self.ema = float(c)
            else:
                alpha = 2.0 / (EMA_BARS + 1)
                self.ema = alpha * c + (1.0 - alpha) * self.ema

        # Note fills delivered with this batch: a buy fill starts the hold
        # clock (hold = 1 on the fill bar), a sell fill starts the cooldown.
        bought_this_batch = False
        for fill in batch.get("fills", []):
            if fill.get("status") != "filled":
                continue
            if fill.get("symbol") != SYMBOL:
                continue
            if fill["side"] == "buy":
                self.hold_bars = 1
                bought_this_batch = True
            elif fill["side"] == "sell":
                self.hold_bars = 0
                self.last_exit_seq = state.seq

        # Nothing to decide on the final batch: its orders would be rejected
        # (after_end) and the harness flattens any position anyway.
        if state.seq >= WINDOW_BARS - 1:
            return []

        held = state.positions.get(SYMBOL)
        if held is not None:
            if self.hold_bars > 0 and not bought_this_batch:
                self.hold_bars += 1
            value = state.value(SYMBOL, held.qty)
            cost = held.cost
            pnl_bps = (value - cost) * 10000 // cost if cost else 0
            if pnl_bps >= TARGET_BPS or pnl_bps <= -STOP_BPS or self.hold_bars >= HOLD_BARS:
                return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
            return []

        # Flat: look for a deep dip to buy.
        if state.seq > NO_BUY_AFTER_SEQ:
            return []
        if state.seq - self.last_exit_seq < COOLDOWN_BARS:
            return []
        close = state.close(SYMBOL)
        if close is None or self.ema is None:
            return []
        if close * 10000 < self.ema * (10000 - DIP_BPS):
            amount = state.cash
            room = state.weight_room(SYMBOL)
            if room < amount:
                amount = room
            if amount >= int(state.hello["fees"]["min_notional_quote_units"]):
                return [{"side": "buy", "symbol": SYMBOL,
                         "notional_quote_units": amount,
                         "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []


makefun_bars.run(Bot().on_batch)
