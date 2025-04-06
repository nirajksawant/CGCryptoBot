# test_announcement_parser.py

from announcement_parser import parse_announcement_page

# Example Binance announcement
TEST_URL = "https://www.binance.com/en/support/announcement/abc123-sample-url"

if __name__ == "__main__":
    parsed_data = parse_announcement_page(TEST_URL)
    print("📄 Extracted Info:")
    for key, val in parsed_data.items():
        print(f"{key}: {val}")
