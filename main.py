import sqlite3
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

NUM_CUSTOMERS = 1000

# 1. Generate Customers Data
plans = ['Basic', 'Pro', 'Enterprise']
plan_prices = {'Basic': 29, 'Pro': 99, 'Enterprise': 299}
regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America']
acquisition_channels = ['Organic Search', 'Paid Ads', 'Referral', 'Outreach']

customers = []
start_date = datetime(2024, 1, 1)

for i in range(1, NUM_CUSTOMERS + 1):
  signup_offset = random.randint(0, 500)
  created_at = start_date + timedelta(days=signup_offset)
  region = random.choice(regions)
  channel = random.choice(acquisition_channels)

  customers.append({
      'customer_id': f'CUST-{i:04d}',
      'created_at': created_at.strftime('%Y-%m-%d'),
      'region': region,
      'acquisition_channel': channel,
  })

df_customers = pd.DataFrame(customers)

# 2. Generate Subscriptions & Events
subscriptions = []
payment_logs = []

for idx, cust in df_customers.iterrows():
  cust_id = cust['customer_id']
  signup_dt = datetime.strptime(cust['created_at'], '%Y-%m-%d')

  current_plan = random.choices(plans, weights=[0.5, 0.35, 0.15])[0]
  mrr = plan_prices[current_plan]

  # Decide if customer churned
  churned = random.random() < 0.25  # 25% overall churn
  if churned:
    tenure_months = random.randint(1, 12)
    end_dt = signup_dt + timedelta(days=tenure_months * 30)
    status = 'Cancelled'
  else:
    end_dt = datetime(2026, 6, 30)  # Active
    status = 'Active'

  subscriptions.append({
      'subscription_id': f'SUB-{idx+1:04d}',
      'customer_id': cust_id,
      'plan_type': current_plan,
      'monthly_revenue': mrr,
      'status': status,
      'start_date': signup_dt.strftime('%Y-%m-%d'),
      'end_date': (
          end_dt.strftime('%Y-%m-%d') if status == 'Cancelled' else None
      ),
  })

  # Generate Monthly Payment Logs
  curr_payment_dt = signup_dt
  while curr_payment_dt <= min(end_dt, datetime(2026, 6, 30)):
    payment_logs.append({
        'payment_id': f'PAY-{len(payment_logs)+1:06d}',
        'customer_id': cust_id,
        'payment_date': curr_payment_dt.strftime('%Y-%m-%d'),
        'amount': mrr,
        'status': 'Success' if random.random() > 0.03 else 'Failed',
    })
    curr_payment_dt += timedelta(days=30)

df_subscriptions = pd.DataFrame(subscriptions)
df_payments = pd.DataFrame(payment_logs)

# Export to CSV Files
df_customers.to_csv('customers.csv', index=False)
df_subscriptions.to_csv('subscriptions.csv', index=False)
df_payments.to_csv('payment_logs.csv', index=False)

# Export directly to SQLite Database file for DBeaver
conn = sqlite3.connect('saas_data.db')
df_customers.to_sql('customers', conn, if_exists='replace', index=False)
df_subscriptions.to_sql('subscriptions', conn, if_exists='replace', index=False)
df_payments.to_sql('payment_logs', conn, if_exists='replace', index=False)
conn.close()

print('✅ Success! CSVs and saas_data.db have been generated in your folder.')

