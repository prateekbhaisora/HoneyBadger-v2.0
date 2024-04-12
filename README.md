HoneyBadger
===========

<img src="https://github.com/christoftorres/HoneyBadger/blob/master/honeybadger_logo.png" width="200">

An analysis tool to detect honeypots in Ethereum smart contracts :honey_pot:. HoneyBadger is based on [Oyente](https://github.com/melonproject/oyente). Our paper can be found [here](https://arxiv.org/pdf/1902.06976.pdf).

## Quick Start

A container with the dependencies set up can be found [here](https://hub.docker.com/r/christoftorres/honeybadger/).

To open the container, install docker and run:

```
docker pull christoftorres/honeybadger && docker run -i -t christoftorres/honeybadger
```

To evaluate a simple honeypot inside the container, run:

```
python honeybadger/honeybadger.py -s honeypots/MultiplicatorX3.sol
```

and you are done!

## Custom Docker image build

```
docker build -t honeybadger .
docker run -it honeybadger:latest
```

## Full installation

### Install the following dependencies
#### solc
```
$ sudo add-apt-repository ppa:ethereum/ethereum
$ sudo apt-get update
$ sudo apt-get install solc
```

#### evm from [go-ethereum](https://github.com/ethereum/go-ethereum)

1. https://geth.ethereum.org/downloads/ or
2. By from PPA if your using Ubuntu
```
$ sudo apt-get install software-properties-common
$ sudo add-apt-repository -y ppa:ethereum/ethereum
$ sudo apt-get update
$ sudo apt-get install ethereum
```

#### [z3](https://github.com/Z3Prover/z3/releases) Theorem Prover version 4.7.1.

Download the [source code of version z3-4.7.1](https://github.com/Z3Prover/z3/releases/tag/z3-4.7.1)

Install z3 using Python bindings

```
$ python scripts/mk_make.py --python
$ cd build
$ make
$ sudo make install
```

#### [Requests](https://github.com/kennethreitz/requests/) library

```
pip install requests
```

#### [web3](https://github.com/pipermerriam/web3.py) library

```
pip install web3
```

### Evaluate Ethereum smart contract honeypot

```
python honeybadger.py -s <contract filename>
```

Run ```python honeybadger.py --help``` for a complete list of options.

### An alternate manual way of installation

#### Solidity Compiler (solc)

1. Download the solc executable binary from [here](https://github.com/ethereum/solidity/releases). e.g. Download ``solc-static-linux`` for ``Ubuntu 22.04 LTS`` or above. 

2. Move the executable solc binary to a directory in your system's PATH environment variable *(This allows you to run solc from any directory in your terminal)* as:

```sh
cd ~/Downloads/
sudo mv solc-static-linux /usr/local/bin/
sudo chmod +x /usr/local/bin/solc-static-linux
```

3. *(Optional Step)* Rename the binary to solc and verify installation as:

```sh
cd /usr/local/bin/
sudo mv solc-static-linux solc
solc --version
```

#### Ethereum Virtual Machine (EVM) using geth-tools


1. Download the appropriate get binary for your system from [here](https://github.com/ethereum/go-ethereum/releases/tag/v1.8.6).

2. Ensure that you have GoLang installed.

3. Build evm v1.8.6 from source using ``make all`` command.

#### [z3](https://github.com/Z3Prover/z3/releases) Theorem Prover version 4.7.1

1. Download the source code from [here](https://github.com/Z3Prover/z3/releases/tag/z3-4.7.1) and extract the contents. e.g. Download ``Source code (zip)`` for ``Ubuntu 22.04 LTS`` or above and then extract its contents.

2. Ensure that you have python2 installed on your system. If not, install and verify as:

```sh
sudo apt-get update
sudo apt-get install python2.7
sudo ln -s /usr/bin/python2.7 /usr/bin/python
python --version
```

3. Install z3 using Python binding as:

```sh
cd ~/Downloads/z3-z3-4.7.1
python scripts/mk_make.py --python
cd build
make
```

4. Move it to your system libraries as:

```sh
sudo mv ~/Downloads/z3-z3-4.7.1/ /usr/local/lib
```

5. Add the following line to ``~/.bashrc``:

``export LD_LIBRARY_PATH=/usr/local/lib/z3-z3-4.7.1/build:$LD_LIBRARY_PATH``

#### Python libraries

1. Ensure that you have python2 venv installed on your system. If not, install as:

```sh
sudo apt install python-pip
sudo apt install python2-dev
```

2. Then install all the Python dependencies as:

```sh
pip2 install requests
pip2 install sha3
```

### Evaluate Ethereum smart contract honeypots

```sh
cd ~/Desktop/
git clone git@github.com:prateekbhaisora/HoneyBadger-v2.0.git
cd ~/Desktop/HoneyBadger-v2.0/
python honeybadger/honeybadger.py -s <path to contract filename>
```

Run ```python honeybadger.py --help``` for a complete list of options.