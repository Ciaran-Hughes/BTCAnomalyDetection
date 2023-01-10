#!/usr/bin/env python3

"""
Description: A command line tool that will detect an anomalous bitcoin transaction.
"""
import argparse
import joblib
import json

import os
import sys 
import CLIUtils

# Read in the trained ML model that does the anomaly detection. 
abs_path = os.path.dirname(__file__)
load_path = os.path.join(abs_path, '../ModelCreation/saved_models/anom_detection_pipeline.joblib')
pipeline = joblib.load(load_path)

# Read in modules in sibling directory
sys.path.append(abs_path+'/../ModelCreation/')
import DataUtils 
import BtcChainScraper

# Parse args for command line tool
parser = argparse.ArgumentParser(description="Find whether bitcoin transactions are anomalies or not")

# Can't input both raw tx and also run continuous functionality. 
group = parser.add_mutually_exclusive_group()

group.add_argument("--raw-tx", nargs='+', help="Input valid bitcoin raw transactions as list ")
group.add_argument("--run-block", type=int, help="Run the Anomaly Detector on n_txs txs in latest block. ")

# Could allow a decoded json tx as input, though seems too messy for now.
group.add_argument("--json-tx", nargs='+', help="Input valid bitcoin json decoded transactions as list")

args = parser.parse_args()


# Go over the different command line arguments 
if args.raw_tx:
    # Get the list of hex encoded transactions from command line
    list_tx_hexs  = args.raw_tx

if args.run_block: 
    n_tx = args.run_block 
    # Find the tx hashes from the latest block and use this to get the 
    # tx hexes 
    scraper = BtcChainScraper.ChainScraper()
    latestblockhash = scraper.GetLatestBlockHash()

    latestTxHashs = scraper.GetLatestBlockTxHashs(latestblockhash)
    latestTxHashs = json.loads(latestTxHashs)[:n_tx]
    list_tx_hexs = [ scraper.GetTxHexFromHash(tx_hash) for tx_hash in latestTxHashs ]


if args.raw_tx or args.run_block:
    # Get a Dataframe of the decoded Tx Hexs
    df = CLIUtils.DecodeTxsFromHexs(list_tx_hexs)

    # Split into valid and invalid transactions
    df_invalid = df[ df['verified'] == False ]
    df_valid   = df[ df['verified'] == True ].copy()

    # Find the features for ML 
    df_valid = DataUtils.AddFeatures(df_valid)

    # Units from transaction package are given in btc instead of sat. 
    # Need to convert to satoshis for the ML model
    df_valid['tot_out_val'] = 1e8 * df_valid['tot_out_val']


    # Find if valid txs are anomalous or not using same model trained earlier 
    # These are features of trained model. 
    X_valid = df_valid[['tot_out_val', 'n_addresses']]
    df_valid['y_pred'] = pipeline.predict(X_valid)

    # Print results to stdout for blowfish api integration
    CLIUtils.PrintInvalidTxs(df_invalid)
    CLIUtils.PrintValidTxs(df_valid)


if args.json_tx:
    print('Needs to be implemented')

    raise




