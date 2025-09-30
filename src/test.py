import socket
import subprocess
import platform
import pyodbc
from sqlalchemy import create_engine
import time
import sys

def check_network_connectivity():
    """Test basic network connectivity to the SQL Server"""
    print("1. NETWORK CONNECTIVITY TESTS")
    print("=" * 50)
    
    server = "MYLAPTOP020"
    port = 54180
    
    # Test if we can resolve the hostname
    print(f"Testing hostname resolution for '{server}'...")
    try:
        ip = socket.gethostbyname(server)
        print(f"✓ Hostname resolved to: {ip}")
    except socket.gaierror as e:
        print(f"✗ Hostname resolution failed: {e}")
        print("  Try using IP address instead of hostname")
        return False
    
    # Test TCP connectivity
    print(f"\nTesting TCP connection to {server}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    
    try:
        result = sock.connect_ex((server, port))
        if result == 0:
            print(f"✓ TCP connection successful to {server}:{port}")
            sock.close()
            return True
        else:
            print(f"✗ TCP connection failed to {server}:{port}")
            print(f"  Connection result code: {result}")
            sock.close()
            return False
    except Exception as e:
        print(f"✗ TCP connection error: {e}")
        sock.close()
        return False

def test_alternative_ports():
    """Test common SQL Server ports"""
    print("\n2. TESTING COMMON SQL SERVER PORTS")
    print("=" * 50)
    
    server = "MYLAPTOP020"
    common_ports = [1433, 1434, 54180, 14033]  # Include your custom port
    
    for port in common_ports:
        print(f"Testing port {port}...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        
        try:
            result = sock.connect_ex((server, port))
            if result == 0:
                print(f"✓ Port {port} is open")
            else:
                print(f"✗ Port {port} is closed/filtered")
        except Exception as e:
            print(f"✗ Error testing port {port}: {e}")
        finally:
            sock.close()

def check_sql_server_services():
    """Check if SQL Server services are running (Windows only)"""
    print("\n3. SQL SERVER SERVICE STATUS")
    print("=" * 50)
    
    if platform.system() != "Windows":
        print("Service check only available on Windows")
        return
    
    sql_services = [
        "MSSQLSERVER",
        "SQLSERVERAGENT", 
        "MSSQLServerOLAPService",
        "SQLBrowser",
        "MSSQL$*"  # Named instances
    ]
    
    try:
        # Get all services
        result = subprocess.run(['sc', 'query', 'type=service', 'state=all'], 
                              capture_output=True, text=True, shell=True)
        
        services_output = result.stdout
        
        print("SQL Server related services:")
        for line in services_output.split('\n'):
            if any(service.replace('$*', '') in line.upper() for service in sql_services):
                if 'SERVICE_NAME' in line or 'STATE' in line or 'DISPLAY_NAME' in line:
                    print(f"  {line.strip()}")
        
        # Check specifically for SQL Server Browser (important for named instances)
        browser_result = subprocess.run(['sc', 'query', 'SQLBrowser'], 
                                      capture_output=True, text=True, shell=True)
        
        if browser_result.returncode == 0:
            print("\nSQL Server Browser service status:")
            for line in browser_result.stdout.split('\n'):
                if 'STATE' in line:
                    print(f"  {line.strip()}")
        
    except Exception as e:
        print(f"Could not check services: {e}")

def test_named_instance_connection():
    """Test connection using named instance format"""
    print("\n4. TESTING NAMED INSTANCE CONNECTIONS")
    print("=" * 50)
    
    # Common named instance patterns
    instance_formats = [
        "MYLAPTOP020\\SQLEXPRESS",
        "MYLAPTOP020\\MSSQLSERVER", 
        "MYLAPTOP020\\SQL2019",
        "MYLAPTOP020\\SQL2022",
        "localhost\\SQLEXPRESS",
        "localhost,54180",
        "MYLAPTOP020,54180"
    ]
    
    for server_name in instance_formats:
        print(f"Testing connection to: {server_name}")
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server_name};"
                f"DATABASE=master;"  # Try master database first
                f"Trusted_Connection=yes;"
                f"Connection Timeout=5;"
            )
            
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT @@SERVERNAME, @@VERSION")
            result = cursor.fetchone()
            print(f"✓ Connected to: {result[0]}")
            print(f"  Version: {result[1][:80]}...")
            cursor.close()
            conn.close()
            return server_name
            
        except pyodbc.Error as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                print(f"  ✗ Timeout (server may not exist)")
            elif "login failed" in error_msg.lower():
                print(f"  ✗ Authentication failed (but server is reachable!)")
            else:
                print(f"  ✗ {error_msg[:100]}...")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
    
    return None

def test_windows_authentication():
    """Test Windows Authentication"""
    print("\n5. TESTING WINDOWS AUTHENTICATION")
    print("=" * 50)
    
    server_formats = [
        "MYLAPTOP020,54180",
        "MYLAPTOP020\\SQLEXPRESS",
        "localhost,54180",
        "(local)",
        "."
    ]
    
    for server in server_formats:
        print(f"Testing Windows Auth to: {server}")
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={server};"
                f"DATABASE=historian;"
                f"Trusted_Connection=yes;"
                f"Connection Timeout=5;"
            )
            
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT SYSTEM_USER, DB_NAME()")
            result = cursor.fetchone()
            print(f"✓ Connected as: {result[0]} to database: {result[1]}")
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"  ✗ {str(e)[:100]}...")
    
    return False

def provide_recommendations():
    """Provide troubleshooting recommendations"""
    print("\n6. TROUBLESHOOTING RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = [
        "1. Check if SQL Server is running:",
        "   - Open SQL Server Configuration Manager",
        "   - Ensure SQL Server service is started",
        "   - Check if SQL Server Browser is running (for named instances)",
        "",
        "2. Enable TCP/IP protocol:",
        "   - SQL Server Configuration Manager > SQL Server Network Configuration",
        "   - Enable TCP/IP protocol",
        "   - Restart SQL Server service",
        "",
        "3. Configure firewall:",
        "   - Allow SQL Server through Windows Firewall",
        "   - Allow port 54180 (your custom port)",
        "   - Allow port 1434 (SQL Server Browser)",
        "",
        "4. Check SQL Server Authentication:",
        "   - Enable 'SQL Server and Windows Authentication mode'",
        "   - Verify user 'n8n' exists and has proper permissions",
        "",
        "5. Alternative connection strings to try:",
        "   - Use (local) instead of MYLAPTOP020",
        "   - Try Windows Authentication first",
        "   - Use IP address instead of hostname",
        "",
        "6. Check SQL Server port configuration:",
        "   - SQL Server Configuration Manager > Protocols for MSSQLSERVER",
        "   - TCP/IP Properties > IP Addresses",
        "   - Verify port 54180 is configured correctly"
    ]
    
    for rec in recommendations:
        print(rec)

def main():
    print("SQL SERVER CONNECTION DIAGNOSTIC TOOL")
    print("=" * 60)
    
    # Run all diagnostic tests
    network_ok = check_network_connectivity()
    
    test_alternative_ports()
    
    check_sql_server_services()
    
    working_server = test_named_instance_connection()
    
    if not working_server:
        windows_auth_ok = test_windows_authentication()
    
    provide_recommendations()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETED")
    
    if network_ok:
        print("✓ Network connectivity is working")
    else:
        print("✗ Network connectivity issues detected")

if __name__ == "__main__":
    main()