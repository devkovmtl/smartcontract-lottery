// SPDX-License-Identifier: MIT

pragma solidity ^0.8.0;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    // keep track of all the players who have payed
    address payable[] public players;
    // minimum of entry fee
    uint256 public usdEntryFee;
    // Store our price feed
    AggregatorV3Interface internal ethUsdPriceFeed;

    // to pass the address to Aggregator to find
    // eth/usd
    constructor(address _priceFeedAddress) {
        // unit in wey
        // need a price feed to transform
        // https://docs.chain.link/docs/get-the-latest-price/
        usdEntryFee = 50 * (10 ** 18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
    }
 
    // we need user to pay so make the function 
    // payable
    function enter() public payable {
        // Check a minimum of $50
        // require();
        // each time somebody pay keep track
        players.push(payable(msg.sender));
    }

    // we return just a number view 
    // need a price feed to transform 50USD to ETH
    // https://docs.chain.link/docs/get-the-latest-price/
    function getEntranceFee() public view returns (uint256) {
        
    }

    function startLottery() public {}

    function endLottery() public {}

}