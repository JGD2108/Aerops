import pandas as pd 

def read_raw_data(file_path):
    """
    Reads raw data from a CSV file and returns a DataFrame.
    
    Parameters:
    file_path (str): The path to the CSV file containing the raw data.
    
    Returns:
    pd.DataFrame: A DataFrame containing the raw data.
    """
    try:
        raw_data = pd.read_csv(file_path)
        print(f"Successfully read raw data from {file_path}")
        return raw_data
    except Exception as e:
        print(f"Error reading raw data: {e}")
        return None
    
def status(df):
    if df["CANCELLED"] == 1:
        return "CANCELLED"
    if df["DEP_DELAY"] >= 15:
        return "DELAYED"
    if pd.notna(df["DEP_TIME"]):
        return "DEPARTED"
    return "SCHEDULED"

def normalize_time(value):
    if pd.isna(value):
        return None
    try:
        return str(int(float(value))).zfill(4)
    except ValueError:
        return None
    
def process_raw_data():
    airports_file = "./data/raw/airports.csv"
    airport_df = read_raw_data(airports_file)
    
    if airport_df is not None:
        #delete columns that have iata_code empty or null, because we will use iata_code as primary key to link with flights data
        airport_df = airport_df[airport_df['iata_code'].notna()]
        
        # type only int his 3 categories type en large_airport, medium_airport, small_airport, so we will filter out the other types
        airport_df = airport_df[airport_df['type'].isin(['large_airport', 'medium_airport', 'small_airport'])]
        
        # only save this columns iata_code, 
        airport_df = airport_df[['iata_code', 'icao_code', 'name', 'municipality', 'iso_country', 'latitude_deg', 'longitude_deg', 'type']]
        
        airport_df.rename(columns={'type': 'airport_type', 'iso_country': 'country', 'latitude_deg': 'latitude', 'longitude_deg': 'longitude'}, inplace=True)
        airport_df = airport_df[
            [
                "iata_code",
                "icao_code",
                "name",
                "municipality",
                "country",
                "latitude",
                "longitude",
                "airport_type",
            ]
        ]
        
    
    flights_file = "./data/raw/flights.csv"
    flights_df = read_raw_data(flights_file)
    if flights_df is not None:
        cols = [
            "FL_DATE",
            "OP_UNIQUE_CARRIER",
            "OP_CARRIER_FL_NUM",
            "ORIGIN",
            "DEST",
            "CRS_DEP_TIME"
                ]
        flights_df = flights_df.dropna(subset=cols)
        flights_df["FL_DATE"] = pd.to_datetime(flights_df["FL_DATE"]).dt.strftime("%Y-%m-%d")
        flights_df = flights_df.head(10000)
        
        flights_df["flight_id"] = (
            flights_df["FL_DATE"].astype(str) + "-" +
            flights_df["OP_UNIQUE_CARRIER"].astype(str) + "-" +
            flights_df["OP_CARRIER_FL_NUM"].astype(str) + "-" +
            flights_df["ORIGIN"].astype(str) + "-" +
            flights_df["DEST"].astype(str)
        )
        
        flights_df["status"] = flights_df.apply(status, axis=1)
        flights_df["scheduled_departure"] = flights_df["CRS_DEP_TIME"].apply(normalize_time)
        flights_df["actual_departure"] = flights_df["DEP_TIME"].apply(normalize_time)
        
        flights_df["flight_date"] = flights_df["FL_DATE"]
        flights_df["airline"] = flights_df["OP_UNIQUE_CARRIER"]
        flights_df["flight_number"] = flights_df["OP_CARRIER_FL_NUM"].astype(str)
        flights_df["origin"] = flights_df["ORIGIN"]
        flights_df["destination"] = flights_df["DEST"]
        flights_df["departure_delay_minutes"] = flights_df["DEP_DELAY"].fillna(0)
        flights_df["arrival_delay_minutes"] = flights_df["ARR_DELAY"].fillna(0)
        flights_df["cancelled"] = flights_df["CANCELLED"].fillna(0).astype(int).astype(bool)
        flights_df["diverted"] = False
        flights_df["distance"] = flights_df["DISTANCE"]
        flights_df["tail_number"] = flights_df["TAIL_NUM"].fillna("")
        
        
        flights_df = flights_df[
            [
                "flight_id",
                "flight_date",
                "airline",
                "flight_number",
                "origin",
                "destination",
                "scheduled_departure",
                "actual_departure",
                "departure_delay_minutes",
                "arrival_delay_minutes",
                "status",
                "cancelled",
                "diverted",
                "distance",
                "tail_number",
            ]
        ]
    
    if airport_df is None:
        raise FileNotFoundError(f"Required raw file not found or unreadable: {airports_file}")

    if flights_df is None:
        raise FileNotFoundError(f"Required raw file not found or unreadable: {flights_file}")

    # save both dataframes in processed folder
    airport_df.to_csv("./data/processed/airports_processed.csv", index=False)
    flights_df.to_csv("./data/processed/flights_processed.csv", index=False)
    print("Processed raw datasets successfully")


if __name__ == "__main__":
    process_raw_data()
