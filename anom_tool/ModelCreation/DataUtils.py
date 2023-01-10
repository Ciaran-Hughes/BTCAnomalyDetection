"""
Description: Utilies used to manipulate data in order to fit it. 

"""

import json
import requests
import pandas as pd
import BtcChainScraper

def GetNTxs(n_txs: int, scraper: BtcChainScraper.ChainScraper) -> pd.DataFrame:
    """
    This function collects n_txs from the mempool.space bitcoin indexer
    starting from the latest published block
    --------
    n_txs: the number of transactions you want to analyse
    scraper: the class which scrapes the data

    returns: the in a pandas Dataframe 
    """

    #initialise variables
    df = pd.DataFrame() 
    iblockhash   = scraper.GetLatestBlockHash()
    iblockheight = scraper.GetLatestBlockHeight()

    # keep scanning blocks starting from latest until we have the number of 
    # transactions we want
    while df.shape[0] < n_txs: 

        # Find the height and hash of the previous block 
        iblockheight -= 1 
        iblockhash = scraper.GetBlockHash(iblockheight)

        # Only scrape a block if we want more txs
        n_left = n_txs - df.shape[0]
        iblockdf = scraper.GetTxsFromBlock(block_hash=iblockhash, n_txs_left=n_left)

        # Cache the block heights that we scraped
        scraper.block_heights_scraped.append(iblockheight)
        
        # Concat all the txs into a single dataframe 
        df = pd.concat([df, iblockdf], ignore_index=True)

    return df 


def CleanData(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of indexed data, clean it. 
    We would normally want to check types, impute missing data, etc
    """

    #remove null values 
    df = df.dropna() 

    return df

def tot_out_val(row):
    """
    Helper function to find the total outgoing btc in a tx.
    """
    out_val = 0
    # Note not a numpy array so cannot use reduce
    try:
        for out_tx in row['vout']:
            out_val += out_tx['value']
    #Sometimes there is no input due to new coins being minted.
    # Ex: 22dd52bd6ff432c2fc5aa524abe53ca78227172e4df32f11caaad5681be6a7f9
    # Wrap this edge case in a try-except clause
    except:
        out_val = 0 
    return out_val
    
def AddFeatures(df: pd.DataFrame) -> pd.DataFrame:
    """
    Given our dataframe, find the features that we want to use in our 
    anomaly detection algorithm. 

    Other features might include: the fee amount, 
    input and output addresses seperately,
    historical info about a wallet, etc
    """

    # Find the total number of addresses involved in a transaction
    df['num_out_addresses'] = df['vout'].apply(lambda row: len(row))
    df['num_in_addresses'] = df['vin'].apply(lambda row: len(row))
    df['n_addresses'] = df['num_out_addresses'] + df['num_in_addresses']

    # Find the total initial amount transfered in a transaction
    df['tot_out_val'] = df.apply(tot_out_val, axis=1)

    return df 

