

# BTCAnomalyDetection

## Anomaly Detection for Bitcoin Transactions 



This codebase is intended to be used for two complementary objectives: 
1. To train an anomaly detection model on bitcoin transactions. 
   
   - The anomaly detection model currently takes in two features: i) the total number of addresses involved in the transaction; ii) the total amount sent out in the transaction. More features can be added if needed. 

   - The anomaly detection model uses scitkit-learn's [isolation forest algorithm](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html#sklearn.ensemble.IsolationForest), with parameters set in the config file. After training the model, a plot visualizing how the algorithm is classifying the transactions is shown. 


2. Have a command line tool that can detect if a bitcoin transaction is anomalous or not (using the above anomalous detection model). 
   
     - The CLI can accept a list of raw hex-encoded bitcoin transactions, and will classify them as anomalous or not. 

     - The CLI also has a flag to test the latest "n" transactions in the current bitcoin block. This can be used for testing, or used for real-time anomalous transaction detection. 

     - Note if a transaction is invalid, the output will classify it as invalid rather than anomalous or not. 




Further details on both goals are given below. 


## Prerequisites


Python3 is needed to run this package. The easiest way to run this code is to make a new conda environment with python3.9.6
```
$ conda create -n "anom_detect" python=3.9.6
```

Now install the modules that are needed inside this conda environment by running 
```
$ pip install -r requirements.txt
```

Note: this code does not contain a setup.py as it is not intended to be installed globally on a system. 


# Usage 

The directory structure of this package is laid out as follows:
```
                                 |--> ModelCreation--> SaveModel
               |--> anom_tool ---|
  Anom_tool ---|                 |--> AnomalyCLI
               |--> tests
               |--> examples 
```

## Model Creation 

---

To create the anomaly detection model, move to the ModelCreation directory 
and run 
```
  $ python AnomalyModelCreation.py 
```

Note that the number of training samples to use is set in the config.yml file, which is located in the anom_tool directory. 
After running this, a scikit-learn anomaly detection model is saved in the SavedModels folder. This model can be used on-the-fly to detect anomalies (which the second part of the code does). 

This code also outputs some statistics to the screen about the absolute number and percentage of anomalies found in the training set. A classification plot is saved in SavedModels to visualize the outlier detection. 

## Anomaly Detection via python command line tool

---

To utilize the anomaly detection model, there is a python command line tool in the AnomalyCLI directory. This can be run using python or as an executable

```
 python anomaly_cli.py -h 
```

or 

```
 ./anomaly_cli.py -h 
```

There are two options for command line arguments
1. --raw-tx: this allows one to include a list of hex encoded bitcoin transactions. 
2. --run-block: Instead of inputting hex-encoded bitcoin transactions, this reads the latest "n" bitcoin transactions from the current bitcoin block.  This option allows the user to make sure the tool is working as desired, or can be used for real-time anomalous transaction detection. 

### Examples 

To run the tool to detect whether the latest 10 bitcoin transactions are anomalous or not, run 

```
  ./anomaly_cli.py --run-block 10 
```

To run the tool to detect whether a specific hex-encoded transaction is anomalous or not, run 

```
  ./anomaly_cli.py --raw-tx 010000000536a007284bd52ee826680a7f43536472f1bcce1e76cd76b826b88c5884eddf1f0c0000006b483045022100bcdf40fb3b5ebfa2c158ac8d1a41c03eb3dba4e180b00e81836bafd56d946efd022005cc40e35022b614275c1e485c409599667cbd41f6e5d78f421cb260a020a24f01210255ea3f53ce3ed1ad2c08dfc23b211b15b852afb819492a9a0f3f99e5747cb5f0ffffffffee08cb90c4e84dd7952b2cfad81ed3b088f5b32183da2894c969f6aa7ec98405020000006a47304402206332beadf5302281f88502a53cc4dd492689057f2f2f0f82476c1b5cd107c14a02207f49abc24fc9d94270f53a4fb8a8fbebf872f85fff330b72ca91e06d160dcda50121027943329cc801a8924789dc3c561d89cf234082685cbda90f398efa94f94340f2ffffffff36a007284bd52ee826680a7f43536472f1bcce1e76cd76b826b88c5884eddf1f060000006b4830450221009c97a25ae70e208b25306cc870686c1f0c238100e9100aa2599b3cd1c010d8ff0220545b34c80ed60efcfbd18a7a22f00b5f0f04cfe58ca30f21023b873a959f1bd3012102e54cd4a05fe29be75ad539a80e7a5608a15dffbfca41bec13f6bf4a32d92e2f4ffffffff73cabea6245426bf263e7ec469a868e2e12a83345e8d2a5b0822bc7f43853956050000006b483045022100b934aa0f5cf67f284eebdf4faa2072345c2e448b758184cee38b7f3430129df302200dffac9863e03e08665f3fcf9683db0000b44bf1e308721eb40d76b180a457ce012103634b52718e4ddf125f3e66e5a3cd083765820769fd7824fd6aa38eded48cd77fffffffff36a007284bd52ee826680a7f43536472f1bcce1e76cd76b826b88c5884eddf1f0b0000006a47304402206348e277f65b0d23d8598944cc203a477ba1131185187493d164698a2b13098a02200caaeb6d3847b32568fd58149529ef63f0902e7d9c9b4cc5f9422319a8beecd50121025af6ba0ccd2b7ac96af36272ae33fa6c793aa69959c97989f5fa397eb8d13e69ffffffff0400e6e849000000001976a91472d52e2f5b88174c35ee29844cce0d6d24b921ef88ac20aaa72e000000001976a914c15b731d0116ef8192f240d4397a8cdbce5fe8bc88acf02cfa51000000001976a914c7ee32e6945d7de5a4541dd2580927128c11517488acf012e39b000000001976a9140a59837ccd4df25adc31cdad39be6a8d97557ed688ac00000000
``` 

In both cases, the output is a json-packet with relevant information which describes whether or not a transaction is anomalous, or if it is an invalid transaction. 


# Dependencies 

- To decode the hex-encoded bitcoin transaction, a third-party tool called [cryptotools](https://github.com/mcdallas/cryptotools/blob/master/cryptotools/BTC/transaction.py#L307) is used. Potential issue of supply-chain attack. Likely need to code personal version for production. 
- The [mempool.space indexer api](https://mempool.space/docs/api/rest#get-transaction-hex) is used to get the latest blockchain data to train the model on, and also to showcase the CLI. 
<!--
das
- Use[mempool.space visualisation](https://mempool.space/tx/546f00a799cdc5a814a0e5e32135774dafcfa795a6b1adf8db648d26b088d9bc) to verify raw Txn decoding and anomaly detection.    
- Use [web interface](https://live.blockcypher.com/btc/decodetx/) to make sure the decoding works as expected. 
-->

# LICENSE

This project is open source under the MIT license as given in LICENSE.txt 



# Project Status


### Data Source
- This code base uses an external bitcoin indexer in order to scrape data to fit the model. The same indexer is also used to take the latest transactions and classify them as anomalous or not. If the external indexer is replaced with a personal node, it would scale well. It would also be straightforward to extend the code to read from an SQL database of historical transactions. 
  
### Speed
- The slowest part of the code is acquiring the data from the indexer for training the model. <!--This is because the api calls are rate limited and only return 25 transactions per api call. -->
This restrictions would be removed if a local node was hosted. 
- Some panda's dataframe calls (like apply's) are inefficient and could be replaced or vectorised if needed. 

### Maintainable 
- The separation into tasks allows the model to be retrained on more recent data to avoid data-drift concurrently to the tooling being used. 
- The code is modularized, with different modules doing conceptually different tasks, and with a functional programming framework coding style, in order to ensure maintainability, extendability, and simplicity. 
