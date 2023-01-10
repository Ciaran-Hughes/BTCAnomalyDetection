#!/usr/bin/env python3

"""
Description: The main script which performs data collection, cleaning, and fitting.

"""

# Import custom modules and packages for manipulating data
import BtcChainScraper 
import DataUtils

import matplotlib.pyplot as plt
import seaborn as sns 

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import MinMaxScaler
from sklearn.pipeline import Pipeline

import os
import joblib
import yaml

# Read in the config file 
abs_path = os.path.dirname(__file__)
rel_path = "../config.yml"
full_path = os.path.join(abs_path, rel_path)

with open(full_path, "r") as ymlfile:
    cfg = yaml.safe_load(ymlfile)

# Initialise variables
chain_scraper = BtcChainScraper.ChainScraper()

# Collect chain data, Clean the data, and Get Features for fitting
df_btc = DataUtils.GetNTxs(cfg['n_train'], chain_scraper)
df_btc = DataUtils.CleanData(df_btc)
df_btc = DataUtils.AddFeatures(df_btc)

# Set up a data fitting pipeline using scaling and forest for anomaly detection
pipeline = Pipeline([('scaler', MinMaxScaler()), 
                        ('iso', IsolationForest(contamination=cfg['contamination']))])

# Select features as our model variables
print('\nThe features which we are using are 1) the number of addresses in the transaction')
print('and 2) the total value being transfered out of the transaction.')
X = df_btc[['tot_out_val', 'n_addresses']]

# Fit the model 
# Aside: Could do hyperparam tuning in this step 
pipeline.fit(X)
df_btc['y_pred'] = pipeline.predict(X)
df_btc['y_pred_tag'] = df_btc['y_pred'].map( lambda x: 'Outlier' if x<0 else 'Inlier' )

# Print stats and make classification plot 
n_anom = sum(df_btc['y_pred'] < 0)
perc_anom = 100 - 100 * df_btc['y_pred'].mean() 
print('Number of anomalies (outliers) found : {0}'.format(n_anom))
print('Fraction of outliers found : {:.1f} %'.format(perc_anom))

save_path = os.path.join(abs_path, './saved_models/model_classification.pdf')
sns.scatterplot(data=df_btc, x="tot_out_val", y="n_addresses", hue="y_pred_tag")
plt.title("Features are standardised")
plt.savefig(save_path) 
print()
print('*'*30)
print('A plot showing which transactions are anomalies is shown in saved_models/model_classification.pdf')
print('*'*30)

# save model to be read in by command line tool 
# (can also continuously retrain to avoid data drift)
save_path = os.path.join(abs_path, './saved_models/anom_detection_pipeline.joblib')
joblib.dump(pipeline, save_path)
print()
print('*'*30)
print('The model is saved in saved_models/anom_detection_pipeline.joblib')
print('*'*30)
plt.show()





