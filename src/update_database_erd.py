#!/usr/bin/env python3
"""
Script để cập nhật database theo ERD mới
Chạy script này để đồng bộ database với model Ticket đã được cập nhật
"""

from infrastructure.databases.mssql import engine
from infrastructure.databases.base import Base
from infrastructure.models.Ticket_model import TicketModel
from infrastructure.models.user_model import UserModel
from sqlalchemy import text

def update_database_to_erd():
    """
    Cập nhật database để phù hợp với ERD mới
    """
    print("🔄 Bắt đầu cập nhật database theo ERD mới...")
    
    try:
        # Kiểm tra xem bảng ticket có tồn tại không (SQL Server syntax)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'ticket'"))
            table_exists = result.fetchone() is not None
            
            if table_exists:
                print("📋 Bảng 'ticket' đã tồn tại, kiểm tra cấu trúc...")
                
                # Kiểm tra các cột hiện tại (SQL Server syntax)
                result = conn.execute(text("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'ticket'"))
                existing_columns = {row[0] for row in result.fetchall()}
                print(f"📊 Các cột hiện tại: {existing_columns}")
                
                # Các cột cần thiết theo ERD
                required_columns = {
                    'TicketID': 'INT IDENTITY(1,1) PRIMARY KEY',
                    'EventDate': 'DATETIME NOT NULL',
                    'Price': 'FLOAT NOT NULL',
                    'EventName': 'NVARCHAR(100) NOT NULL',
                    'Status': 'NVARCHAR(20) DEFAULT N\'Available\'',
                    'PaymentMethod': 'NVARCHAR(100) NOT NULL DEFAULT N\'Cash\'',
                    'ContactInfo': 'NVARCHAR(200) NOT NULL DEFAULT N\'Contact information required\'',
                    'OwnerID': 'INT NOT NULL'
                }
                
                # Thêm các cột còn thiếu
                for column_name, column_def in required_columns.items():
                    if column_name not in existing_columns:
                        try:
                            sql = f"ALTER TABLE ticket ADD {column_name} {column_def}"
                            conn.execute(text(sql))
                            print(f"✅ Đã thêm cột: {column_name}")
                        except Exception as e:
                            print(f"⚠️ Lỗi khi thêm cột {column_name}: {e}")
                            # Thử thêm cột với giá trị mặc định
                            try:
                                if 'NOT NULL' in column_def and 'DEFAULT' not in column_def:
                                    # Thêm cột cho phép NULL trước
                                    temp_def = column_def.replace(' NOT NULL', '')
                                    sql = f"ALTER TABLE ticket ADD {column_name} {temp_def}"
                                    conn.execute(text(sql))
                                    print(f"✅ Đã thêm cột {column_name} (cho phép NULL)")
                                    
                                    # Cập nhật dữ liệu mặc định
                                    if column_name == 'PaymentMethod':
                                        update_sql = f"UPDATE ticket SET {column_name} = N'Cash' WHERE {column_name} IS NULL"
                                    elif column_name == 'ContactInfo':
                                        update_sql = f"UPDATE ticket SET {column_name} = N'Contact information required' WHERE {column_name} IS NULL"
                                    else:
                                        continue
                                    
                                    conn.execute(text(update_sql))
                                    print(f"✅ Đã cập nhật dữ liệu mặc định cho {column_name}")
                                    
                                    # Thay đổi thành NOT NULL
                                    alter_sql = f"ALTER TABLE ticket ALTER COLUMN {column_name} NVARCHAR(100) NOT NULL"
                                    conn.execute(text(alter_sql))
                                    print(f"✅ Đã thay đổi {column_name} thành NOT NULL")
                            except Exception as e2:
                                print(f"❌ Không thể thêm cột {column_name}: {e2}")
                
                # Xóa các cột không cần thiết (nếu muốn)
                columns_to_remove = [
                    'EventLocation', 'EventType', 'TicketType', 'OriginalPrice', 
                    'Description', 'CreatedAt', 'UpdatedAt', 'ExpiryDate', 
                    'IsNegotiable', 'ViewCount', 'Rating', 'ReviewCount'
                ]
                
                for column_name in columns_to_remove:
                    if column_name in existing_columns:
                        try:
                            sql = f"ALTER TABLE ticket DROP COLUMN {column_name}"
                            conn.execute(text(sql))
                            print(f"🗑️ Đã xóa cột: {column_name}")
                        except Exception as e:
                            print(f"⚠️ Không thể xóa cột {column_name}: {e}")
                
                print("✅ Đã cập nhật cấu trúc bảng 'ticket'")
                
            else:
                print("📋 Bảng 'ticket' chưa tồn tại, tạo mới...")
                # Tạo lại tất cả bảng với schema mới
                Base.metadata.create_all(bind=engine)
                print("✅ Đã tạo database với schema mới")
        
        print("🎉 Hoàn thành cập nhật database!")
        
    except Exception as e:
        print(f"❌ Lỗi khi cập nhật database: {e}")
        raise

def verify_database_structure():
    """
    Kiểm tra cấu trúc database sau khi cập nhật
    """
    print("\n🔍 Kiểm tra cấu trúc database...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = 'ticket'
                ORDER BY ORDINAL_POSITION
            """))
            columns = result.fetchall()
            
            print("📋 Cấu trúc bảng 'ticket' hiện tại:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"  - {col[0]} ({col[1]}) {nullable}{default}")
                
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra cấu trúc: {e}")

if __name__ == "__main__":
    print("🚀 Bắt đầu quá trình cập nhật database theo ERD...")
    update_database_to_erd()
    verify_database_structure()
    print("\n✨ Hoàn thành! Database đã được cập nhật theo ERD mới.")
