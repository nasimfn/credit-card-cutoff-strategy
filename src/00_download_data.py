"""
Step 0: Download the data.

Dataset: Default of Credit Card Clients (Yeh & Lien, 2009), UCI Machine Learning Repository,
https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients
30,000 credit card clients in Taiwan, April-September 2005.

This script downloads a CSV copy of the UCI data from a public GitHub repository
(MatteoM95/Default-of-Credit-Card-Clients-Dataset-Analisys). It is a copy, not the UCI
file itself. Its row count (30,000), column count (25 including ID and the target) and
codebook agree with UCI's description, but it was not compared value-by-value with the UCI
file. You can also place the UCI file, saved as CSV with the same name, in data/raw/.
"""
from pathlib import Path
import urllib.request

URL = ("https://raw.githubusercontent.com/MatteoM95/Default-of-Credit-Card-Clients-Dataset-Analisys/"
       "main/dataset/default_of_credit_card_clients.csv")
DEST = Path("data/raw/default_of_credit_card_clients.csv")

if __name__ == "__main__":
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if DEST.exists():
        print(f"already have {DEST}")
    else:
        print(f"downloading {DEST.name} ...")
        urllib.request.urlretrieve(URL, DEST)
    print("Done.")
