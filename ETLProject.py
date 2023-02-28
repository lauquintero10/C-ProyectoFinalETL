#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import gcsfs


# In[ ]:


from googleplaces import GooglePlaces, types, lang
YOUR_API_KEY = '*****************************'


# In[ ]:


google_places = GooglePlaces(YOUR_API_KEY)
from google.cloud import storage
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="etl-project-370513-***********.json"


# In[ ]:


df = pd.read_csv('gs://provided-table/subway.csv')

#hicimos el subset para una prueba de concepto y despues ejecutamos para todo, devido al uso de la version gratuita de la API de google
df_sample1 = df[df["city"]=="Alexandria"]
df_sample1.to_csv('df_sample1.csv', index = False)


# In[ ]:


#función para extrair los dados de la API por lat y long e guardar en un dataframe
def search_locations(data):

    locations_final = pd.DataFrame(columns=['business_status', 'icon', 'icon_background_color',
    'icon_mask_base_uri', 'name', 'photos', 'place_id', 'rating',
    'reference', 'scope', 'types', 'user_ratings_total', 'vicinity',
    'geometry.location.lat', 'geometry.location.lng',
    'geometry.viewport.northeast.lat', 'geometry.viewport.northeast.lng',
    'geometry.viewport.southwest.lat', 'geometry.viewport.southwest.lng',
    'opening_hours.open_now', 'plus_code.compound_code',
    'plus_code.global_code', 'lat_ref', 'long_ref'])

    for i in range(len(data)):

        query_result = google_places.nearby_search(
            lat_lng={'lat': data['latitude'].iloc[i], 'lng': data['longitude'].iloc[i]}, 
            keyword='business',
            radius=2000, 
            types=[types.TYPE_FOOD])

        result = query_result.raw_response

        locations = pd.json_normalize(result, record_path =['results'])
        locations["lat_ref"]=data['latitude'].iloc[i]
        locations["long_ref"]=data['longitude'].iloc[i]

        locations_final=pd.concat([locations,locations_final])

    return(locations_final)


result_api_google = search_locations(df)

result_api_google.shape


# In[ ]:


# guardando el cvs
result_api_google.to_csv('result_api_google.csv', index = False)


# In[ ]:


# guargar en google cloud storage
bucket_name = 'etl_raw_data' 
local_path = 'result_api_google.csv' 
blob_path = datetime.today().strftime('%Y-%m-%d') + '/data/' + local_path

bucket = storage.Client(project='etl-project-370513').bucket(bucket_name)
blob = bucket.blob(blob_path)
blob.upload_from_filename(local_path)


# In[ ]:




