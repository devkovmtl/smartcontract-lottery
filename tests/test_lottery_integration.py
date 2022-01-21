import pytest
import time
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import Lottery, accounts, config, network, exceptions
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    fund_with_link,
    get_contract,
)

# we are going to use rinkeby
def test_can_pick_winner():
    # Skip if we are on dev chain skip
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    account = get_account()
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee() + 10000})
    # lottery.enter({"from": account, "value": lottery.getEntranceFee() + 1000})
    fund_with_link(lottery)
    lottery.endLottery({"from": account})
    # we have to wait for the chainlink node to response
    time.sleep(90)
    assert lottery.recentWinner() == account
    assert lottery.balance() == 0
