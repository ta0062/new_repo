import os
import time
import boto3
import psycopg2
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# ===== load enviroment ====
load_dotenv()

# AWS S3 setup
S3_BUCKET=os.getenv("S3_BUCKET")
s3=boto3.client('s3')
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")
DB_HOST=os.getenv("DB_HOST")
DB_PORT=os.getenv("DB_PORT")
WATCH_FOLDER=os.getenv("WATCH_FOLDER")

# PostgreSQL connection setup
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)
cur = conn.cursor()

# Folder to watch
WATCH_FOLDER = WATCH_FOLDER

class S3SyncHandler(FileSystemEventHandler):
    def process_file(self, file_path):
        if not os.path.isfile(file_path):
            return

        file_name = os.path.basename(file_path)

        try:
            # Upload to S3
            s3.upload_file(file_path, S3_BUCKET, file_name)
            s3_url = f"https://{S3_BUCKET}.s3.amazonaws.com/{file_name}"

            # Insert into PostgreSQL
            cur.execute(
                "INSERT INTO s3_link_storage (file_name, s3_links) VALUES (%s, %s)",
                (file_name, s3_url)
            )
            conn.commit()

            print(f"✅ Uploaded {file_name} → S3 & stored in DB")

        except Exception as e:
            print(f"❌ Error processing {file_name}: {e}")

    def on_created(self, event):
        if not event.is_directory:
            print(f"📄 New file detected: {event.src_path}")
            self.process_file(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"✏️ File modified: {event.src_path}")
            self.process_file(event.src_path)


if __name__ == "__main__":
    print(f"📡 Watching for changes in {WATCH_FOLDER} and syncing to S3 bucket: {S3_BUCKET}")
    event_handler = S3SyncHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_FOLDER, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        conn.close()
        print("👋 Sync stopped.")
    observer.join()
