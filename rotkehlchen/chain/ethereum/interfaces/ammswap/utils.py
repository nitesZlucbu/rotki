import logging
from typing import TYPE_CHECKING, Any, Dict, NamedTuple, Set, Tuple

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.assets.asset import EthereumToken
from rotkehlchen.assets.utils import get_or_create_ethereum_token
from rotkehlchen.chain.ethereum.utils import token_normalized_value_decimals
from rotkehlchen.fval import FVal
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.types import ChecksumEthAddress

from .types import LiquidityPool, LiquidityPoolAsset, NFTLiquidityPool

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler


logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


SUBGRAPH_REMOTE_ERROR_MSG = (
    "Failed to request the {location} subgraph due to {error_msg}. "
    "All {location} balances and historical queries are not functioning until this is fixed. "  # noqa: E501
    "Probably will get fixed with time. If not report it to rotki's support channel"  # noqa: E501
)


class TokenDetails(NamedTuple):
    address: ChecksumEthAddress
    name: str
    symbol: str
    decimals: int
    amount: FVal


def _decode_token(entry: Tuple) -> TokenDetails:
    decimals = entry[0][3]
    return TokenDetails(
        address=entry[0][0],
        name=entry[0][1],
        symbol=entry[0][2],
        decimals=decimals,
        amount=token_normalized_value_decimals(entry[1], decimals),
    )


def _decode_v3_token(entry: Dict[str, Any]) -> TokenDetails:
    return TokenDetails(
        address=entry['address'],
        name=entry['name'],
        symbol=entry['symbol'],
        decimals=entry['decimals'],
        amount=FVal(entry['amount']),
    )


def _decode_result(
        userdb: 'DBHandler',
        data: Tuple,
        known_assets: Set[EthereumToken],
        unknown_assets: Set[EthereumToken],
) -> LiquidityPool:
    pool_token = _decode_token(data[0])
    token0 = _decode_token(data[1][0])
    token1 = _decode_token(data[1][1])

    assets = []
    for token in (token0, token1):
        asset = get_or_create_ethereum_token(
            userdb=userdb,
            symbol=token.symbol,
            ethereum_address=token.address,
            name=token.name,
            decimals=token.decimals,
        )
        # Classify the asset either as price known or unknown
        if asset.has_oracle():
            known_assets.add(asset)
        else:
            unknown_assets.add(asset)
        assets.append(LiquidityPoolAsset(
            asset=asset,
            total_amount=None,
            user_balance=Balance(amount=token.amount),
        ))

    pool = LiquidityPool(
        address=pool_token.address,
        assets=assets,
        total_supply=None,
        user_balance=Balance(amount=pool_token.amount),
    )
    return pool


def _decode_v3_result(
        userdb: 'DBHandler',
        data: Tuple,
        known_assets: Set[EthereumToken],
        unknown_assets: Set[EthereumToken],
) -> NFTLiquidityPool:
    nft_id = data[0]
    pool_token = data[1]
    token0 = _decode_v3_token(data[4])
    token1 = _decode_v3_token(data[5])
    total_amounts_of_tokens = {
        token0.address: data[4]['total_amount'],
        token1.address: data[5]['total_amount'],
    }

    assets = []
    for token in (token0, token1):
        asset = get_or_create_ethereum_token(
            userdb=userdb,
            symbol=token.symbol,
            ethereum_address=token.address,
            name=token.name,
            decimals=token.decimals,
        )
        # Classify the asset either as price known or unknown
        if asset.has_oracle():
            known_assets.add(asset)
        else:
            unknown_assets.add(asset)
        assets.append(LiquidityPoolAsset(
            asset=asset,
            total_amount=total_amounts_of_tokens[token.address],
            user_balance=Balance(amount=token.amount),
        ))

    pool = NFTLiquidityPool(
        address=pool_token,
        price_range=(FVal(data[3][0]), FVal(data[3][1])),
        nft_id=nft_id,
        assets=assets,
        total_supply=None,
        user_balance=Balance(amount=FVal(0)),
    )
    return pool
