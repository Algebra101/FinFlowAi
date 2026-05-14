import csv
import random
from datetime import datetime, timedelta

# Create 20 synthetic SME users
smes = [f"SME_USER_{i:03d}" for i in range(1, 21)]
banks_list = ["GTBank", "First Bank", "OPay", "PalmPay", "Squad Virtual Account"]

narrations_credit = ["Squad Settlement", "POS Transfer", "Invoice Payment", "NIP Transfer from GTB", "Vendor Credit", "", "TRF/REV/992"]
narrations_debit = ["Ikeja Electric", "Payroll", "Supplier Payment", "AWS Hosting", "Logistics", "Tax Remittance", "NIP/TRF/0000", ""]

file_name = "sme_training_data.csv"

with open(file_name, "w", newline="") as f:
    writer = csv.writer(f)
    # Added "sme_id" so your teammate can group multiple banks to one user!
    writer.writerow(["sme_id", "account_id", "bank_name", "date", "transaction_type", "amount", "narration", "balance", "is_fraud"])
    
    for sme in smes:
        # Each SME has 2 to 4 different bank accounts linked to their BVN
        num_accounts = random.randint(2, 4)
        sme_banks = random.sample(banks_list, num_accounts)
        
        for bank_name in sme_banks:
            account_id = f"{sme}_{bank_name.replace(' ', '_').upper()}"
            balance = random.randint(50000, 300000) 
            current_date = datetime.now() - timedelta(days=180) 
            
            # Generate 50 to 150 transactions per bank account
            for _ in range(random.randint(50, 150)): 
                current_date += timedelta(hours=random.randint(5, 48))
                is_fraud = 0
                
                if random.random() < 0.02:
                    is_fraud = 1
                    t_type = "Debit"
                    amount = balance * 0.95 
                    narration = "Unknown Crypto Transfer"
                else:
                    t_type = random.choices(["Credit", "Debit"], weights=[0.6, 0.4])[0]
                    if t_type == "Credit":
                        amount = random.randint(10000, 150000)
                        narration = random.choice(narrations_credit)
                    else:
                        amount = random.randint(5000, 80000)
                        if amount > balance: amount = balance
                        narration = random.choice(narrations_debit)
                        
                if t_type == "Credit":
                    balance += amount
                else:
                    balance -= amount
                    
                writer.writerow([
                    sme,
                    account_id, 
                    bank_name,
                    current_date.strftime("%Y-%m-%d %H:%M:%S"), 
                    t_type, 
                    round(amount, 2), 
                    narration, 
                    round(balance, 2), 
                    is_fraud
                ])

print(f" Successfully generated {file_name} with multi-bank aggregation!")
