from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_synthetic_data(num_records=1000):
    fake = Faker()
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    Faker.seed(42)
    
    # Generate unique values for ID columns based on specified counts
    customers = [f"CUST_{i:03d}" for i in range(5)]
    app_ids = [f"APP_{i:03d}" for i in range(10)]
    os_types = ["Android", "iOS", "Windows"]
    build_identifiers = [f"BUILD_{i:03d}" for i in range(15)]
    
    # Use faker for country names and timezones
    unique_countries = list(set([fake.country() for _ in range(20)]))[:20]
    unique_timezones = list(set([fake.timezone() for _ in range(25)]))[:25]
    
    # Generate the main DataFrame
    data = {
        'CUSTOMERID': [random.choice(customers) for _ in range(num_records)],
        'APPID': [random.choice(app_ids) for _ in range(num_records)],
        'OS': [random.choice(os_types) for _ in range(num_records)],
        'PROTECTEDBUILDIDENTIFIER': [random.choice(build_identifiers) for _ in range(num_records)],
        'GEOIP_COUNTRYNAME': [random.choice(unique_countries) for _ in range(num_records)],
        'GEOIP_TZ': [random.choice(unique_timezones) for _ in range(num_records)],
    }
    
    # Generate hour data for the last 24 hours
    current_time = datetime.now()
    hours = [(current_time - timedelta(hours=x)).strftime('%Y-%m-%d %H:00:00') 
             for x in range(24)]
    
    data['INGESTTIME_HOUR'] = [random.choice(hours) for _ in range(num_records)]
    
    # Generate count columns with realistic distributions
    count_columns = [
        'COUNT_APPLICATIONFIRSTRUN',
        'COUNT_ROOTINGDETECTED',
        'COUNT_DEBUGGERDETECTED',
        'COUNT_OVERLAYDETECTED',
        'COUNT_APPLICATIONOPENED',
        'COUNT_BOOTLOADERUNLOCKDETECTED',
        'COUNT_TAMPERINGDETECTED',
        'COUNT_HOOKINGDETECTED',
        'COUNT_GENERICINFORMATIONUPDATE',
        'COUNT_EMULATORDETECTED'
    ]
    
    # Generate count data with different distributions for each type
    for column in count_columns:
        if 'APPLICATIONFIRSTRUN' in column or 'APPLICATIONOPENED' in column:
            # More common events - higher counts
            data[column] = np.random.poisson(lam=5, size=num_records)
        elif 'GENERICINFORMATIONUPDATE' in column:
            # Medium frequency events
            data[column] = np.random.poisson(lam=2, size=num_records)
        else:
            # Security events - should be rare
            data[column] = np.random.binomial(n=1, p=0.05, size=num_records)
    
    data["IS_ANOMALY"] = np.random.binomial(1, 0.05, num_records)

    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Verify unique counts
    unique_counts = {
        'CUSTOMERID': 5,
        'APPID': 10,
        'OS': 3,
        'PROTECTEDBUILDIDENTIFIER': 15,
        'GEOIP_COUNTRYNAME': 20,
        'GEOIP_TZ': 25
    }
    
    # Print validation of unique counts
    print("\nUnique value counts verification:")
    for col, expected_count in unique_counts.items():
        actual_count = df[col].nunique()
        print(f"{col}: Expected {expected_count}, Got {actual_count}")
    
    return df

# Generate sample data
if __name__ == "__main__":
    # Generate 1000 records
    df = generate_synthetic_data(1000)
    
    # Display first few rows and basic statistics
    print("\nFirst few rows of the generated data:")
    print(df.head())
    
    print("\nBasic statistics of count columns:")
    count_columns = [col for col in df.columns if col.startswith('COUNT_')]
    print(df[count_columns].describe())
    
    # Save to CSV (optional)
    df.to_csv('synthetic_security_data.csv', index=False)
    print("\nData saved to 'synthetic_security_data.csv'")