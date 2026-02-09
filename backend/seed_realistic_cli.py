#!/usr/bin/env python3
"""CLI to seed realistic test data for Crowd Pulse."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.append(str(Path(__file__).parent))

from app.seed_realistic import seed_realistic_data

def main():
    parser = argparse.ArgumentParser(description="Seed realistic test data for Crowd Pulse")
    parser.add_argument("--days", type=int, default=7, help="Number of days of data to generate")
    parser.add_argument("--posts", type=int, default=40, help="Posts per symbol per day")
    parser.add_argument("--source", type=str, default="test", choices=["test", "live"], 
                       help="Data source (test or live)")
    
    args = parser.parse_args()
    
    print(f"Seeding realistic data: {args.days} days, {args.posts} posts/day, source={args.source}")
    
    try:
        seed_realistic_data(
            num_days=args.days,
            posts_per_symbol_per_day=args.posts,
            data_source=args.source
        )
        print("✅ Realistic seed data created successfully!")
    except Exception as e:
        print(f"❌ Failed to seed data: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
