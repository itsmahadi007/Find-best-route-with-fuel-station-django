import pandas as pd
from opencage.geocoder import OpenCageGeocode
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

load_dotenv()

# Initialize OpenCage Geocoder with API key
key = os.getenv('GEO_KEY')
geocoder = OpenCageGeocode(key)

# Function to geocode an address
def geocode_address(address):
    try:
        result = geocoder.geocode(address)
        if result:
            return result[0]['geometry']['lat'], result[0]['geometry']['lng']
        else:
            return None, None
    except Exception as e:
        print(str(e))
        return None, None

# Function to get the last processed index
def get_last_processed_index():
    if os.path.exists('progress.txt'):
        with open('progress.txt', 'r') as f:
            return int(f.read().strip())
    return 0

# Function to save the last processed index
def save_progress(index):
    with open('progress.txt', 'w') as f:
        f.write(str(index))

# Load the CSV file into a DataFrame
df = pd.read_csv('fuel_stations_without_geocodes.csv')

# Get the index to resume from
start_index = get_last_processed_index()

# Filter the DataFrame to get rows where Latitude or Longitude is missing, and index >= start_index
df_to_process = df[(df['Latitude'].isnull() | df['Longitude'].isnull()) & (df.index >= start_index)]

# Now process in chunks
chunk_size = 100  # You can adjust this as needed
indices = df_to_process.index.tolist()

# Divide indices into chunks
chunks = [indices[i:i + chunk_size] for i in range(0, len(indices), chunk_size)]

for chunk_num, chunk_indices in enumerate(chunks, start=1):
    print(f"Processing chunk {chunk_num}/{len(chunks)}")
    chunk_df = df.loc[chunk_indices].copy()
    
    addresses = chunk_df['FullAddress'].tolist()
    indices = chunk_indices
    
    success = True
    processed_indices = []
    with ThreadPoolExecutor() as executor:
        future_to_index = {executor.submit(geocode_address, addr): idx for addr, idx in zip(addresses, indices)}
        try:
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                lat, lon = future.result()
                if lat is None or lon is None:
                    print(f"Geocoding failed for index {idx}. Stopping the process.")
                    success = False
                    break
                else:
                    df.at[idx, 'Latitude'] = lat
                    df.at[idx, 'Longitude'] = lon
                    processed_indices.append(idx)
        except Exception as e:
            print(f"An error occurred: {e}")
            success = False
            break
    if not success:
        # Save progress up to the last successfully processed index
        if processed_indices:
            last_processed_index = max(processed_indices)
            save_progress(last_processed_index + 1)  # Next index to start from
            df.to_csv('fuel_stations_without_geocodes.csv', index=False)
        else:
            # No indices processed in this chunk
            save_progress(chunk_indices[0])  # Next index to start from
        exit()
    else:
        # Update progress
        last_processed_index = chunk_indices[-1]
        save_progress(last_processed_index + 1)  # Next index to start from
        df.to_csv('fuel_stations_without_geocodes.csv', index=False)
        print(f"Chunk {chunk_num} processed and saved.")

# Remove the progress file if processing is complete
if os.path.exists('progress.txt'):
    os.remove('progress.txt')

print("Geocoding and saving completed.")


"""
Used https://opencagedata.com/ to have the latitude and longitude for the fuel stations.
"""