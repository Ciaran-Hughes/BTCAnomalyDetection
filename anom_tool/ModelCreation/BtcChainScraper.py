"""
Description: A module to scrape the bitcoin chain using the mempool.space api

"""

import requests
import pandas as pd

class ChainScraper(): 
    """
    This Class contains all the functions needed to scrap the bitcoin chain using 
    the mempool.space api, starting from the latest block, and going linearly back until
    n_txs are found
    """
    def __init__(self):
        self.api_tag = "https://mempool.space/api/"
        self.block_heights_scraped = [] 


    def GetLatestBlockHash(self) -> str:
        """
        Find the latest block hash from mempool.space api
        """
        end_tag = 'blocks/tip/hash'
        result = requests.get(url = self.api_tag + end_tag, params = {})
        return result.content.decode('utf-8')

    def GetBlockHash(self, block_height) -> str:
        """
        Given a block height, find the blocks hash. Needed to find the blocks transations
        from mempool.space  
        """
        end_tag = '/block-height/' + str(block_height)
        result = requests.get(url = self.api_tag + end_tag, params = {})
        return result.content.decode('utf-8')



    def GetLatestBlockHeight(self) -> int:
        """
        Find the latest block height from mempool.space api
        """
        end_tag = 'blocks/tip/height'
        result = requests.get(url = self.api_tag + end_tag, params = {})
        return int(result.content.decode('utf-8'))


    def GetLatestBlockTxHashs(self, block_hash: str):
        """
        Find the latest block Tx Hashes from mempool.space api
        """
        end_tag = 'block/'+str(block_hash)+'/txids'
        result = requests.get(url = self.api_tag + end_tag, params = {})
        return result.content.decode('utf-8')

    def GetTxHexFromHash(self, tx_hash: str) -> str:
        """
        Find the Hex of a Tx from its Hash from mempool.space api
        """
        end_tag = 'tx/'+str(tx_hash)+'/hex'
        result = requests.get(url = self.api_tag + end_tag, params = {})
        return result.content.decode('utf-8')


    def GetTxsFromBlock(self, block_hash: str, n_txs_left: int ) -> pd.DataFrame: 
        """
        Find all transactions from a block which has hash = block_hash. If we only want 
        n_txs_left txs, then dont find all the block transactions
        """

        # Initialise variable. Note mempool.space only allows reading 
        # 25 txs from a block at a time, so we need to pagentate
        df = pd.DataFrame()
        tx_batch = 0

        # Put an escape clause on while loop. 
        # escape while loop in the worst case where a block has 
        # 5-10x more txs than should be possible
        max_num_batches = 800

        # Keep reading from block in batches of 25. 
        while tx_batch < max_num_batches:

            # Read the 25 transactions from the block starting at the ith=25*tx_batch tx. 
            end_tag = 'block/' + block_hash + '/txs/' + str(25*tx_batch)
            result = requests.get(url = self.api_tag + end_tag, params = {})
            block25_txs = result.content.decode('utf-8')

            # If we have read all the blocks transactions, then return
            if block25_txs.strip() == 'start index out of range':
                print('Finished reading from block {0} with a total number of txs {1}'.format(block_hash, df.shape[0]))
                return df

            # Error control: if we don't have a multiple of 25 then the api breaks
            if block25_txs.strip() == 'start index must be a multipication of 25':
                print('The pagenation start in the api call must be a multiple of 25')
                raise 

            # Read these 25 transactions into a dataframe,
            # and concat them into a single dataframe
            df_temp=pd.read_json(block25_txs)
            df = pd.concat([df, df_temp], ignore_index=True)

            # If we don't need to read more txs, then return
            if n_txs_left <= tx_batch*25:
                return df

            #increment to the next batch
            tx_batch += 1

        


