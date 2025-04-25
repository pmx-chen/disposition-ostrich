# %%
import pandas as pd
import os
from pathlib import Path

# Define data directories using forward slashes
data_dir = {
    'stock_price_returns': 'C:/Users/pequa/Dropbox (Personal)/Research/my-project-shared/disposition-learning/src/data/Daily Stock Price Returns',
    'stock_price_returns_combined': 'C:/Users/pequa/Dropbox (Personal)/Research/my-project-shared/disposition-learning/src/data/Daily Stock Price Returns/combined_stock_data.csv'
}

def read_stock_data(file_path):
    """
    Read stock data file
    """
    # Define column names
    columns = [
        'Stkcd', 'Trddt', 'Trdsta', 'Opnprc', 'Hiprc', 'Loprc', 'Clsprc',
        'Dnshrtrd', 'Dnvaltrd', 'Dsmvosd', 'Dsmvtll', 'Dretwd', 'Dretnd',
        'Adjprcwd', 'Adjprcnd', 'Markettype', 'Capchgdt', 'Ahshrtrd_D',
        'Ahvaltrd_D', 'PreClosePrice', 'ChangeRatio', 'LimitDown', 'LimitUp',
        'LimitStatus'
    ]
    
    print(f"Reading file: {file_path}")
    
    # Read data, always skip the header row
    df = pd.read_csv(file_path, sep='\t', names=columns, skiprows=1)
    
    return df

def main():
    # Get data file path
    data_dir_path = Path(data_dir['stock_price_returns'])
    print(f"Looking for files in: {data_dir_path}")
    
    # Read all data files
    all_data = []
    
    for file in data_dir_path.glob('TRD_Dalyr*.txt'):
        print(file.name)
        if '[DES]' not in file.name:  # Skip description file
            try:
                df = read_stock_data(file)
                all_data.append(df)
                print(f"Successfully read {len(df)} rows from {file.name}")
            except Exception as e:
                print(f"Error reading {file.name}: {str(e)}")
    
    # Merge all data
    if all_data:
        combined_data = pd.concat(all_data, ignore_index=True)
        print(f'\nTotal number of rows: {len(combined_data)}')
        print('\nData preview:')
        print(combined_data.head())
        
        # Save combined data with a single header row
        output_path = data_dir['stock_price_returns_combined']
        combined_data.to_csv(output_path, index=False)
        print(f'\nCombined data saved to: {output_path}')
        
        # Verify the output file
        print("\nVerifying output file...")
        verification_df = pd.read_csv(output_path)
        print(f"Number of rows in output file: {len(verification_df)}")
        print("First few rows of output file:")
        print(verification_df.head())

        return verification_df
    
    else:
        print('No data files found')

if __name__ == '__main__':
    main()

    
# %%
