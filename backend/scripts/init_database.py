"""
Database initialization script.

Creates all tables with ea_ prefix in the remote database.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine
from models.base import Base
from models.user import User, UserSettings, APICredit
from models.analysis import Analysis, ErrorDetail, Tag, AnalysisTag, AnalysisCache
from core.config import settings


def init_database():
    """Initialize database with all tables."""
    print("🚀 Starting database initialization...")

    # URL-encode the password for special characters
    db_url = "postgresql://english_assistant:NHb475%26%23g@110.40.137.26:5432/db_english_assistant"

    print(f"📡 Connecting to database...")
    engine = create_engine(db_url, echo=True)

    print("\n📋 Creating tables with ea_ prefix:")
    print("  - ea_users")
    print("  - ea_user_settings")
    print("  - ea_api_credits")
    print("  - ea_analyses")
    print("  - ea_error_details")
    print("  - ea_tags")
    print("  - ea_analysis_tags")
    print("  - ea_analysis_cache")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print("\n✅ Database initialization completed successfully!")
    print("\nCreated tables:")

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    for table in sorted(tables):
        if table.startswith('ea_'):
            print(f"  ✓ {table}")

    engine.dispose()
    print("\n🎉 All done! Database is ready to use.")


if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
