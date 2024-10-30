import pandas as pd

def format_and_clean_address(df):
    # Combine address components into 'FullAddress'
    df['FullAddress'] = df['Address'] + ', ' + df['City'] + ', ' + df['State']
    
    # Clean the 'FullAddress' column
    df['FullAddress'] = df['FullAddress'].str.strip()  # Remove leading and trailing whitespaces
    df['FullAddress'] = df['FullAddress'].str.replace(r'\s{2,}', ' ', regex=True)  # Replace multiple spaces with single spaces
    
    # Set Latitude and Longitude to empty values initially
    df['Latitude'] = ''
    df['Longitude'] = ''

    return df


fuel_prices_df = pd.read_csv('./fuel-prices-for-be-assessment.csv')

# Format and clean the 'FullAddress' column
fuel_prices_df = format_and_clean_address(fuel_prices_df)

# Save the updated DataFrame to a new CSV without geocoordinates
fuel_prices_df.to_csv('./fuel_stations_without_geocodes.csv', index=False)

print("Data converted and saved without latitude and longitude.")
