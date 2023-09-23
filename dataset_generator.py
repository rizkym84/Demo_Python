import pandas as pd
import random
from faker import Faker

# Create a random number generator
fake = Faker()

# Function to generate a fake credit card number


def generate_credit_card_number(card_type):
    if card_type == 'credit':
        # Generate a fake credit card number format
        card_number = '4' + ''.join(str(random.randint(0, 9))
                                    for _ in range(15))
    elif card_type == 'debit':
        # Generate a fake debit card number format
        card_number = '5' + ''.join(str(random.randint(0, 9))
                                    for _ in range(15))
    else:
        raise ValueError("Invalid card type")
    return card_number


# Define the number of rows in the dataset
num_samples = 1000

# Create empty lists to store data
transaction_amounts = []
transaction_dates = []
merchant_ids = []
customer_ids = []
transaction_types = []
locations = []
card_types = []
card_numbers = []
is_fraud = []

# Generate synthetic data
for _ in range(num_samples):
    transaction_amounts.append(round(random.uniform(10.0, 1000.0), 2))
    # Generate a fake date and time
    transaction_dates.append(fake.date_time_between(
        start_date='-1y', end_date='now'))
    merchant_ids.append(fake.uuid4())
    customer_ids.append(fake.uuid4())
    transaction_types.append(random.choice(['purchase', 'refund', 'transfer']))
    locations.append(fake.city())
    card_type = random.choice(['credit', 'debit'])
    card_types.append(card_type)
    card_numbers.append(generate_credit_card_number(card_type))
    is_fraud.append(random.choice([0, 1]))

# Create a DataFrame
data = {
    'transaction_amount': transaction_amounts,
    'transaction_date': transaction_dates,  # Keep dates as strings for now
    'merchant_id': merchant_ids,
    'customer_id': customer_ids,
    'transaction_type': transaction_types,
    'location': locations,
    'card_type': card_types,
    'card_number': card_numbers,
    'is_fraud': is_fraud
}

df = pd.DataFrame(data)

# Convert 'transaction_date' column to datetime
df['transaction_date'] = pd.to_datetime(df['transaction_date'])

# Save the DataFrame to a CSV file
df.to_csv('credit_card_transactions.csv', index=False)
