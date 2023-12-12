# Họ và Tên: Phạm Trần Gia Phú
# Ứng tuyển software engineer intern

import requests
import argparse
from datetime import datetime, timedelta
from typing import Dict
import json

class OfferFilter:
    def __init__(self, api_response: Dict, checkin_date: str):
        self.api_response = api_response
        self.checkin_date = checkin_date
        self.valid_categories = [1, 2, 4]
        self.valid_offers = []
        self.selected_offers = []

    def filter_offers(self):
        for offer in self.api_response['offers']:
            # Filter by category
            if offer['category'] not in self.valid_categories:
                continue
            # Filter by validity
            offer_valid_to = datetime.strptime(offer['valid_to'], '%Y-%m-%d')
            checkin_date = datetime.strptime(self.checkin_date, '%Y-%m-%d')
            if offer_valid_to < (checkin_date + timedelta(days=5)):
                continue
            self.valid_offers.append(offer)

        # Sort offers by distance
        self.valid_offers.sort(key=lambda x: x['merchants'][0]['distance'])

        # Select the closest offer from each category
        selected_categories = set()
        for offer in self.valid_offers:
            if offer['category'] not in selected_categories:
                selected_categories.add(offer['category'])
                self.selected_offers.append(offer)
                if len(selected_categories) == 2:
                    # delete one and keep a closest merchant
                    offer['merchants'].sort(key=lambda x:x['distance'])
                    del offer['merchants'][1]
                    break
    
    def get_selected_offers(self, output_file):
        output_data = {'offers': self.selected_offers}
        with open(output_file, 'w') as file:
            json.dump(output_data, file, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Filter and save offers based on certain criteria.')
    parser.add_argument('checkin_date', type=str, help='Customer check-in date in the format YYYY-MM-DD')
    args = parser.parse_args()

    response = requests.get('https://61c3deadf1af4a0017d990e7.mockapi.io/offers/near_by?lat=1.313492&lon=103.860359&rad=20').json()
    output_file = 'output.json'

    offer_filter = OfferFilter(response, checkin_date=args.checkin_date)
    offer_filter.filter_offers()
    offer_filter.get_selected_offers(output_file)

    print(f'Selected offers saved to {output_file}')
