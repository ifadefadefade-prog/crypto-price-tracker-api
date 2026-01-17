import requests
from typing import Optional, Dict, Tuple
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.core.logger import logger

DEXSCREENER_TOKEN_URL = "https://api.dexscreener.com/latest/dex/tokens/{}"
CEX_MEXC_TOKEN_URL = (
    "https://contract.mexc.com/api/v1/contract/index_price/{}_USDT"
)

W_LIQUIDITY = 0.7
W_VOLUME = 0.3

DEX_TIMEOUT = 10
CEX_TIMEOUT = 5


def create_http_session() -> requests.Session:
    session = requests.Session()

    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=10,
        pool_block=False,
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    session.headers.update(
        {
            "User-Agent": "CryptoPriceTracker/1.0",
            "Accept": "application/json",
        }
    )

    return session


def get_dex_price(
    session: requests.Session,
    token_address: str,
    preferred_quote: Tuple[str, ...] = ("USDC", "USDT"),
    min_liquidity: float = 10000,
    min_volume: float = 5000,
    timeout: int = DEX_TIMEOUT,
) -> Optional[float]:
    url = DEXSCREENER_TOKEN_URL.format(token_address)

    try:
        logger.debug(f"Fetching DEX price for {token_address}")

        response = session.get(url, timeout=timeout)

        if response.status_code != 200:
            logger.error(
                f"DexScreener error: status={response.status_code}, "
                f"token={token_address}"
            )
            return None

        data = response.json()
        pairs = data.get("pairs", [])

        if not pairs:
            logger.warning(f"No pairs found for token {token_address}")
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
                    "chainId": pair.get("chainId"),
                    "dexId": pair.get("dexId"),
                    "pairAddress": pair.get("pairAddress"),
                    "base": pair.get("baseToken", {}).get("symbol"),
                    "quote": quote_symbol,
                    "liquidity_usd": liquidity,
                    "volume_24h": volume,
                    "price_usd": pair.get("priceUsd"),
                    "score": round(score, 2),
                }

        if best_pair is not None:
            price = best_pair.get("price_usd")
            logger.debug(
                f"DEX price found for {token_address}: ${price} "
                f"(pair: {best_pair.get('base')}/{best_pair.get('quote')}, "
                f"liquidity: ${best_pair.get('liquidity_usd'):,.0f})"
            )
            return float(price) if price else None

        logger.warning(
            f"No suitable pairs found for {token_address} "
            f"(min_liquidity=${min_liquidity:,.0f}, "
            f"min_volume=${min_volume:,.0f})"
        )
        return None

    except requests.Timeout:
        logger.error(f"DEX price request timeout for {token_address}")
        return None
    except requests.RequestException as e:
        logger.error(f"DEX price request failed for {token_address}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"DEX price parsing error for {token_address}: {e}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error getting DEX price for {token_address}: {e}",
            exc_info=True,
        )
        return None


def get_cex_price(
    session: requests.Session,
    token_symbol: str,
    timeout: int = CEX_TIMEOUT,
) -> Optional[float]:
    url = CEX_MEXC_TOKEN_URL.format(token_symbol)

    try:
        logger.debug(f"Fetching CEX price for {token_symbol}")

        response = session.get(url, timeout=timeout)

        if not (200 <= response.status_code < 300):
            logger.error(
                f"MEXC error: status={response.status_code}, "
                f"token={token_symbol}"
            )
            return None

        data = response.json()
        price = data.get("data", {}).get("indexPrice")

        if price is not None:
            logger.debug(f"CEX price found for {token_symbol}: ${price}")
            return float(price)

        logger.warning(f"No price data in MEXC response for {token_symbol}")
        return None

    except requests.Timeout:
        logger.error(f"CEX price request timeout for {token_symbol}")
        return None
    except requests.RequestException as e:
        logger.error(f"CEX price request failed for {token_symbol}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logger.error(f"CEX price parsing error for {token_symbol}: {e}")
        return None
    except Exception as e:
        logger.error(
            f"Unexpected error getting CEX price for {token_symbol}: {e}",
            exc_info=True,
        )
        return None


def check_price_apis_health(
    session: Optional[requests.Session] = None,
) -> Dict[str, str]:
    if session is None:
        session = create_http_session()

    health = {
        "dex_api": "unknown",
        "cex_api": "unknown",
    }

    try:
        test_address = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        response = session.get(
            DEXSCREENER_TOKEN_URL.format(test_address),
            timeout=5,
        )
        health["dex_api"] = (
            "healthy" if response.status_code == 200 else "unhealthy"
        )
    except Exception:
        health["dex_api"] = "unreachable"

    try:
        response = session.get(
            CEX_MEXC_TOKEN_URL.format("BTC"),
            timeout=5,
        )
        health["cex_api"] = (
            "healthy" if response.status_code == 200 else "unhealthy"
        )
    except Exception:
        health["cex_api"] = "unreachable"

    logger.info(f"Price APIs health check: {health}")
    return health
