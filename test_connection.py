import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from config import settings

async def test_basic_connection():
    """Test basic database connection"""
    print("Testing basic database connection...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,  # Set to False in production
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        pool_timeout=settings.POOL_TIMEOUT,
        pool_recycle=settings.POOL_RECYCLE
    )
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            print("✅ Basic connection successful!")
            print(f"Test result: {row}")
            return True
    except Exception as e:
        print(f"❌ Basic connection failed: {e}")
        return False
    finally:
        await engine.dispose()

async def test_database_info():
    """Test database information queries"""
    print("\nTesting database information queries...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # Test database version
            result = await conn.execute(text("SELECT VERSION() as version"))
            version = result.fetchone()
            print(f"✅ Database version: {version[0]}")
            
            # Test current database
            result = await conn.execute(text("SELECT DATABASE() as current_db"))
            current_db = result.fetchone()
            print(f"✅ Current database: {current_db[0]}")
            
            # Test current user
            result = await conn.execute(text("SELECT USER() as current_user"))
            current_user = result.fetchone()
            print(f"✅ Current user: {current_user[0]}")
            
            # Test current time
            result = await conn.execute(text("SELECT NOW() as current_time"))
            current_time = result.fetchone()
            print(f"✅ Current time: {current_time[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Database info queries failed: {e}")
        return False
    finally:
        await engine.dispose()

async def test_table_operations():
    """Test table creation and operations"""
    print("\nTesting table operations...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # Drop table if exists
            await conn.execute(text("DROP TABLE IF EXISTS test_table"))
            print("✅ Dropped existing test table")
            
            # Create table
            await conn.execute(text("""
                CREATE TABLE test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Created test table")
            
            # Insert data
            await conn.execute(text("""
                INSERT INTO test_table (name) VALUES 
                ('Test User 1'), ('Test User 2'), ('Test User 3')
            """))
            print("✅ Inserted test data")
            
            # Select data
            result = await conn.execute(text("SELECT * FROM test_table"))
            rows = result.fetchall()
            print(f"✅ Retrieved {len(rows)} rows:")
            for row in rows:
                print(f"  - ID: {row[0]}, Name: {row[1]}, Created: {row[2]}")
            
            # Clean up
            await conn.execute(text("DROP TABLE test_table"))
            print("✅ Cleaned up test table")
            
            return True
    except Exception as e:
        print(f"❌ Table operations failed: {e}")
        return False
    finally:
        await engine.dispose()

async def test_session_operations():
    """Test SQLAlchemy session operations"""
    print("\nTesting session operations...")
    
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    try:
        async with async_session() as session:
            # Test session query
            result = await session.execute(text("SELECT 1 as test, 'session' as type"))
            row = result.fetchone()
            print(f"✅ Session query successful: {row}")
            
            # Test transaction
            async with session.begin():
                await session.execute(text("SELECT 'transaction test' as test"))
                print("✅ Transaction test successful")
            
            return True
    except Exception as e:
        print(f"❌ Session operations failed: {e}")
        return False
    finally:
        await engine.dispose()

async def test_connection_pool():
    """Test connection pool behavior"""
    print("\nTesting connection pool...")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=2,
        max_overflow=3
    )
    
    try:
        # Test multiple concurrent connections
        async def query_task(task_id):
            async with engine.begin() as conn:
                result = await conn.execute(text(f"SELECT {task_id} as task_id, CONNECTION_ID() as conn_id"))
                row = result.fetchone()
                print(f"✅ Task {task_id} - Connection ID: {row[1]}")
                await asyncio.sleep(0.1)  # Simulate work
                return row
        
        # Run multiple tasks concurrently
        tasks = [query_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        print(f"✅ Successfully handled {len(results)} concurrent connections")
        
        return True
    except Exception as e:
        print(f"❌ Connection pool test failed: {e}")
        return False
    finally:
        await engine.dispose()

async def main():
    """Run all tests"""
    print("=== Aiven MySQL Database Connection Tests ===")
    print(f"Database URL: {settings.DATABASE_URL.replace(settings.DB_PASSWORD, '***')}")
    print(f"Host: {settings.DB_HOST}:{settings.DB_PORT}")
    print(f"Database: {settings.DB_NAME}")
    print(f"User: {settings.DB_USER}")
    print("=" * 50)
    
    tests = [
        ("Basic Connection", test_basic_connection),
        ("Database Info", test_database_info),
        ("Table Operations", test_table_operations),
        ("Session Operations", test_session_operations),
        ("Connection Pool", test_connection_pool),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        try:
            success = await test_func()
            if success:
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                failed += 1
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Your database connection is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())