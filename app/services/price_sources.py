import aiohttp

DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"
CEX_MEXC_TOKEN_URL = 'https://contract.mexc.com/api/v1/contract/index_price/{}_USDT'

W_LIQUIDITY = 0.7
W_VOLUME = 0.3


async def get_dex_price(
    session,
    token_address: str,
    preferred_quote=("USDC", "USDT"),
    min_liquidity=10_000,
    min_volume=5_000
):
    url = DEXSCREENER_TOKEN_URL.format(token_address)

    async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
        if resp.status != 200:
            raise RuntimeError(f"Dexscreener error {resp.status}")
        data = await resp.json()

    pairs = data.get("pairs", [])
    if not pairs:
        return None

    best_pair = None
    best_score = 0

    for pair in pairs:
        liquidity = float(pair.get("liquidity", {}).get("usd") or 0)
        volume = float(pair.get("volume", {}).get("h24") or 0)

        if liquidity < min_liquidity or volume < min_volume:
            continue

        quote_symbol = pair.get("quoteToken", {}).get("symbol", "")

        score = liquidity * W_LIQUIDITY + volume * W_VOLUME

        if quote_symbol in preferred_quote:
            score *= 1.2

        if score > best_score:
            best_score = score
            best_pair = {
                "chainId": pair["chainId"],
                "dexId": pair["dexId"],
                "pairAddress": pair["pairAddress"],
                "base": pair["baseToken"]["symbol"],
                "quote": quote_symbol,
                "liquidity_usd": liquidity,
                "volume_24h": volume,
                "price_usd": pair.get("priceUsd"),
                "score": round(score, 2)
            }
    if best_pair is not None:
        return best_pair.get("price_usd")


async def get_cex_price(session, token):
    url = CEX_MEXC_TOKEN_URL.format(token)
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
        if not (200 <= resp.status < 301):
            raise RuntimeError(f"MEXC error {resp.status}")
        data = await resp.json()
    return data["data"]["indexPrice"]
