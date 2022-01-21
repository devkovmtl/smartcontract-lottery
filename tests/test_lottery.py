from brownie import Lottery, accounts, config, network
from web3 import Web3

# expect 0,0178141979157388 $50 USD / #ETH PRICE
# in wey 170000000000000000 (18 dec)
# to text our entrance fee, first deploy
def test_get_entrance_fee():
    # to deploy get account (address)
    account = accounts[0]
    # Lottery have a param constructor
    lottery = Lottery.deploy(
        config["networks"][network.show_active()]["eth_usd_price_feed"],
        {"from": account},
    )
    # test not great way but we can see if we are int the
    # right direction
    assert lottery.getEntranceFee() > Web3.toWei(0.016, "ether")
    assert lottery.getEntranceFee() < Web3.toWei(0.019, "ether")
