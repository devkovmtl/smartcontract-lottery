from brownie import Lottery, accounts, config, network, exceptions
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)
import pytest

# expect 0,0178141979157388 $50 USD / #ETH PRICE
# in wey 170000000000000000 (18 dec)
# to text our entrance fee, first deploy
# def test_get_entrance_fee():
#     # to deploy get account (address)
#     account = accounts[0]
#     # Lottery have a param constructor
#     lottery = Lottery.deploy(
#         config["networks"][network.show_active()]["eth_usd_price_feed"],
#         {"from": account},
#     )
# test not great way but we can see if we are int the
# right direction
# assert lottery.getEntranceFee() > Web3.toWei(0.016, "ether")
# assert lottery.getEntranceFee() < Web3.toWei(0.019, "ether")


def test_get_entrance_fee():
    # only run in local dev
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    # arrange
    lottery = deploy_lottery()  # give us lottery contract
    # act
    # if price 2000 eth/usd
    # usdEntryfee is 50
    # 2000/1 == 50/x == 0.025
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    # assert
    assert expected_entrance_fee == entrance_fee


def test_cant_enter_unless_started():
    # only run in local dev
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # only run in local dev
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    # Act
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    # check we push players correctly
    assert lottery.players(0) == account


def test_can_end_lottery():
    # only run in local dev
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    assert lottery.lottery_state() == 2  # 2: CALCULATING_WINNER


def test_can_pick_winner():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=1), "value": lottery.getEntranceFee()})
    lottery.enter({"from": get_account(index=2), "value": lottery.getEntranceFee()})
    fund_with_link(lottery)
    # emit event in transaction
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RequestedRandomness"]["requestId"]
    # in our mock
    STATIC_RNG = 777
    # dummying getting a response from chainlink node with random num
    # mock response
    get_contract("vrf_coordinator").callBackWithRandomness(
        request_id, STATIC_RNG, lottery.address, {"from": account}
    )
    starting_balance_of_account = account.balance()
    balance_of_lottery = lottery.balance()
    # who is the winner
    # 777 % 3: 3 num player = 0
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
    assert account.balance() == starting_balance_of_account + balance_of_lottery
