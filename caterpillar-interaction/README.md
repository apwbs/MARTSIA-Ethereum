# Interaction MARTSIA-Ethereum - Caterpillar

To run Caterpillar and MARTSIA in a combined manner you should run the two containers opening the ports to let them 
communicate. To run the Caterpillar container `docker run -it --network host -v path_to_MARTSIA-Ethereum/:/MARTSIA-Ethereum orlenyslp/caterpillar-demo:v1`. In the same way run the MARTSIA_Ethereum container 
`docker run --network host -it -v path_to_MARTSIA-Ethereum/:/MARTSIA-Ethereum ethereum-martsia`.
