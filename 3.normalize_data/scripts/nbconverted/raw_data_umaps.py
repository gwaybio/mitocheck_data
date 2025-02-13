#!/usr/bin/env python
# coding: utf-8

# ### Import libraries

# In[1]:


import pathlib
import pandas as pd
import numpy as np

import sys
sys.path.append("../utils")
from load_utils import compile_mitocheck_batch_data, split_data
from analysis_utils import get_2D_umap_embeddings, show_2D_umap_from_embeddings


# ### Compile control data

# In[2]:


# get 10% of negative control features
negative_control_data_path = pathlib.Path("../1.idr_streams/extracted_features/negative_control_data/merged_features")
negative_control_data = compile_mitocheck_batch_data(negative_control_data_path)
negative_control_data = negative_control_data.sample(frac=0.1, random_state=0)

# get 10% of positive control features
positive_control_data_path = pathlib.Path("../1.idr_streams/extracted_features/positive_control_data/merged_features")
positive_control_data = compile_mitocheck_batch_data(positive_control_data_path)
positive_control_data = positive_control_data.sample(frac=0.1, random_state=0)

# combine negative and positive control features
control_data = pd.concat([negative_control_data, positive_control_data])
# shuffle data so negative/positive controls are not ordered
control_data = control_data.sample(frac=1, random_state=0)
control_data


# ### Create 2D umaps colored by metadata (with CP features)

# In[3]:


metadata_dataframe, feature_data = split_data(control_data, "CP")
x_data, y_data = get_2D_umap_embeddings(feature_data)

metadata_fields = ["Metadata_Plate", "Metadata_Well", "Metadata_Frame", "Metadata_Gene"]

for metadata_field in metadata_fields:
    metadata = metadata_dataframe[metadata_field]
    show_2D_umap_from_embeddings(x_data, y_data, metadata)


# ### Create 2D umaps colored by metadata (with DP features)

# In[4]:


metadata_dataframe, feature_data = split_data(control_data, "DP")
x_data, y_data = get_2D_umap_embeddings(feature_data)

metadata_fields = ["Metadata_Plate", "Metadata_Well", "Metadata_Frame", "Metadata_Gene"]

for metadata_field in metadata_fields:
    metadata = metadata_dataframe[metadata_field]
    show_2D_umap_from_embeddings(x_data, y_data, metadata)


# ### Create 2D umaps colored by metadata (with CP and DP features)

# In[5]:


metadata_dataframe, feature_data = split_data(control_data)
x_data, y_data = get_2D_umap_embeddings(feature_data)

metadata_fields = ["Metadata_Plate", "Metadata_Well", "Metadata_Frame", "Metadata_Gene"]

for metadata_field in metadata_fields:
    metadata = metadata_dataframe[metadata_field]
    show_2D_umap_from_embeddings(x_data, y_data, metadata)

