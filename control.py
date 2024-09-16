import yaml, time, subprocess, os, threading, shutil, sqlite3
from urllib.parse import urlparse

def load_settings():
    global settings
    with open('settings.yml', 'r') as file:
        settings = yaml.safe_load(file)

def disable_mc():
    while settings['enabled']:
        if settings['run']['disable_mc']:
            interval = settings['settings']['kill_java_interval']
            try:
                subprocess.run(['pkill', 'java'], check=True)
                print("Java died lol")
            except subprocess.CalledProcessError:
                print("Java is already dead")
            time.sleep(interval)

def disable_downloads():
    while settings['enabled']:
        if settings['run']['disable_downloads']:
            interval = settings['settings']['disable_downloads_interval']
            downloads_path = settings['settings']['downloads_path']
            
            items_deleted = False
            try:
                for item in os.listdir(downloads_path):
                    item_path = os.path.join(downloads_path, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                        items_deleted = True
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                        items_deleted = True
                
                if items_deleted:
                    print("lol your files got snapped")
            except Exception as e:
                print(f"Error clearing Downloads folder: {e}")
            
            time.sleep(interval)

def disable_phone(): # if someone finds this, youre on youre own on this one, Im using google family link with an api request I captured from my browser but Im not publishing that part ofcourse
    try:
        from api import flink_request 
    except ImportError:
        print("api.py not found. Skipping phone disabling.")
        return
        
    prevos_state = None
    while settings['enabled']:
        interval = settings['settings']['disable_phone_interval']
        current_state = settings['run']['disable_phone']
        if current_state != prevos_state:
            # api request
            flink_request(current_state)
            print(f'Sent api request to set Phone Disabled to {current_state}')
            prevos_state = current_state
        time.sleep(interval)

def disable_websites():
    if os.geteuid() != 0:
        print("Disabling websites requires root privileges")
        return
        
    firefox_profile_path = settings['settings']['firefox_profile_path']
    original_db_path = os.path.join(firefox_profile_path, 'places.sqlite')
    temp_db_path = 'temp_places.sqlite'
    hosts_file = '/etc/hosts'
    excluded_domains = settings['settings']['excluded_domains']

    while settings['enabled']:
        changes_made = False

        if not os.path.exists(original_db_path):
            print("Firefox profile not found at the specified path")
            time.sleep(60)  # Wait for a minute before checking again
            continue

        try:
            if settings['run']['disable_websites']:

                # Create a temporary copy of the database
                shutil.copy2(original_db_path, temp_db_path)
                conn = sqlite3.connect(temp_db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT url FROM moz_places")
                domains = set()
                for (url,) in cursor.fetchall():
                    domain = urlparse(url).netloc
                    if domain:
                        domains.add(domain)
                conn.close()

                # Read existing hosts file
                with open(hosts_file, 'r') as hosts:
                    existing_lines = hosts.readlines()

                # Add new domains to hosts file
                with open(hosts_file, 'a') as hosts:
                    added_count = 0
                    for domain in domains:
                        if not any(excluded in domain for excluded in excluded_domains) and not any(line.strip() == f"0.0.0.0 {domain}" for line in existing_lines):
                            hosts.write(f"0.0.0.0 {domain}\n")
                            added_count += 1
                    
                    if added_count > 0:
                        print(f"Added {added_count} new domains to {hosts_file}")
                        changes_made = True
            else:
                # Remove redirected domains from hosts file
                with open(hosts_file, 'r') as hosts:
                    lines = hosts.readlines()
                
                new_lines = [line for line in lines if not line.startswith("0.0.0.0 ")]
                
                if len(new_lines) != len(lines):
                    with open(hosts_file, 'w') as hosts:
                        hosts.writelines(new_lines)
                    print("Removed redirected domains from hosts file")
                    changes_made = True

            if changes_made:
                # Flush DNS caches
                subprocess.run(['resolvectl', 'flush-caches'], check=True)
                print("DNS caches flushed")

                # Kill Firefox processes
                try:
                    subprocess.run(['pkill', 'firefox'], check=True)
                    user = os.getenv('SUDO_USER') or os.getenv('USER')
                    subprocess.Popen(['sudo', '-u', user, 'firefox'], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print("Restarted Firefox")

                except subprocess.CalledProcessError:
                    print("Firefox is not running")
                changes_made = False

        except sqlite3.Error as e:
            print(f"Error accessing Firefox history: {e}")
        except subprocess.CalledProcessError as e:
            print(f"Error executing system command: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_db_path):
                os.remove(temp_db_path)

        time.sleep(int(settings['settings']['disable_websites_interval']))

def main():
    threads = []

    while True:
        load_settings()
        if settings['enabled']:
            if not threads:
                threads = [
                    threading.Thread(target=disable_mc, daemon=True),
                    threading.Thread(target=disable_downloads),
                    threading.Thread(target=disable_phone),
                    threading.Thread(target=disable_websites)
                ]
                for thread in threads:
                    thread.start()
        else:
            for thread in threads:
                thread.join()
            threads = []

        time.sleep(1)

if __name__ == "__main__":
    main()