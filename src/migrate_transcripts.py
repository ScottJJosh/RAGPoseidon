#!/usr/bin/env python3
"""
Migration script to reorganize transcripts into new folder structure.

Old: transcripts/*.txt
New: transcripts/industry/company/quarter_year.txt
"""

import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

import shutil
import re
import config


def get_company_industry(company: str) -> str:
    """Map company to industry.

    Add your company-to-industry mappings here.
    """
    industry_map = {
        'CVS': 'Healthcare',
        'DVA': 'Healthcare',
        # Add more mappings as needed
    }
    return industry_map.get(company, 'Unknown')


def parse_old_filename(filename: str) -> dict:
    """Parse old filename format to extract metadata.

    Examples:
        cvs_Q3.txt -> company=CVS, quarter=Q3, year=2024 (assumed)
        dva_Q32024.txt -> company=DVA, quarter=Q3, year=2024
        dva_Q4_2024.txt -> company=DVA, quarter=Q4, year=2024
    """
    # Remove .txt extension
    name = filename.replace('.txt', '')

    # Try different patterns
    patterns = [
        r'^([a-z]+)_Q([1-4])(\d{4})$',  # dva_Q32024
        r'^([a-z]+)_Q([1-4])_(\d{4})$',  # dva_Q4_2024
        r'^([a-z]+)_Q([1-4])$',          # cvs_Q3 (assume 2024)
    ]

    for pattern in patterns:
        match = re.match(pattern, name, re.IGNORECASE)
        if match:
            company = match.group(1).upper()
            quarter = match.group(2)
            year = match.group(3) if len(match.groups()) == 3 else '2024'

            return {
                'company': company,
                'quarter': f'Q{quarter}',
                'year': year,
                'industry': get_company_industry(company)
            }

    return None


def migrate_transcripts(source_dir: Path = None, backup: bool = True):
    """Migrate transcripts to new folder structure.

    Args:
        source_dir: Source directory containing transcripts (Path object or None for config default)
        backup: Whether to create a backup before migration
    """
    # Use config default if not provided
    if source_dir is None:
        source_path = config.TRANSCRIPTS_DIR
    else:
        source_path = Path(source_dir) if not isinstance(source_dir, Path) else source_dir

    if not source_path.exists():
        print(f"Error: {source_dir} directory not found")
        return

    # Create backup if requested
    if backup:
        backup_dir = Path(f"{source_dir}_backup")
        if backup_dir.exists():
            print(f"Backup already exists at {backup_dir}")
            response = input("Overwrite backup? (y/n): ")
            if response.lower() != 'y':
                print("Migration cancelled")
                return
            shutil.rmtree(backup_dir)

        shutil.copytree(source_path, backup_dir)
        print(f"✓ Created backup at {backup_dir}")

    # Find all .txt files in root of transcripts directory
    txt_files = [f for f in source_path.glob('*.txt') if f.is_file()]

    if not txt_files:
        print("No .txt files found in root of transcripts directory")
        return

    print(f"\nFound {len(txt_files)} transcript files to migrate:\n")

    migrations = []
    for txt_file in txt_files:
        metadata = parse_old_filename(txt_file.name)

        if not metadata:
            print(f"⚠ Skipping {txt_file.name} - could not parse filename")
            continue

        # Build new path: transcripts/industry/company/Q#_YEAR.txt
        new_path = source_path / metadata['industry'] / metadata['company'] / f"{metadata['quarter']}_{metadata['year']}.txt"

        migrations.append({
            'old': txt_file,
            'new': new_path,
            'metadata': metadata
        })

        print(f"{txt_file.name}")
        print(f"  → {metadata['industry']}/{metadata['company']}/{metadata['quarter']}_{metadata['year']}.txt")
        print()

    if not migrations:
        print("No files to migrate")
        return

    # Confirm migration
    response = input(f"\nMigrate {len(migrations)} files? (y/n): ")
    if response.lower() != 'y':
        print("Migration cancelled")
        return

    # Perform migration
    for migration in migrations:
        old_path = migration['old']
        new_path = migration['new']

        # Create directory structure
        new_path.parent.mkdir(parents=True, exist_ok=True)

        # Move file
        shutil.move(str(old_path), str(new_path))
        print(f"✓ Moved {old_path.name} → {new_path.relative_to(source_path)}")

    print(f"\n✓ Migration complete! Migrated {len(migrations)} files")
    print(f"\nNew structure:")
    print(f"  transcripts/")

    # Show directory tree
    for industry in sorted(set(m['metadata']['industry'] for m in migrations)):
        print(f"    {industry}/")
        for company in sorted(set(m['metadata']['company'] for m in migrations if m['metadata']['industry'] == industry)):
            print(f"      {company}/")
            for m in migrations:
                if m['metadata']['industry'] == industry and m['metadata']['company'] == company:
                    print(f"        {m['new'].name}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Migrate transcripts to new folder structure')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--dir', type=str, default=None,
                       help=f'Transcripts directory (default: {config.TRANSCRIPTS_DIR})')
    args = parser.parse_args()

    source_dir = Path(args.dir) if args.dir else None
    migrate_transcripts(source_dir=source_dir, backup=not args.no_backup)
