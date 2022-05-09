import pytest

from rotkehlchen.accounting.structures.balance import Balance
from rotkehlchen.accounting.structures.base import (
    HistoryBaseEntry,
    HistoryEventSubType,
    HistoryEventType,
)
from rotkehlchen.chain.ethereum.modules.aave.constants import CPT_AAVE_V1
from rotkehlchen.constants.assets import A_DAI, A_ETH
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.aave import A_ADAI_V1
from rotkehlchen.tests.utils.ethereum import get_decoded_events_of_transaction
from rotkehlchen.types import Location, deserialize_evm_tx_hash

ADDY = '0x2B888954421b424C5D3D9Ce9bB67c9bD47537d12'


@pytest.mark.parametrize('ethereum_accounts', [[ADDY]])  # noqa: E501
def test_aave_deposit_v1(database, ethereum_manager, function_scope_messages_aggregator):
    """Data taken from
    https://etherscan.io/tx/0x930879d66d13c37edf25cdbb2d2e85b65c3b2a026529ff4085146bb7a5398410
    """
    # TODO: For faster tests hard-code the transaction and the logs here so no remote query needed
    tx_hash = deserialize_evm_tx_hash('0x930879d66d13c37edf25cdbb2d2e85b65c3b2a026529ff4085146bb7a5398410')  # noqa: E501
    events = get_decoded_events_of_transaction(
        ethereum_manager=ethereum_manager,
        database=database,
        msg_aggregator=function_scope_messages_aggregator,
        tx_hash=tx_hash,
    )
    amount = '2507.675873220870275072'
    expected_events = [
        HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=0,
            timestamp=1595376667000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal('0.00825148723006')),
            location_label=ADDY,
            notes=f'Burned 0.00825148723006 ETH in gas from {ADDY}',
            counterparty='gas',
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=93,
            timestamp=1595376667000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.REWARD,
            asset=A_ADAI_V1,
            balance=Balance(amount=FVal('17.91499070977557364')),
            location_label=ADDY,
            notes='Gain 17.91499070977557364 aDAI from aave-v1 as interest',
            counterparty=CPT_AAVE_V1,
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=94,
            timestamp=1595376667000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.DEPOSIT,
            event_subtype=HistoryEventSubType.DEPOSIT_ASSET,
            asset=A_DAI,
            balance=Balance(amount=FVal(amount)),
            location_label=ADDY,
            notes=f'Deposit {amount} DAI to aave-v1 from {ADDY}',
            counterparty=CPT_AAVE_V1,
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=96,
            timestamp=1595376667000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.RECEIVE_WRAPPED,
            asset=A_ADAI_V1,
            balance=Balance(amount=FVal(amount)),
            location_label=ADDY,
            notes=f'Receive {amount} aDAI from aave-v1 for {ADDY}',
            counterparty=CPT_AAVE_V1,
        ),
    ]
    assert expected_events == events


@pytest.mark.parametrize('ethereum_accounts', [[ADDY]])  # noqa: E501
def test_aave_withdraw_v1(database, ethereum_manager, function_scope_messages_aggregator):
    """Data taken from
    https://etherscan.io/tx/0x4fed67963375a3f90916f0cf7cb9e4d12644629e36233025b36060494ffba486
    """
    # TODO: For faster tests hard-code the transaction and the logs here so no remote query needed
    tx_hash = deserialize_evm_tx_hash('0x4fed67963375a3f90916f0cf7cb9e4d12644629e36233025b36060494ffba486')  # noqa: E501
    events = get_decoded_events_of_transaction(
        ethereum_manager=ethereum_manager,
        database=database,
        msg_aggregator=function_scope_messages_aggregator,
        tx_hash=tx_hash,
    )
    amount = '7968.408929477087756071'
    interest = '88.663672238882760399'
    expected_events = [
        HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=0,
            timestamp=1598217272000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.FEE,
            asset=A_ETH,
            balance=Balance(amount=FVal('0.028562839354')),
            location_label=ADDY,
            notes=f'Burned 0.028562839354 ETH in gas from {ADDY}',
            counterparty='gas',
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=98,
            timestamp=1598217272000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.RECEIVE,
            event_subtype=HistoryEventSubType.REWARD,
            asset=A_ADAI_V1,
            balance=Balance(amount=FVal(interest)),
            location_label=ADDY,
            notes=f'Gain {interest} aDAI from aave-v1 as interest',
            counterparty=CPT_AAVE_V1,
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=99,
            timestamp=1598217272000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.SPEND,
            event_subtype=HistoryEventSubType.RETURN_WRAPPED,
            asset=A_ADAI_V1,
            balance=Balance(amount=FVal(amount)),
            location_label=ADDY,
            notes=f'Return {amount} aDAI to aave-v1',
            counterparty=CPT_AAVE_V1,
        ), HistoryBaseEntry(
            event_identifier=tx_hash.hex(),  # pylint: disable=no-member
            sequence_index=102,
            timestamp=1598217272000,
            location=Location.BLOCKCHAIN,
            event_type=HistoryEventType.WITHDRAWAL,
            event_subtype=HistoryEventSubType.REMOVE_ASSET,
            asset=A_DAI,
            balance=Balance(amount=FVal(amount)),
            location_label=ADDY,
            notes=f'Withdraw {amount} DAI from aave-v1',
            counterparty=CPT_AAVE_V1,
        ),
    ]
    assert expected_events == events