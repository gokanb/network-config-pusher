import sys
from ip_file_valid import ip_file_valid
from ip_addr_validity import ip_addr_valid
from ip_reach import ip_reach
from ssh_connect import ssh_connection
from create_threads import create_threads


def main():
   


    # Saving the list of IP addresses in ip.txt to a variable
    try:
        ip_list = ip_file_valid()
    except KeyboardInterrupt:
        print("\n\n* Program aborted by user. Exiting...\n")
        sys.exit()

    #  Validate that ip_list is not empty before proceeding
    if not ip_list:
        print("\n[-] No IP addresses found in the file. Exiting...\n")
        sys.exit()

    # Verifying the validity of each IP address in the list
    try:
        ip_addr_valid(ip_list)
    except KeyboardInterrupt:
        print("\n\n* Program aborted by user. Exiting...\n")
        sys.exit()
    except ValueError as e:                              # BUG FIX 3: Catch invalid IP format errors
        print(f"\n[-] IP address validation error: {e}\n")
        sys.exit()

    # Verifying the reachability of each IP address in the list
    try:
        ip_reach(ip_list)
    except KeyboardInterrupt:
        print("\n\n* Program aborted by user. Exiting...\n")
        sys.exit()
    except OSError as e:                                 # BUG FIX 4: Catch network/OS-level errors
        print(f"\n[-] Network reachability error: {e}\n")  # during ping/reach check
        sys.exit()

    # Wrap thread creation in try/except to handle
    # threading errors or SSH failures gracefully
    try:
        create_threads(ip_list, ssh_connection)
    except KeyboardInterrupt:
        print("\n\n* Program aborted by user. Exiting...\n")
        sys.exit()
    except Exception as e:
        print(f"\n[-] An unexpected error occurred during threading: {e}\n")
        sys.exit()


if __name__ == "__main__":      # Entry point guard
    main()
