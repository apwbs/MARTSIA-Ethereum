var messageExchange = artifacts.require("messageExchange");

module.exports = function(deployer) {
    deployer.deploy(messageExchange);
};