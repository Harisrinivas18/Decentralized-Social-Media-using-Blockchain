const BlockchainOSN = artifacts.require("BlockchainOSN");

module.exports = function(deployer) {
  deployer.deploy(BlockchainOSN);
};
