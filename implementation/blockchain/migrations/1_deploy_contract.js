var sendPairingElement = artifacts.require("sendPairingElement");

module.exports = function(deployer) {
    deployer.deploy(sendPairingElement);
};