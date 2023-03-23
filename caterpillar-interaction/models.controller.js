"use strict";
var _this = this;
Object.defineProperty(exports, "__esModule", { value: true });
var express_1 = require("express");
var solc = require("solc");
var Web3 = require("web3");
var models_parsers_1 = require("./models.parsers");
var models_store_1 = require("./models.store");
var app = require('express')();
var http = require('http').Server(app);
var io = require('socket.io')(http);
http.listen(8090, function () {
    console.log('started on port 8090');
});
var models = express_1.Router();
var web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
//var web3 = new Web3(new Web3.providers.HttpProvider("http://193.40.11.64:80"));
var activityContractMap = new Map();
var runningActivities = new Map(); // contract-activity
var enabledTasks = new Map();
var validExecution = false;
web3.eth.filter("latest", function (error, result) {
    if (!error) {
        var info = web3.eth.getBlock(result);
        if (info.transactions.length > 0) {
            console.log('----------------------------------------------------------------------------------------------');
            console.log('NEW BLOCK MINED');
            var updatesInProcess = false;
            var contractsToNotify = [];
            info.transactions.forEach(function (transactionHash) {
                if (runningActivities.has(transactionHash)) {
                    var activityData = runningActivities.get(transactionHash);
                    var contractsArray = activityContractMap.get(activityData.activity);
                    if (contractsArray.length == 1)
                        activityContractMap.delete(activityData.activity);
                    else
                        contractsArray.splice(contractsArray.indexOf(activityData.contract));
                    runningActivities.delete(transactionHash);
                }
                var transRec = web3.eth.getTransactionReceipt(transactionHash);
                transRec.logs.forEach(function (logElem) {
                    var contractAddress = logElem.address.toString();
                    if (instances.has(contractAddress)) {
                        var _a = instances.get(contractAddress), contractName = _a[0], modelInfo = _a[1];
                        var elementName = contractName.slice(contractName.indexOf(':') + 1, contractName.indexOf('_Contract'));
                        var controlFlowInfo = modelInfo.controlFlowInfoMap.get(elementName);
                        var nodeId = controlFlowInfo.nodeList[Math.log2(parseInt(logElem.data, 16))];
                        if (nodeId !== undefined) {
                            console.log(controlFlowInfo.nodeNameMap.get(nodeId) + " COMPLETED IN CONTRACT " + contractAddress);
                            updatesInProcess = true;
                        }
                        else
                            console.log("MESSAGE RECEIVED FROM CONTRACT " + contractAddress);
                    }
                    if (workListInstances.has(contractAddress)) {
                        var realContractAddress = workListInstances.get(contractAddress);
                        var _a = instances.get(realContractAddress), contractName = _a[0], modelInfo = _a[1];
                        var elementName = contractName.slice(contractName.indexOf(':') + 1, contractName.indexOf('_Contract'));
                        var controlFlowInfo = modelInfo.controlFlowInfoMap.get(elementName);
                        var nodeId = controlFlowInfo.nodeList[Math.log2(parseInt(logElem.data, 16))];
                        if (nodeId !== undefined) {
                            console.log(controlFlowInfo.nodeNameMap.get(nodeId) + " IS ENABLED IN CONTRACT " + realContractAddress);
                            updatesInProcess = true;
                        }
                    }
                });
                console.log('----------------------------------------------------------------------------------------------');
            });
            if (updatesInProcess) {
                console.log('----------------------------------------------------------------------------------------------');
                console.log("Message sent through socket running on port 8090");
                console.log('----------------------------------------------------------------------------------------------');
                io.emit('message', { type: 'new-message', text: "Updates in Server" });
            }
        }
    }
});
models.get('/processes', function (req, res, next) {
    console.log('QUERYING ALL ACTIVE CONTRACTS');
    var actives = [];
    instances.forEach(function (dataList, addr, map) {
        console.log({ id: dataList[1].name, name: dataList[1].entryContractName, contractName: dataList[0], address: addr });
        actives.push({ id: dataList[1].name, name: dataList[1].entryContractName, contractName: dataList[0], address: addr });
    });
    console.log('----------------------------------------------------------------------------------------------');
    if (actives.length > 0) {
        res.status(200).send(actives);
    }
    else {
        console.log('No Contracts Available');
        res.status(200).send([]);
    }
});
models.get('/models', function (req, res, next) {
    console.log('QUERING REGISTERED MODELS');
    var actives = [];
    models_store_1.modelStore.forEach(function (modelInfo, modelId, map) {
        console.log(modelInfo.entryContractName);
        actives.push({ id: modelId, name: modelInfo.entryContractName, bpmn: modelInfo.bpmn, solidity: modelInfo.solidity });
    });
    console.log('----------------------------------------------------------------------------------------------');
    res.send(actives);
});
models.post('/models', function (req, res, next) {
    var modelInfo = req.body;
    try {
        var cont = models_parsers_1.parseModel(modelInfo);
        cont.then(function () {
            var input = {};
            input[modelInfo.name] = modelInfo.solidity;
            var activityNames = [];
            modelInfo.controlFlowInfoMap.forEach(function (controlFlowInfo, contractName, map) {
                controlFlowInfo.callActivities.forEach(function (activityName, activityId, map2) {
                    activityNames.push(activityName);
                });
            });
            activityNames.forEach(function (activityName) {
                if (!models_store_1.modelStore.has(activityName)) {
                    res.status(404).send("ERROR: Process model '" + activityName + "' not found");
                    return;
                }
                input[activityName] = models_store_1.modelStore.get(activityName).solidity;
            });
            console.log('=============================================');
            console.log("SOLIDITY CODE");
            console.log('=============================================');
            Object.keys(input).forEach(function (key) {
                console.log(input[key]);
            });
            console.log('----------------------------------------------------------------------------------------------');
            var output = solc.compile({ sources: input }, 1);
            if (Object.keys(output.contracts).length === 0) {
                res.status(400).send('COMPILATION ERROR IN SMART CONTRACTS');
                console.log('COMPILATION ERROR IN SMART CONTRACTS');
                console.log('----------------------------------------------------------------------------------------------');
                return;
            }
            console.log('CONTRACTS');
            Object.keys(output.contracts).forEach(function (key) {
                console.log(key);
            });
            modelInfo.contracts = output.contracts;
            models_store_1.modelStore.set(modelInfo.name, modelInfo);
            res.status(201).send({
                id: modelInfo.name,
                name: modelInfo.entryContractName,
                bpmn: modelInfo.bpmn,
                solidity: modelInfo.solidity
            });
            console.log('PROCESSED SUCCESSFULLY');
            console.log('----------------------------------------------------------------------------------------------');
        });
    }
    catch (e) {
        console.log("Error: ", e);
        res.status(400).send(e);
    }
});
var instances = new Map();
var workListInstances = new Map();
var workListRealAddress = new Map();
var globalControlFlowInfo;
var computeActivation = function (contractAddress) {
    var _a = instances.get(contractAddress), contractName = _a[0], modelInfo = _a[1];
    var contract = web3.eth.contract(JSON.parse(modelInfo.contracts[contractName].interface));
    var elementName = contractName.slice(contractName.indexOf(':') + 1, contractName.indexOf('_Contract'));
    var controlFlowInfo = modelInfo.controlFlowInfoMap.get(elementName);
    var nodeList = controlFlowInfo.nodeList;
    var instance = contract.at(contractAddress);
    var workListAddress = instance.getWorkListAddress.call(); // worklistAddress
    var activation = instance.getStartedFlowNodes.call();
    var activationAsString = activation.toString(2).split('').reverse();
    var workItemList = [];
    var externalItemGroupList = [];
    var addresses = instance.getSubprocessAddresses ? instance.getSubprocessAddresses.call() : 0;
    var mWorkListAddress = workListAddress.toString();
    if (!workListInstances.has(mWorkListAddress)) {
        workListInstances.set(mWorkListAddress, contractAddress.toString());
        workListRealAddress.set(mWorkListAddress, workListAddress);
    }
    for (var index = 0; index < activationAsString.length; index++)
        if (activationAsString[index] === '1') {
            var nodeId = controlFlowInfo.nodeList[index];
            if (controlFlowInfo.activeMessages.indexOf(nodeId) >= 0) {
                var reqIds = instance.getTaskRequestIndex.call(1 << index).toString(2).split('').reverse();
                for (var i = 0; i < reqIds.length; i++) {
                    validExecution = true;
                    if (reqIds[i] === '1') {
                        workItemList.push({
                            elementId: nodeId,
                            processAddress: contractAddress,
                            hrefs: ["/workitems/" + workListAddress + "/" + i]
                        });
                    }
                }
            }
            var nestedSubprocesses = new Map();
            if (controlFlowInfo.nonInterruptingEvents.has(nodeId))
                nestedSubprocesses = controlFlowInfo.nonInterruptingEvents;
            else if (controlFlowInfo.multiinstanceActivities.has(nodeId) && controlFlowInfo.childSubprocesses.has(nodeId))
                nestedSubprocesses = controlFlowInfo.childSubprocesses;
            if (nestedSubprocesses.size > 0) {
                var mask = instance.getInstances.call(1 << index); // TODO: Should be a bignumber?
                var maskAsString = mask.toString(2).split('').reverse();
                for (var iindex = 0; iindex < maskAsString.length; iindex++)
                    if (maskAsString[iindex] === '1') {
                        var addr = addresses[iindex].toString();
                        var subprocessContractName = nestedSubprocesses.get(nodeId);
                        instances.set(addr, [subprocessContractName, modelInfo]);
                        var _b = computeActivation(addr), nestedWorkItemList = _b[0], nestedExternalItemGroupList = _b[1];
                        nestedWorkItemList.forEach(function (workItem) {
                            var originalWorkItem = workItemList.find(function (witem) { return witem.elementId === workItem.elementId; });
                            if (!originalWorkItem) {
                                originalWorkItem = { elementId: workItem.elementId, hrefs: [] };
                                workItemList.push(originalWorkItem);
                            }
                            originalWorkItem.hrefs = originalWorkItem.hrefs.concat(workItem.hrefs);
                        });
                        nestedExternalItemGroupList.forEach(function (externalItemGroup) {
                            var originalExternalItemGroup = externalItemGroupList.find(function (eitem) { return eitem.elementId === externalItemGroup.elementId; });
                            if (!originalExternalItemGroup) {
                                originalExternalItemGroup = { elementId: externalItemGroup.elementId, hrefs: [] };
                                externalItemGroupList.push(originalExternalItemGroup);
                            }
                            originalExternalItemGroup.hrefs = originalExternalItemGroup.hrefs.concat(externalItemGroup.hrefs);
                        });
                    }
                // verificar si es aquí donde tengo que adicionar la dirección del worklist que se crea internamente
            }
            else if (controlFlowInfo.multiinstanceActivities.has(nodeId)) {
                var mask_1 = instance.getInstances.call(1 << index); // TODO: Should be bignumber?
                var maskAsString_1 = mask_1.toString(2).split('').reverse();
                var hrefList = [];
                for (var iindex = 0; iindex < maskAsString_1.length; iindex++)
                    if (maskAsString_1[iindex] === '1') {
                        var addr_1 = addresses[iindex].toString();
                        var functionName = controlFlowInfo.nodeNameMap.get(nodeId);
                        instances.set(addr_1, [controlFlowInfo.multiinstanceActivities.get(nodeId), modelInfo]);
                        var reqIds = instance.getTaskRequestIndex.call(1 << index).toString(2).split('').reverse();
                        for (var i = 0; i < reqIds.length; i++) {
                            if (reqIds[i] === '1')
                                hrefList.push("/workitems/" + workListAddress + "/" + i);
                        }
                    }
                workItemList.push({ elementId: nodeId, hrefs: hrefList });
            }
            else if (controlFlowInfo.callActivities.has(nodeId)) {
                var mask_2 = instance.getInstances.call(1 << index); // TODO: Should be a bignumber?
                var maskAsString_2 = mask_2.toString(2).split('').reverse();
                var hrefList = [];
                for (var iindex = 0; iindex < maskAsString_2.length; iindex++)
                    if (maskAsString_2[iindex] === '1') {
                        var addr_2 = addresses[iindex].toString();
                        var subprocessModelName = controlFlowInfo.nodeNameMap.get(nodeId);
                        var subprocessModelInfo = models_store_1.modelStore.get(subprocessModelName);
                        instances.set(addr_2, [subprocessModelInfo.entryContractName, subprocessModelInfo]);
                        var _ma = instances.get(addresses[iindex]), mContractName = _ma[0], mModelInfo = _ma[1];
                        var mContract = web3.eth.contract(JSON.parse(mModelInfo.contracts[mContractName].interface));
                        var mInstance = contract.at(addresses[iindex]);
                        var mWorkListAddress = mInstance.getWorkListAddress.call().toString();
                        if (!workListInstances.has(mWorkListAddress)) {
                            workListInstances.set(mWorkListAddress, addr_2);
                            workListRealAddress.set(mWorkListAddress, mInstance.getWorkListAddress.call());
                        }
                        hrefList.push("" + addr_2);
                    }
                externalItemGroupList.push({ elementId: nodeId, hrefs: hrefList });
            }
            else {
                var reqIds = instance.getTaskRequestIndex.call(1 << index).toString(2).split('').reverse();
                for (var i = 0; i < reqIds.length; i++) {
                    validExecution = true;
                    if (reqIds[i] === '1') {
                        workItemList.push({
                            elementId: nodeId,
                            processAddress: contractAddress,
                            hrefs: ["/workitems/" + workListAddress + "/" + i]
                        });
                    }
                }
            }
        }
    activation = instance.getRunningFlowNodes.call();
    activationAsString = activation.toString(2).split('').reverse();
    for (var index = 0; index < activationAsString.length; index++)
        if (activationAsString[index] === '1') {
            var nodeId = controlFlowInfo.nodeList[index];
            workItemList.push({
                elementId: nodeId,
                processAddress: contractAddress,
                hrefs: []
            });
        }
    globalControlFlowInfo = controlFlowInfo;
    return [workItemList, externalItemGroupList];
};
var getExtendedList = function (originalList) {
    var extendedWorkItemList = [];
    originalList.forEach(function (workItem) {
        var nextStatus = workItem.hrefs.length == 0 ? ['running'] : [];
        workItem.hrefs.forEach(function (href) {
            nextStatus.push('started');
        });
        var inputParams = [];
        if (globalControlFlowInfo.localParameters.has(workItem.elementId)) {
            globalControlFlowInfo.localParameters.get(workItem.elementId).forEach(function (input) {
                inputParams.push({ type: input.type, name: input.name });
            });
        }
        extendedWorkItemList.push({ elementId: workItem.elementId, input: inputParams, status: nextStatus, hrefs: workItem.hrefs });
    });
    return extendedWorkItemList;
};
var computeExtendedActivation = function (contractAddress) {
    var _b = computeActivation(contractAddress), workItemList = _b[0], externalItemGroupList = _b[1];
    return [getExtendedList(workItemList), getExtendedList(externalItemGroupList)];
};
models.post('/models/:modelId', function (req, res) {
    if (models_store_1.modelStore.has(req.params.modelId)) {
        var modelInfo_1 = models_store_1.modelStore.get(req.params.modelId);
        var entryContract = modelInfo_1.entryContractName;
        console.log('----------------------------------------------------------------------------------------------');
        console.log("TRYING TO CREATE INSTANCE OF CONTRACT: ", entryContract);
        var ProcessContract = web3.eth.contract(JSON.parse(modelInfo_1.contracts[entryContract].interface));
        ProcessContract.new({ from: web3.eth.accounts[0], data: "0x" + modelInfo_1.contracts[entryContract].bytecode, gas: 4700000 }, function (err, contract) {
            if (err) {
                console.log('error ', err);
                res.status(404).send('ERROR: Contract could not be instantiated');
            }
            else if (contract.address) {
                instances.set(contract.address.toString(), [modelInfo_1.entryContractName, modelInfo_1]);
                var workListAdr = contract.getWorkListAddress.call().toString();
                workListInstances.set(workListAdr, contract.address.toString());
                workListRealAddress.set(workListAdr, contract.getWorkListAddress.call());
                console.log('CONTRACT CREATED !!! AT ADDRESS: ', contract.address.toString());
                console.log('WORKITEMS ADDRESS: ', contract.getWorkListAddress.call());
                console.log('----------------------------------------------------------------------------------------------');
                res.status(201).send({ address: contract.address });
            }
        });
    }
    else
        res.status(404).send('Process model not found');
});
models.get('/processes/:procId', function (req, res) {
    var contractAddress = req.params.procId;
    console.log('----------------------------------------------------------------------------------------------');
    console.log('QUERYING ACTIVATION FOR CONTRACT:', contractAddress);
    if (instances.has(contractAddress)) {
        enabledTasks = new Map();
        var _b = computeExtendedActivation(contractAddress), workItemList = _b[0], externalItemGroupList = _b[1];
        console.log("External ", externalItemGroupList);
        var _c = instances.get(contractAddress), contractName = _c[0], modelInfo = _c[1];
        console.log("CHECKING STARTED ELEMENTS ", workItemList.length == 0 && externalItemGroupList.length == 0 ? "Empty" : "..........");
        var toDraw = workItemList.concat(externalItemGroupList);
        toDraw.forEach(function (elem) {
            enabledTasks.set(elem.elementId, contractAddress);
            console.log("Element ID: ", elem.elementId);
            console.log("Input Parameters: ", elem.input);
            console.log("Status: ", elem.status);
            console.log("hrefs: ", elem.hrefs);
            console.log("...............................................................");
        });
        if (workItemList.length == 0 && externalItemGroupList.length == 0) {
            if (instances.has(contractAddress)) {
                instances.delete(contractAddress);
                workListInstances.forEach(function (procAddr, workListAddr, map) {
                    if (procAddr === contractAddress) {
                        workListInstances.delete(workListAddr);
                        workListRealAddress.delete(workListAddr);
                    }
                });
            }
        }
        console.log('----------------------------------------------------------------------------------------------');
        res.status(200).send({ bpmn: modelInfo.bpmn, workItems: workItemList, externalItemGroupList: externalItemGroupList });
    }
    else
        res.status(404).send('Process instance not found');
});
models.post('/workitems/:workListAddress/:reqId', function (req, res) {
    var workListAddress = req.params.workListAddress;
    var reqId = req.params.reqId;
    var activityId = req.body.elementId;
    var inputParams = req.body.inputParameters;

    if (activityId != "Order_parts") {

        var realParameters = inputParams.length > 0 ? [reqId].concat(inputParams) : [reqId];
        if (validExecution && enabledTasks.has(activityId) && workListInstances.has(workListAddress) && instances.has(workListInstances.get(workListAddress))) {
            validExecution = false;
            var _b = instances.get(workListInstances.get(workListAddress)), contractName = _b[0], modelInfo = _b[1];
            var elementName = contractName.slice(contractName.indexOf(':') + 1, contractName.indexOf('_Contract'));
            var activityName = modelInfo.controlFlowInfoMap.get(elementName).nodeNameMap.get(req.body.elementId);
            console.log('----------------------------------------------------------------------------------------------');
            console.log("WANT TO FIRE Task: " + activityName + ", ON WORKITEM: " + workListAddress);
            var result = void 0;
            var contract = web3.eth.contract(JSON.parse(modelInfo.contracts[contractName.slice(0, contractName.indexOf('_Contract')) + "_WorkList"].interface));
            var instance = contract.at(workListRealAddress.get(workListAddress));
            if (!modelInfo.controlFlowInfoMap.get(elementName).localParameters.has(activityId) || modelInfo.controlFlowInfoMap.get(elementName).localParameters.get(activityId).length == 0)
                activityName = 'DefaultTask';
            result = instance[activityName + '_callback'].apply(_this, realParameters.concat({ from: web3.eth.accounts[1], gas: 4700000 }));
            if (!activityContractMap.has(activityId) || activityContractMap.get(activityId).indexOf(workListAddress) < 0) {
                runningActivities.set(result, { activity: req.body.elementId, contract: workListAddress });
                if (!activityContractMap.has(activityId))
                    activityContractMap.set(activityId, []);
                activityContractMap.get(activityId).push(workListAddress);
            }
            console.log("TRANSACTION: " + result + ", PENDING !!!");
            console.log('----------------------------------------------------------------------------------------------');
            res.status(201).send(result);
        }
        else
            res.status(404).send('Invalid Execution');

    } else {

        const fs1 = require('fs');
        const filePath1 = '/MARTSIA-Ethereum/architecture/files/data_to_martsia.json';
        const jsonObj = {
            clear_data: inputParams[0],
            martsia: inputParams[1],
        };
        fs1.writeFile(filePath1, JSON.stringify(jsonObj), (err) => {
            if (err) throw err;
        });

        const filePath = '/MARTSIA-Ethereum/architecture/files/ciphered_file.json';
        const fs = require('fs');
        function readFile(filePath, callback) {
            fs.readFile(filePath, 'utf8', callback);
        }
        function readAndParseJson(filePath, callback) {
            readFile(filePath, (err, jsonContent) => {
                if (err) {
                    // console.error('Si è verificato un errore:', err);
                    console.log('Riprovo tra 10 secondi...');
                    setTimeout(() => {
                        readAndParseJson(filePath, callback);
                    }, 10000);
                } else {
                    try {
                        const jsonObj = JSON.parse(jsonContent);
                        const stringList = Object.keys(jsonObj).map(key => jsonObj[key].trim());
                        callback(null, stringList);
                    } catch (err) {
                        console.error('Si è verificato un errore:', err);
                        callback(err, null);
                    }
                }
            });
        }
        readAndParseJson(filePath, (err, stringList) => {
            if (err) {
                console.error('Si è verificato un errore:', err);
            } else {
                // console.log('Lista di stringhe ora:', stringList);
                var inputParams2 = stringList

            }
            console.log(inputParams2);


            var realParameters = inputParams2.length > 0 ? [reqId].concat(inputParams2) : [reqId];
            if (validExecution && enabledTasks.has(activityId) && workListInstances.has(workListAddress) && instances.has(workListInstances.get(workListAddress))) {
                validExecution = false;
                var _b = instances.get(workListInstances.get(workListAddress)), contractName = _b[0], modelInfo = _b[1];
                var elementName = contractName.slice(contractName.indexOf(':') + 1, contractName.indexOf('_Contract'));
                var activityName = modelInfo.controlFlowInfoMap.get(elementName).nodeNameMap.get(req.body.elementId);
                console.log('----------------------------------------------------------------------------------------------');
                console.log("WANT TO FIRE Task: " + activityName + ", ON WORKITEM: " + workListAddress);
                var result = void 0;
                var contract = web3.eth.contract(JSON.parse(modelInfo.contracts[contractName.slice(0, contractName.indexOf('_Contract')) + "_WorkList"].interface));
                var instance = contract.at(workListRealAddress.get(workListAddress));
                if (!modelInfo.controlFlowInfoMap.get(elementName).localParameters.has(activityId) || modelInfo.controlFlowInfoMap.get(elementName).localParameters.get(activityId).length == 0)
                    activityName = 'DefaultTask';
                result = instance[activityName + '_callback'].apply(_this, realParameters.concat({ from: web3.eth.accounts[1], gas: 4700000 }));
                if (!activityContractMap.has(activityId) || activityContractMap.get(activityId).indexOf(workListAddress) < 0) {
                    runningActivities.set(result, { activity: req.body.elementId, contract: workListAddress });
                    if (!activityContractMap.has(activityId))
                        activityContractMap.set(activityId, []);
                    activityContractMap.get(activityId).push(workListAddress);
                }
                console.log("TRANSACTION: " + result + ", PENDING !!!");
                console.log('----------------------------------------------------------------------------------------------');
                res.status(201).send(result);
            }
            else
                res.status(404).send('Invalid Execution');
        });

    }


});
exports.default = models;
//# sourceMappingURL=models.controller.js.map
