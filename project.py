import os
import sys
import csv
import time
import getpass
import paramiko
from pathlib import Path
from termcolor import colored
from tabulate import tabulate
from datetime import datetime


devices = []
option = 0
csv_file = 'devices.csv'


def get_device_list():
    # Read CSV file into a list of dictionaries
    if Path(csv_file).exists():
        with open(csv_file, mode='r') as file:
            csv_reader = csv.DictReader(file)
            rows = [row for row in csv_reader]
        if rows:
            for row in rows:
                devices.append(row)
    return devices
    
def write_device_list():
    # Writing dictionary data to CSV
    if len(devices):
        with open(csv_file, mode='w', newline='') as file:
            # Define the fieldnames (keys from the first dictionary)
            fieldnames = devices[0].keys()

            # Create a DictWriter object
            writer = csv.DictWriter(file, fieldnames=fieldnames)

            # Write the header (column names)
            writer.writeheader()

            # Write the rows (data)
            writer.writerows(devices)

            print(colored("\n> Data written to CSV successfully!", "green"))
    
    return True
    
# Connection details
def get_config(host, username, password):
    port = 22  # Default SSH port   
    try:
        # Initialize the SSH client
        ssh = paramiko.SSHClient()
        
        # Automatically add the server's host key (not recommended for production)
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect to the router
        ssh.connect(hostname=host, port=port, username=username, password=password)
        
        print(colored(f"\n> Successfully connected to {host}", "green"))
        # Open an interactive shell session
        remote_conn = ssh.invoke_shell()    
        # Disable terminal paging
        remote_conn.send("terminal length 0\n")
        
        # Send the `show running-config` command
        remote_conn.send("show running-config\n")
        
        # Wait for the command to execute and retrieve the output
       
        time.sleep(1)  # Allow some time for the command to run

        # Read the output
        output = remote_conn.recv(65535).decode('utf-8')

        # Close the connection
        ssh.close()
        
        return output

    except paramiko.AuthenticationException:
        print(colored("\n> Authentication failed, please verify your credentials", 'red'))
    except paramiko.SSHException as sshException:
        print(colored(f"\n> Unable to establish SSH connection: {sshException}", "red"))
    except Exception as e:
        print(colored(f"\n> Error: {e}", "red"))



def menu_options():
    menu_list = {'1': "Device List", '2': 'Add Device', '3':'Del Device', "4": "Make Backup", "5": "Exit"}
    
    return menu_list



def menu():
    print()
    print(colored("==========================================", "green"))
    for key, value in menu_options().items():
        print(f"{key}. {value}")
    print(colored("==========================================", "green"))
    print()

def add_device(name, ip, test=False):
    max_id = 0
    if devices:
        max_id = int(max(device['id'] for device in devices))
    max_id += 1
    
    if not test:
        devices.append({'id': max_id, 'name':name, 'ip': ip})
       
    return max_id
    
    
    


def del_device(id_to_remove, test=False):
    global devices
    new_list = []
    result = False
    
    for device in devices:
        if int(device['id']) == id_to_remove:
            result = True
        else:
            new_list.append(device)
    
    if not test:
        devices = new_list
       
    if result:
        print(colored("\n> Device deleted!", "red"))
    else:
        print(colored("\n> Device not found!", "red"))
        
    return id_to_remove
    

def device_list():
    data = []
    for item in devices:
        data.append([item['id'], item['name'], item['ip']])
    
    table = tabulate(
        data, 
        headers=["id", "name", "ip"], 
        tablefmt="grid"
    )

    print(table)


def save_config(device_name, config):
    # CHECK BACKUP DIR
    check_dir('backup')
    # CHECK DEVICE DIR
    check_dir(f"backup/{device_name}")
    
    current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{current_datetime}_{device_name}.txt"
    
    if config:    
        with open(f"backup/{device_name}/{filename}", 'w') as file:
            file.write(config)
        
        print(colored("\n> Config saved!", "green"))
        
   

def check_dir(path):
     # CHECK IF DIRECTORY EXISTS OR CREATE IT
    directory_path = Path(path)
   
    if not directory_path.exists():
        directory_path.mkdir(parents=True, exist_ok=True)
        
    
def make_backup():
    device_id = int(input('Device ID: '))

    # GET DEVICE
    selected_device = [device for device in devices if int(device['id']) == device_id]
    
    if len(selected_device) == 0:
        return
    else:
        # PRINT DEVICE DETAILS
        device_ip = selected_device[0]['ip']
        device_name = selected_device[0]['name']
    
        print('------------------------------------------')
        print(colored('Selected Device', 'red'))
        print(f"Device name:\t{device_name}")
        print(f"Device ip:\t{device_ip}")
        print('------------------------------------------')
        
        
    confirm = input("Make backup? y/n (y): ")
    
    if confirm == 'n':
        return 
    elif confirm == 'y' or confirm == '':
        user = input('User: ')
        password = getpass.getpass('Password: ')
        config = get_config(device_ip, user, password)
        save_config(device_name, config)
        
    return

def clear_screen():
    # For Windows
    if os.name == 'nt':
        os.system('cls')
    # For macOS and Linux
    else:
        os.system('clear')
        
    return True
        
def bye():
    print(colored("\n==========================================", "red"))
    print("Bye!")
    print(colored("==========================================", "red"))
    sys.exit()


if __name__ == "__main__":
    clear_screen()
    # READ DEVICE LIST FROM CSV FILE
    get_device_list()
    
    print(colored("==========================================\n","green"))
    print(colored(f" CISCO CONFIG BACKUP CLI", "red"))
    
    while option != '5':
        try:
            menu()
            
            option = input("Enter option: ")
            print()
        
            # DEVICE LIST
            if option == '1':
                device_list()
            # ADD DEVICE
            if option == '2':
                name = input("Device Name: ")
                ip = input("Device IP: ")
                add_device(name, ip)
                print(colored("\n> Device added!", "green"))
                
            # DEL DEVICE
            if option == '3':
                id_to_remove = int(input('Device ID: '))
                del_device(id_to_remove)
            # BACKUP
            if option == '4':
                make_backup()
            # EXIT
            if option == '5':
                bye()
                             
        except KeyboardInterrupt:
            bye()
        except EOFError:
            bye()

        