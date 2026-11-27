"""Command-line entry point for the FitDesk enquiry assistant."""
import argparse
import os

from dotenv import load_dotenv

from fitdesk.app import process_enquiry

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="FitDesk enquiry assistant")
    parser.add_argument("message", nargs="?", help="customer message (prompted if omitted)")
    args = parser.parse_args()
    message = args.message or input("Customer message: ")
    process_enquiry(
        message,
        data_path=os.path.join(HERE, "data", "fitdesk_data.json"),
        log_path=os.path.join(HERE, "status_log.json"),
    )


if __name__ == "__main__":
    main()
