import time
import requests

from app.models.prices import Price
from app.crud.token_sync import get_token_from_db, get_token_from_db_for_id
from app.crud.prices_sync import create_price as create_price_crud
from app.services.price_sources_sync import (
    get_dex_price,
    get_cex_price,
    create_http_session,
)
from app.dependencies_sync import get_db
from app.core.logger import logger


class TokenNotFound(Exception):
    pass


class PriceSourceError(Exception):
    pass


def create_price_service(value: str) -> Price:
    with get_db() as db:
        token = get_token_from_db(db, value)
        if not token:
            raise TokenNotFound(f"Token not found: {value}")

        http_session = create_http_session()

        try:
            price_dex = get_dex_price(http_session, token.address)
            price_cex = get_cex_price(http_session, token.cex_symbol)

            if price_dex is None or price_cex is None:
                missing = []
                if price_dex is None:
                    missing.append("DEX")
                if price_cex is None:
                    missing.append("CEX")
                raise PriceSourceError(
                    f"Could not fetch {', '.join(missing)} "
                    f"price(s) for token {value}"
                )

            price_dex = float(price_dex)
            price_cex = float(price_cex)

            spread = abs(price_dex - price_cex) / price_cex * 100

            orm_price = Price(
                token_id=token.id,
                price_dex=price_dex,
                price_cex=price_cex,
                spread=spread,
            )

            result = create_price_crud(db, orm_price)

            logger.info(
                f"Price created for token {value}: "
                f"DEX=${price_dex:.6f}, CEX=${price_cex:.6f}, "
                f"spread={spread:.2f}%"
            )

            return result

        finally:
            http_session.close()


def create_price_service_for_celery(
    http_session: requests.Session,
    token_id: int,
    rate_limit_delay: float = 0.0,
) -> Price:
    with get_db() as db:
        token = get_token_from_db_for_id(db, token_id)
        if not token:
            raise TokenNotFound(f"Token with id {token_id} not found")

        price_dex = get_dex_price(http_session, token.address)
        price_cex = get_cex_price(http_session, token.cex_symbol)

        if rate_limit_delay > 0:
            time.sleep(rate_limit_delay)

        if price_dex is None or price_cex is None:
            missing = []
            if price_dex is None:
                missing.append(f"DEX (address: {token.address})")
            if price_cex is None:
                missing.append(f"CEX (symbol: {token.cex_symbol})")
            raise PriceSourceError(
                f"Could not fetch {', '.join(missing)} "
                f"price(s) for token_id={token_id}"
            )

        price_dex = float(price_dex)
        price_cex = float(price_cex)

        spread = abs(price_dex - price_cex) / price_cex * 100

        orm_price = Price(
            token_id=token.id,
            price_dex=price_dex,
            price_cex=price_cex,
            spread=spread,
        )

        result = create_price_crud(db, orm_price)

        logger.debug(
            f"Price created for token_id={token_id}: "
            f"DEX=${price_dex:.6f}, CEX=${price_cex:.6f}, "
            f"spread={spread:.2f}%"
        )

        return result


def batch_create_prices_for_tokens(
    token_ids: list[int],
    max_workers: int = 5,
    rate_limit_delay: float = 1.0,
) -> dict:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    stats = {"success": 0, "failed": 0, "total": len(token_ids)}

    http_session = create_http_session()

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_token = {
                executor.submit(
                    create_price_service_for_celery,
                    http_session,
                    token_id,
                    rate_limit_delay,
                ): token_id
                for token_id in token_ids
            }

            for future in as_completed(future_to_token):
                token_id = future_to_token[future]
                try:
                    future.result()
                    stats["success"] += 1
                except Exception as e:
                    stats["failed"] += 1
                    logger.error(
                        f"Failed to create price for token_id={token_id}: {e}"
                    )

        return stats

    finally:
        http_session.close()
