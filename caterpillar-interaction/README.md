# Interaction MARTSIA-Ethereum - Caterpillar

To run Caterpillar and MARTSIA in a combined manner run the two containers opening the ports to let them 
communicate. To run the Caterpillar container `docker run -it --network host -v path_to_MARTSIA-Ethereum/:/MARTSIA-Ethereum orlenyslp/caterpillar-demo:v1`. 
In the same way run the MARTSIA_Ethereum container `docker run --network host -it -v path_to_MARTSIA-Ethereum/:/MARTSIA-Ethereum ethereum-martsia`.

Then, copy the files present in the Caterpillar container into a local folder with `docker cp name_of_caterpillar_container:/usr/caterpillar path_to_a_local_folder`.

Once the files are stored locally and the two containers are open, download the 'models.controller.js' file from this repo and replace it in the Caterpillar
container with the following command `docker cp path_to_file/models.controller.js name_of_caterpillar_container:/usr/caterpillar/caterpillar-core/out/models/models.controller.js`.

At this point, open the page `http://localhost:3200/`, click on 'Create Model' in the top right corner and upload the 
'RunningExamplePaper.bpmn' file. Click save and Caterpillar will generate the Solidity code. Click on the generated instance
and then on 'Create instance' in the local host dashboard. Click on the generated hash and the on 'Go'. 

Now the BPMN in ready to run.
