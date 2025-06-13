from db import create_pueblos_table, load_pharmacies_from_csv

def setup_database():
    print("Creating pueblos table...")
    create_pueblos_table()
    
    print("Loading pharmacy data from CSV...")
    load_pharmacies_from_csv()
    
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database() 