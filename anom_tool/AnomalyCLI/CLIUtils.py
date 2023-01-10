"""
Description: A module that contains utility functions needed by the command line tool.

"""
import pandas as pd
import json

import os
import sys 

# Import modules from Model Creation folder. 
abs_path = os.path.dirname(__file__)
print(abs_path+'/../ModelCreation/')
sys.path.append(abs_path+'/../ModelCreation/')
import DataUtils 
import BtcChainScraper

# Need to decode bitcoin tx, for now use this package, which isn't robust 
# If had more time would use install bitcoiblib or implement own decoder
from cryptotools.BTC import transaction

def DecodeTxsFromHexs(list_hex) -> pd.DataFrame:
    """
        This function takes in a list of bitcoin encoded hex transactions
        and decodes the hex into a human-readable transaction which is stored
        in a database. 

        Note we use the cryptotools package for the decodeing, but a better solution
        would be needed for a more robust decoding. 
    """

    df = pd.DataFrame()

    # For each hex encoded transaction
    for i in range(len(list_hex)):
        ihex_tx = list_hex[i]

        # Decode the raw transaction with default settings
        tx = transaction.Transaction(0,0).from_hex(ihex_tx)
        
        #Initialise empty tx
        empty_tx = {'vin' : '', 'vout' : '', 'txid' : '', 'version' : '', 
                    'size': '', 'locktime' : ''}

        # Verify whether tx is valid or not. 
        # This imported module isn't robust. 
        # Would need to code a new one or find better alternative. 
        try:
            # If a valid tx, decode it
            if tx.verify():

                dic = {} 
                for x in tx.json():
                    dic[x] = str(tx.json()[x])

                df_temp = pd.DataFrame(dic, index=[i])
                df_temp['verified'] = True
                df_temp['RawTxHex'] = ihex_tx

                # Turns cells into list to avoid error and utilise pandas more efficiently
                df_temp.at[i, 'vin']  = tx.json()['vin']
                df_temp.at[i, 'vout'] = tx.json()['vout']

            else:
                empty_tx['txid'] = tx.json()['txid']

                df_temp = pd.DataFrame(empty_tx, index=[i])
                df_temp['verified'] = False
                df_temp['RawTxHex'] = ihex_tx

        except:
            empty_tx['txid'] = 'Invalid'
            df_temp = pd.DataFrame(empty_tx, index=[i])
            df_temp['verified'] = False
            df_temp['RawTxHex'] = ihex_tx

        # Collect all decoded transactions together
        df = pd.concat([df, df_temp], ignore_index=True)


    return df

def PrintInvalidTxs(df_invalid : pd.DataFrame):
    """
    This function will print a pretty json to stdout for the blowfish api saying that the transactions in df_invalid are not valid. 
    """

    # Construct a general json string to print
    nonvalid_json = '[ \
    {   \
        "transactionhex": "", \
        "transactionhash": "", \
        "humanReadableError": "Transaction is not valid ", \
        "kind": "INVALID_TRANSACTION" \
    }]'

    for index, row in df_invalid.iterrows():
        obj = json.loads(nonvalid_json)
        obj[0]['transactionhex'] = row['RawTxHex']
        obj[0]['transactionhash'] = 'hash(hash(hex))'

        json_formatted_str = json.dumps(obj, indent=3)
        print(json_formatted_str, file=sys.stdout)


def PrintValidTxs(df_valid: pd.DataFrame):
    """
    This function will print a pretty json to stdout for the blowfish api 
    saying whether the transactions in df_valid are anomalies or not. 
    """
    

    # Construct general strings
    anom_json = '[{"transactionhex": "hex", "transactionhash":"hash", ' \
                ' "action" : "WARN", ' \
       '"warnings": [{ "severity": "CRITICAL",' \
	            '"message": "We believe this transaction is anomalous, and is therefore suspicious. Check your input and output addresses, and the value transfered."' \
        '}], ' \
        '"simulationResults" : [{'\
                        '"numberOfAddresses": "",' \
                        '"totalOutValue (units Satoshis)": ""' \
        '}]'\
    '}]' 


    nonanom_json = '[ \
    { \
        "transactionhex": "", \
        "transactionhash": "", \
        "warnings": [{ \
	            "severity": "LOW", \
 	            "message": "" \
        }], \
        "action": "NONE" \
    }]'


    for index, row in df_valid.iterrows():

        # Print if the tx is an inlier (not anomaly)
        if row['y_pred']>=0:
            obj = json.loads(nonanom_json)
            obj[0]['transactionhex'] = row['RawTxHex']
            obj[0]['transactionhash'] = 'hash(hash(hex))'

            json_formatted_str = json.dumps(obj, indent=3)
            print(json_formatted_str, file=sys.stdout)


        # Print if tx is an outlier (anomaly) 
        if row['y_pred']<0:

            obj = json.loads(anom_json)
            obj[0]['transactionhex'] = row['RawTxHex']
            obj[0]['transactionhash'] = 'hash(hash(hex))'
            obj[0]['simulationResults'][0]['numberOfAddresses'] = row['n_addresses']
            obj[0]['simulationResults'][0]['totalOutValue (units Satoshis)'] = int(row['tot_out_val'])

            json_formatted_str = json.dumps(obj, indent=3)
            print(json_formatted_str, file=sys.stdout)

