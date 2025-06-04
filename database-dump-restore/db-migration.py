import subprocess
import os
import json
from multiprocessing import Pool, cpu_count
import npyscreen

CHECKPOINT_FILE = 'checkpoint.json'

def check_and_install_mysql():
    try:
        subprocess.run(['mysql', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("MySQL is already installed.")
    except FileNotFoundError:
        print("MySQL command not found. Installing MySQL...")
        subprocess.run(['sudo', 'yum', 'install', 'https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm'], check=True)
        subprocess.run(['sudo', 'yum', 'update', '-y'], check=True)
        subprocess.run(['sudo', 'yum', 'install', 'mysql-community-client', '-y'], check=True)
    except subprocess.CalledProcessError:
        print("Error while checking MySQL installation.")

def check_database_connection(host, user, password):
    try:
        subprocess.run(['mysql', '-h', host, '-u', user, f'-p{password}', '-e', 'SELECT 1'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False

def create_database_if_not_exists(host, user, password, db_name):
    try:
        subprocess.run(['mysql', '-h', host, '-u', user, f'-p{password}', '-e', f'CREATE DATABASE IF NOT EXISTS {db_name}'], check=True)
        print(f"Database '{db_name}' created or already exists on target host.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to create database '{db_name}' on target host. Ensure the user has the CREATE privilege. Error: {e}")
        return False
    return True

def save_checkpoint(data):
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(data, f)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    return {"dumped": [], "restored": []}

def dump_table(args):
    source_host, source_user, source_password, source_db, table, backup_file = args
    print(f"Taking dump of table '{table}' from database '{source_db}'...")
    dump_command = (
        f"mysqldump --single-transaction --set-gtid-purged=OFF "
        f"-h {source_host} -u {source_user} -p{source_password} "
        f"{source_db} {table} | gzip > {backup_file}"
    )
    result = subprocess.run(dump_command, shell=True)
    return table if result.returncode == 0 else None

def restore_table(args):
    target_host, target_user, target_password, target_db, backup_file = args
    print(f"Restoring table from '{backup_file}' into database '{target_db}'...")
    restore_command = f"gunzip < {backup_file} | mysql -h {target_host} -u {target_user} -p{target_password} {target_db}"
    result = subprocess.run(restore_command, shell=True)
    return os.path.basename(backup_file).replace('.sql.gz', '') if result.returncode == 0 else None

class DBBackupRestoreForm(npyscreen.Form):
    def create(self):
        self.source_host = self.add(npyscreen.TitleText, name="Source DB Host:")
        self.source_db = self.add(npyscreen.TitleText, name="Source DB Name:")
        self.source_user = self.add(npyscreen.TitleText, name="Source DB User:")
        self.source_password = self.add(npyscreen.TitlePassword, name="Source DB Password:")
        self.target_host = self.add(npyscreen.TitleText, name="Target DB Host:")
        self.target_db = self.add(npyscreen.TitleText, name="Target DB Name:")
        self.target_user = self.add(npyscreen.TitleText, name="Target DB User:")
        self.target_password = self.add(npyscreen.TitlePassword, name="Target DB Password:")
        self.backup_dir = self.add(npyscreen.TitleText, name="Backup Directory:", value="/tmp/db_backups")

    def afterEditing(self):
        self.parentApp.setNextForm(None)

class DBBackupRestoreApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.form = self.addForm('MAIN', DBBackupRestoreForm, name="DB Backup and Restore")

def backup_and_restore(source_host, source_db, source_user, source_password, target_host, target_db, target_user, target_password, backup_dir):
    """Optimized script to backup a MySQL database from the EU region and restore it to the ME region with checkpointing."""

    # Check if source and target databases are reachable
    if not check_database_connection(source_host, source_user, source_password):
        print(f"Cannot connect to source database at {source_host}. Please check the connection details.")
        return

    if not check_database_connection(target_host, target_user, target_password):
        print(f"Cannot connect to target database at {target_host}. Please check the connection details.")
        return

    # Create the target database if it doesn't exist
    if not create_database_if_not_exists(target_host, target_user, target_password, target_db):
        print("Failed to create the target database. Exiting.")
        return

    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Load checkpoint data
    checkpoint = load_checkpoint()

    # Get list of tables from the source database
    show_tables_command = f"mysql -h {source_host} -u {source_user} -p{source_password} -e 'SHOW TABLES IN {source_db};'"
    tables = subprocess.check_output(show_tables_command, shell=True).decode().splitlines()[1:]

    # Tables to process for dump
    tables_to_dump = [table for table in tables if table not in checkpoint['dumped']]

    # Parallel dump
    pool = Pool(cpu_count())
    for table in tables_to_dump:
        backup_file = os.path.join(backup_dir, f"{table}.sql.gz")
        result = pool.apply_async(dump_table, args=[(source_host, source_user, source_password, source_db, table, backup_file)])
        dumped_table = result.get()
        if dumped_table:
            checkpoint['dumped'].append(dumped_table)
            save_checkpoint(checkpoint)

    pool.close()
    pool.join()

    print("Backup completed for all tables.")

    # Tables to process for restore
    tables_to_restore = [table for table in checkpoint['dumped'] if table not in checkpoint['restored']]

    # Parallel restore
    pool = Pool(cpu_count())
    for table in tables_to_restore:
        backup_file = os.path.join(backup_dir, f"{table}.sql.gz")
        result = pool.apply_async(restore_table, args=[(target_host, target_user, target_password, target_db, backup_file)])
        restored_table = result.get()
        if restored_table:
            checkpoint['restored'].append(restored_table)
            save_checkpoint(checkpoint)

    pool.close()
    pool.join()

    print("Restore completed for all tables.")

if __name__ == '__main__':
    check_and_install_mysql()

    app = DBBackupRestoreApp()
    app.run()

    form = app.form

    backup_and_restore(
        source_host=form.source_host.value,
        source_db=form.source_db.value,
        source_user=form.source_user.value,
        source_password=form.source_password.value,
        target_host=form.target_host.value,
        target_db=form.target_db.value,
        target_user=form.target_user.value,
        target_password=form.target_password.value,
        backup_dir=form.backup_dir.value
    )