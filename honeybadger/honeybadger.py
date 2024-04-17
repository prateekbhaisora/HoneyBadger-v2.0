#!/usr/bin/env python2

import shlex            # Used to split command-line strings into tokens, respecting quoted strings and other shell syntax.
import subprocess       # Allows for the creation and management of subprocesses, enabling interaction with system processes, and executing shell commands.
import os               # Provides functions for interacting with the operating system, such as accessing files and directories.
import re               # Provides support for regular expressions, allowing for pattern matching and string manipulation.
import argparse         # Used for parsing command-line arguments, providing a structured and user-friendly interface for defining and handling script arguments.
import logging          # Provides facilities for event logging within Python programs, allowing for the creation of log messages with various severity levels.
import requests         # Enables HTTP requests to be made from Python code, facilitating interaction with web services and APIs.
import symExec          # custom module for symbolic execution, used for analyzing and reasoning about programs symbolically.
import global_params    # custom module for managing global parameters or configurations within the program.
import z3               # Provides access to the Z3 theorem prover, allowing for formal verification and constraint solving.
import z3.z3util        # Additional utilities for working with Z3, such as simplification and printing of Z3 expressions.
from bs4 import BeautifulSoup # For fetching source code from address.

from source_map import SourceMap    # custom module for managing source code mappings or relationships between different representations of code.
from utils import run_command       # custom module containing utility functions used throughout the program.
from HTMLParser import HTMLParser   # Provides a parser for HTML documents, allowing for parsing and extracting data from HTML strings or files.


# Original Code used solc 0.4.25, evm 1.8.16 and z3 4.7.1 and go 1.9.2 (for building from source)

#  The function returns True if the command exists and is executable, and False otherwise.
def cmd_exists(cmd):
    # Subprocess.call will return 0 (successful exit code) if call was successful
    return subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def cmd_stdout(cmd):
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    if err:
        return False, output.decode("utf-8")
    else:
        return True, output.decode("utf-8")

def has_dependencies_installed():
    try:
        z3.get_version_string()
    except:
        logging.critical("Z3 is not available. Please install z3 from https://github.com/Z3Prover/z3.")
        return False
    if not z3_cmp_version():
        logging.critical("Z3 version is incompatible.")
        return False

    if not cmd_exists("evm"):
        logging.critical("Please install evm from go-ethereum and make sure it is in the path.")
        return False
    if not evm_cmp_version():
        logging.critical("evm version is incompatible.")
        return False

    if not cmd_exists("solc --version"):
        logging.critical("solc is missing. Please install the solidity compiler and make sure solc is in the path.")
        return False
    if not solc_cmp_version():
        logging.critical("solc version is incompatible.")
        return False

    return True

import logging

def z3_cmp_version():
    # max_version and min_version need to have the same number of dot separated numbers.
    # The parts of the version need to be convertible to integers.
    max_version_str = "4.8.1"
    min_version_str = "4.7.1"
    max_version = [int(x) for x in max_version_str.split(".")]
    min_version = [int(x) for x in min_version_str.split(".")]

    success, output = cmd_stdout("z3 --version")  # Modified command to check Z3 version
    if not success or not output:
        logging.critical("Error while determining the version of Z3.")

    version_str = output.split()[2].split("-")[0]
    version = [int(x) for x in version_str.split(".")]

    if len(version) != len(max_version):
        logging.critical("Cannot compare versions: {} (max) and {} (installed).".format(max_version_str, version_str))

    for i in range(0, len(max_version)):
        if max_version[i] < version[i]:
            logging.critical("The installed Z3 version ({}) is too new. Honeybadger supports at most version {}.".format(version_str, max_version_str))
            return False
        if min_version[i] > version[i]:
            logging.critical("The installed Z3 version ({}) is too old. Honeybadger requires at least version {}.".format(version_str, min_version_str))
            return False

    return True

def evm_cmp_version():
    # max_version and min_version need to have the same number of dot separated numbers.
    # The parts of the version need to be convertible to integers.
    max_version_str = "1.8.16"
    min_version_str = "0.0.0"
    max_version = [int(x) for x in max_version_str.split(".")]
    min_version = [int(x) for x in min_version_str.split(".")]

    success, output = cmd_stdout("evm --version")
    if not success or not output:
        logging.critical("Error while determining the version of the evm.")

    version_str = output.split()[2].split("-")[0]
    version = [int(x) for x in version_str.split(".")]

    if len(version) != len(max_version):
        logging.critical("Cannot compare versions: {} (max) and {} (installed).".format(max_version_str, version_str))

    for i in range(0, len(max_version)):
        if max_version[i] < version[i]:
            logging.critical("The installed evm version ({}) is too new. Honeybadger supports at most version {}.".format(version_str, max_version_str))
            return False
        if min_version[i] > version[i]:
            logging.critical("The installed evm version ({}) is too old. Honeybadger requires at least version {}.".format(version_str, min_version_str))
            return False

    return True

import logging

def solc_cmp_version():
    # max_version and min_version need to have the same number of dot separated numbers.
    # The parts of the version need to be convertible to integers.
    max_version_str = "0.4.30"
    min_version_str = "0.4.25"
    max_version = [int(x) for x in max_version_str.split(".")]
    min_version = [int(x) for x in min_version_str.split(".")]

    success, output = cmd_stdout("solc --version")
    if not success or not output:
        logging.critical("Error while determining the version of the solc compiler.")

    version_str = output.split()[-1].split("+")[0]
    version = [int(x) for x in version_str.split(".")]

    if len(version) != len(max_version):
        logging.critical("Cannot compare versions: {} (max) and {} (installed).".format(max_version_str, version_str))

    for i in range(0, len(max_version)):
        if max_version[i] < version[i]:
            logging.critical("The installed solc version ({}) is too new. Honeybadger supports at most version {}.".format(version_str, max_version_str))
            return False
        if min_version[i] > version[i]:
            logging.critical("The installed solc version ({}) is too old. Honeybadger requires at least version {}.".format(version_str, min_version_str))
            return False

    return True

# This function removes the Swarm hash (a content-addressable identifier) from an EVM bytecode string
def removeSwarmHash(evm):
    evm_without_hash = re.sub(r"a165627a7a72305820\S{64}0029$", "", evm)
    return evm_without_hash

# This function takes a string (s) representing the compiled output of a Solidity contract and returns a (contract name, corresponding binary code)
def extract_bin_str(s):
    # print(s)      # Debug
    # Carraige return (\r) is made optional using ?, to support both Windows-style line endings (\r\n) and Unix-style line endings (\n)
    # (.*?): This is a capturing group ( ... ) that matches any character (.), zero or more times *, lazily ?
    # The ? after the * makes the * quantifier lazy, meaning it will match as few characters as possible while still allowing the rest of the regex to match
    # (.*?) is used twice to create a (contract name, corresponding binary code)
    binary_regex = r"======= (.*?) =======\s+Binary of the runtime part:\s+(.*?)\s+"
    # Find all non-overlapping matches of the regular expression pattern binary_regex in the compiled output of a solidity contract s. 
    # Each match is a tuple containing the contract name and its corresponding binary code.
    contracts = re.findall(binary_regex, s)
    # print(contracts)      # Debug 
    # Filters out any contracts where the binary code is empty (contract[1] evaluates to False). 
    # This is done to remove any empty or invalid contracts from the list.
    contracts = [contract for contract in contracts if contract[1]]
    # If no valid contracts are found, log error message
    if not contracts:
        logging.critical("Solidity compilation failed")
        print ("======= error =======")
        print ("Solidity compilation failed")
        exit()
    # If valid contracts are found, it returns a list of tuples, where each tuple = (contract name, corresponding binary code).
    return contracts

def compileContracts(contract):
    # The --bin-runtime flag tells solc to include the binary runtime code in the output.
    cmd = "solc --bin-runtime %s" % contract
    out = run_command(cmd)

    # It uses a regular expression re.findall() to search for occurrences of a specific pattern (underscore characters followed by 
    # some characters followed by another underscore) in the output out. This pattern is commonly used to identify library names in 
    # Solidity output. The findall() function returns a list of all non-overlapping matches of the pattern (library names) in the string out.
    libs = re.findall(r"_+(.*?)_+", out)
    libs = set(libs)        # Remove Duplicates
    if libs:
        return link_libraries(contract, libs)           # If external libraries used in code, link them and then extract binary
    else: 
        return extract_bin_str(out)                     # If no external libraries used in code, then extract binary


def link_libraries(filename, libs):
    option = ""
    for idx, lib in enumerate(libs):
        lib_address = "0x" + hex(idx+1)[2:].zfill(40)
        option += " --libraries %s:%s" % (lib, lib_address)
    FNULL = open(os.devnull, 'w')
    cmd = "solc --bin-runtime %s" % filename
    p1 = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=FNULL)
    cmd = "solc --link%s" %option
    p2 = subprocess.Popen(shlex.split(cmd), stdin=p1.stdout, stdout=subprocess.PIPE, stderr=FNULL)
    p1.stdout.close()
    out = p2.communicate()[0]
    return extract_bin_str(out)

def analyze(processed_evm_file, disasm_file, source_map = None):
    
    # This attempts to disassemble the processed EVM bytecode file using the evm disasm command.
    disasm_out = ""

    try:
        disasm_p = subprocess.Popen(
            ["evm", "disasm", processed_evm_file], stdout=subprocess.PIPE)
        # disasm_out will contain the disassembled bytecode in assembly format
        disasm_out = disasm_p.communicate()[0]
    except:
        logging.critical("Disassembly failed.")
        exit()

    # print(disasm_out)
    with open(disasm_file, 'w') as of:
        of.write(disasm_out)

    if source_map is not None:
        # Main HoneyPot detection logic is in SymExec
        symExec.main(disasm_file, args.source, source_map)
    else:
        symExec.main(disasm_file, args.source)

# This function removes a temporary file if it exists at the specified path
def remove_temporary_file(path):
    if os.path.isfile(path):
        try:
            os.unlink(path)
        except:
            pass

def main():
    global args

    parser = argparse.ArgumentParser()    # Instantiates object of ArguementParser Class 
    group = parser.add_mutually_exclusive_group(required=True)  # Creates mutually exclusive group of atleast one cmd line args.
    group.add_argument("-s", "--source", type=str,
                       help="local source file name. Solidity by default. Use -b to process evm instead. Use stdin to read from stdin.")
    group.add_argument("-ru", "--remoteURL", type=str,
                       help="Get contract from remote URL. Solidity by default. Use -b to process evm instead.", dest="remote_URL")
    group.add_argument("-a", "--address", type=str, 
                       help="Fetches smart contract source code from its address.") 

    # Current HoneyBadger Version
    parser.add_argument("--version", action="version", version="HoneyBadger version 2.0")
    parser.add_argument(
        "-b", "--bytecode", help="read bytecode in source instead of solidity file.", action="store_true")
    parser.add_argument("--contract", type=str, help="Contract in Solidity source to analyze; otherwise analyze all.")
    parser.add_argument(
        "-j", "--json", help="Redirect results to a json file.", action="store_true")
    parser.add_argument("-t", "--timeout", type=int, help="Timeout for Z3 in ms (default "+str(global_params.TIMEOUT)+" ms).")
    parser.add_argument("-gb", "--globalblockchain",
                        help="Integrate with the global ethereum blockchain", action="store_true")
    parser.add_argument("-dl", "--depthlimit", help="Limit DFS depth (default "+str(global_params.DEPTH_LIMIT)+").",
                        action="store", dest="depth_limit", type=int)
    parser.add_argument("-gl", "--gaslimit", help="Limit Gas (default "+str(global_params.GAS_LIMIT)+").",
                        action="store", dest="gas_limit", type=int)
    parser.add_argument(
        "-st", "--state", help="Get input state from state.json", action="store_true")
    parser.add_argument("-ll", "--looplimit", help="Limit number of loops (default "+str(global_params.LOOP_LIMIT)+").",
                        action="store", dest="loop_limit", type=int)
    parser.add_argument("-glt", "--global-timeout", help="Timeout for symbolic execution in sec (default "+str(global_params.GLOBAL_TIMEOUT)+" sec).", action="store", dest="global_timeout", type=int)
    parser.add_argument(
            "--debug", help="Display debug information.", action="store_true")
    parser.add_argument(
        "-c", "--cfg", help="Create control flow graph and store as .dot file.", action="store_true")
    
    print("")
    print("                                    ___,,___                                                        ")
    print("                              _,-='=- =-  -`''--.__,,.._                                            ")
    print("                           ,-;// /  - -       -   -= - '=.                                          ")
    print("                         ,'///    -     -   -   =  - ==-=\`.                                        ")
    print("                        |/// /  =    `. - =   == - =.=_,,._ `=/|                                    ")
    print("                       ///    -   -    \  - - = ,ndDMHHMM/\b  \\                                    ")
    print("                     ,' - / /        / /\ =  - /MM(,,._`YQMML  `|                                   ")
    print("                    <_,=^Kkm / / / / ///H|wnWWdMKKK#''-;. `'0\  |                                   ")
    print("                           `''QkmmmmmnWMMM\''WHMKKMM\   `--.  \> \                                  ")
    print("                                 `'''  `->>>    ``WHMb,.    `-_<@)                                  ")
    print("                                                   `'QMM`.                                          ")
    print("                                                      `>>>                                          ")
    print("  _    _                        ____            _                               ____         ____   ")
    print(" | |  | |                      |  _ \          | |                             |__  \       /    \  ")
    print(" | |__| | ___  _ __   ___ _   _| |_) | __ _  __| | __ _  ___ _ __      __    __   |  |     |  /\  | ")
    print(" |  __  |/ _ \| '_ \ / _ \ | | |  _ < / _` |/ _` |/ _` |/ _ \ '__| ___ \ \  / /   |  |     | |  | | ")
    print(" | |  | | (_) | | | |  __/ |_| | |_) | (_| | (_| | (_| |  __/ |   |___| \ \/ /  _/  /_   _ |  \/  | ")
    print(" |_|  |_|\___/|_| |_|\___|\__, |____/ \__,_|\__,_|\__, |\___|_|          \__/  |______| (_) \____/  ")
    print("                           __/ |                   __/ |                                            ")
    print("                          |___/                   |___/                                             ")
    print("")


    args = parser.parse_args()

    # Set global arguments for symbolic execution, based on cmd line args passed
    global_params.USE_GLOBAL_BLOCKCHAIN = 1 if args.globalblockchain else 0
    global_params.INPUT_STATE = 1 if args.state else 0
    global_params.STORE_RESULT = 1 if args.json else 0
    global_params.DEBUG_MODE = 1 if args.debug else 0
    global_params.CFG = 1 if args.cfg else 0
    global_params.BYTECODE = 1 if args.bytecode else 0

    if args.timeout:
        global_params.TIMEOUT = args.timeout
    if args.depth_limit:
        global_params.DEPTH_LIMIT = args.depth_limit
    if args.gas_limit:
        global_params.GAS_LIMIT = args.gas_limit
    if args.loop_limit:
        global_params.LOOP_LIMIT = args.loop_limit
    if args.global_timeout:
        global_params.GLOBAL_TIMEOUT = args.global_timeout
    
    # Configuring the logging system to display log messages with severity level INFO or higher to the console
    logging.basicConfig(level=logging.INFO)

    # Check that our system has everything we need (solc, evm, Z3)
    if not has_dependencies_installed():
        return
    # Retrieve contract from remote URL, if necessary
    if args.remote_URL:
        r = requests.get(args.remote_URL)
        code = r.text
        filename = "remote_contract.evm" if args.bytecode else "remote_contract.sol"
        if "etherscan.io" in args.remote_URL and not args.bytecode:
            try:
                filename = re.compile('<td>Contract<span class="hidden-su-xs"> Name</span>:</td><td>(.+?)</td>').findall(code.replace('\n','').replace('\t',''))[0].replace(' ', '')
                filename += ".sol"
            except:
                pass
            code = re.compile("<pre class='js-sourcecopyarea' id='editor' style='.+?'>([\s\S]+?)</pre>", re.MULTILINE).findall(code)[0]
            code = HTMLParser().unescape(code)
        args.source = filename
        with open(filename, 'w') as f:
            f.write(code)

    if args.address:
        url = "https://etherscan.io/address/{}/#code".format(args.address)
        headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            code_element = soup.find('pre', class_='js-sourcecopyarea')
            if code_element:
                source_code = code_element.text.strip()         # Source code is fetched in Unicode
                source_code = source_code.encode('utf-8')       # Source code is encoded in UTF-8 to convert it to a string
                subprocess.call(['rm', '-rf', 'inputs'])
                subprocess.call(['mkdir', 'inputs'])
                path_with_filename = "inputs/fetched_source_code.sol"
                with open(path_with_filename, 'w') as f:
                    f.write(source_code)
                args.source = path_with_filename
            else:
                print("Contract source code not found.")
        else:
            print("Failed to fetch contract source code. Status code: {}".format(response.status_code))

    # If we are given bytecode, disassemble first, as we need to operate on EVM ASM.
    if args.bytecode:
        processed_evm_file = args.source + '.evm'
        disasm_file = args.source + '.evm.disasm'
        with open(args.source) as f:
            evm = f.read()

        with open(processed_evm_file, 'w') as f:
            f.write(removeSwarmHash(evm))

        analyze(processed_evm_file, disasm_file)

        remove_temporary_file(disasm_file)
        remove_temporary_file(processed_evm_file)
        remove_temporary_file(disasm_file + '.log')
    else:
        # Compile contracts using solc
        contracts = compileContracts(args.source)               # Returns (contract path with name, corresponding binary code)
        # print(contracts)
        # If contract name is provided as a cmd-line arguement, then concatenate it with source file name, else make it None  
        contract = args.source + ':' + args.contract if args.contract else None
        # contract is set to None if it is not found in the list of contracts. If contract name is found in the list, its value remains unchanged.
        if not any(cname==contract for cname,_ in contracts):
            contract = None

        # Analyze each contract in form of (Contract name, binary code)
        for cname, bin_str in contracts:
            # Keep iterating, until you find required contract name in list
            if contract is not None and cname != contract:
                continue
            print("")
            logging.info("Contract %s:", cname)
            processed_evm_file = cname + '.evm'
            # print(processed_evm_file)
            disasm_file = cname + '.evm.disasm'
            # print(disasm_file)

            # Writing Binary code after removing Swarm Hash into processed_evm_file
            with open(processed_evm_file, 'w') as of:
                of.write(removeSwarmHash(bin_str))

            # Added shell command to create a fresh output directory on every run
            subprocess.call(['rm', '-rf', 'outputs'])
            subprocess.call(['mkdir', 'outputs'])

            # Analyze function will perform the main logic of symbolic execution on the contract
            # i.e., on processed evm bytecode file, disassembled version of the EVM bytecode file and 
            # a mapping between contract name and source file passed using SourceMap() 
            analyze(processed_evm_file, disasm_file, SourceMap(cname, args.source))

            remove_temporary_file(processed_evm_file)
            remove_temporary_file(disasm_file)
            remove_temporary_file(disasm_file + '.log')

        if global_params.STORE_RESULT:
            if ':' in cname:
                result_file = os.path.join(global_params.RESULTS_DIR, cname.split(':')[0].replace('.sol', '.json').split('/')[-1])
                with open(result_file, 'a') as of:
                    of.write("}")

if __name__ == '__main__':
    main()