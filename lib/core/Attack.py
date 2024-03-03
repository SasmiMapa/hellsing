import configparser
from datetime import datetime
import os
import shlex
import socket
import subprocess
import sys
import shutil

from lib.core.Config import *
from lib.output import Output
from lib.output.Logger import logger
from lib.utils.StringUtils import StringUtils
from lib.utils.NetworkUtils import NetworkUtils

class Attack:
    def __init__ (self, settings):
        """
        Construct the Attack object.

        :param Settings settings: Settings from config file
        """
        self.settings = settings
        self.config = configparser.ConfigParser()
        self.config.read(HTTP_CONF_FILE + CONF_EXT)
        self.tools = self.config.sections()
        self.basepath = HTTP_TOOLBOX_DIR
        
        # creating NetworkUtils object
        self.netutils = NetworkUtils()

    #------------------------------------------------------------------------------------
    
    # Attack methods    
    def set_target(self, target):
        """
        Set the target for the attack and execute the relevant commands.

        :param target: Target URL or IP address
        """ 
        protocol, base_target, specified_port, domain = '', '', None, ''
        is_ip_address = False

        # Extract protocol, domain/IP, and port from the target
        if "://" in target:
            protocol, _, rest = target.partition("://")
            if '/' in rest:
                rest = rest.split('/', 1)[0]
            if ':' in rest:
                base_target, port_str = rest.rsplit(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    print(f"Invalid port number: {port_str}.")
                    return
            else:
                base_target = rest
        else:
            if ':' in target:
                base_target, port_str = target.split(':', 1)
                if self.netutils.is_valid_port(port_str):
                    specified_port = port_str
                else:
                    print(f"Invalid port number: {port_str}.")
                    return
            else:
                base_target = target

        # Determine if the base target is an IP address
        try:
            socket.inet_aton(base_target)
            is_ip_address = True
        except socket.error:
            is_ip_address = False

        # Fetch the default port if not specified
        default_port = self.config['config'].get('default_port', '80')
        port = specified_port if specified_port else default_port

        # Perform DNS or reverse DNS lookups as necessary
        if is_ip_address:
            domain = self.netutils.reverse_dns_lookup(base_target) or base_target
        else:
            domain = base_target.split("//")[-1].split("/")[0]
            ip_address = self.netutils.dns_lookup(domain) or base_target

        # List of section names to exclude
        excluded_sections = ["config", "specific_options", "products"]

        for tool in self.tools:
            if tool.lower() in excluded_sections:
                continue

            tool_config = self.config[tool]
            command_template = tool_config.get('command_1', None)
            if command_template:
                command = command_template
                if "[URL]" in command:
                    command = command.replace("[URL]", f"{protocol}://{domain if not is_ip_address else base_target}:{port}")
                if "[IP]" in command:
                    command = command.replace("[IP]", ip_address if not is_ip_address else base_target)
                if "[DOMAIN]" in command:
                    extracted_domain = self.netutils.extract_secondary_domain(domain)
                    command = command.replace("[DOMAIN]", extracted_domain)
                command = command.replace("[PORT]", port)
                
                # Check if the tool's execution directory exists
                tool_name = tool_config.get('tool', '').lower()
                tool_dir_path = HTTP_TOOLBOX_DIR + '/' + tool_name
                
                if os.path.isdir(tool_dir_path):
                    # Change to the tool's directory and execute the command
                    os.chdir(tool_dir_path)
                    print(f"Changed directory to {tool_dir_path}")
                else:
                    # Tool can be executed directly, no directory change needed
                    print(f"Executing {tool_name} directly without changing directory.")

                # Execute the command
                try:
                    print(f"Executing: {command}")
                    subprocess.run(shlex.split(command), check=True)
                except subprocess.CalledProcessError as e:
                    print(f"Error executing {tool}: {e}")
                finally:
                    # Change back to the original directory after execution
                    if os.path.isdir(tool_dir_path):
                        os.chdir(TOOL_BASEPATH)  # Adjust this path to return to the original directory as needed
                print('\n')
            else:
                print(f"No command template found for {tool}.\n")

        print("All applicable tools have been executed for the target.\n")
        
    
    def set_service(self, service):
        """
        Set the service to attack.

        :param str service: Service to attack
        """
        self.service = service
        
    
    def use_profile(self, profile):
        """
        Use the specified attack profile.

        :param str profile: Attack profile to use
        """
        self.profile = profile
        
    
    def run_only(self, checks):
        """
        Run only the specified checks.

        :param list categories: Categories of checks to run
        """
        self.checks = checks
        
    
    def run_exclude(self, checks):
        """
        Exclude the specified checks.

        :param list categories: Categories of checks to exclude
        """
        self.exclude = checks
        
        
    