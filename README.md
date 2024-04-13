HoneyBadger-v2.0
===========

<img src="https://github.com/christoftorres/HoneyBadger/blob/master/honeybadger_logo.png" width="200">

This is the improved version of the Honeybadger - an analysis tool to detect honeypots :honey_pot: in Ethereum smart contracts. HoneyBadger tool was based on [Oyente](https://github.com/melonproject/oyente) and its original paper can be found [here](https://arxiv.org/pdf/1902.06976.pdf).

## How to setup the tool?

The following dependencies must be installed before one can start to use HoneyBadger-v2.0:

#### Solidity Compiler (solc)

1. Ensure that you have Snap store installed. If not, install as:

```sh
sudo apt update
sudo apt install snapd
```

2. Install solc 0.5.16 from snap store and verify installation as:

```sh
sudo snap install solc
solc --version
```

#### Ethereum Virtual Machine (EVM) using geth-tools


1. Download the appropriate geth-tools tar file for your system from [here](https://geth.ethereum.org/downloads) and extract its contents.

2. Move all the geth-tools binaries to your system path and verify installation as:

```sh
cd ~/Downloads/geth-alltools-linux-amd64-1.13.14-2bd6bd01/
mv abigen bootnode clef evm geth rlpdump /usr/local/bin/
geth --version
evm -version
```

#### [z3](https://github.com/Z3Prover/z3/releases) Theorem Prover version 4.7.1

1. Download the source code from [here](https://github.com/Z3Prover/z3/releases/tag/z3-4.7.1) and extract the contents. e.g. Download ``Source code (zip)`` for ``Ubuntu 22.04 LTS`` or above and then extract its contents.

2. Ensure that you have python2 installed on your system. If not, install and verify as:

```sh
sudo apt-get update
sudo apt-get install python2.7
sudo ln -s /usr/bin/python2.7 /usr/bin/python
python --version
```

3. Install z3 using Python binding and verify installation as:

```sh
cd ~/Downloads/z3-z3-4.7.1
python scripts/mk_make.py --python
cd build
make
sudo make install
z3 --version
```

4. Move it to your system libraries as:

```sh
sudo mv ~/Downloads/z3-z3-4.7.1/ /usr/local/lib
```

5. Add the following line to ``~/.bashrc``:

``export LD_LIBRARY_PATH=/usr/local/lib/z3-z3-4.7.1/build:$LD_LIBRARY_PATH``

#### Python libraries

1. Ensure that you have python2 and pip2 installed on your system. If not, install as:

```sh
sudo apt install python-pip
sudo apt install python2-dev
```

2. Then install all the Python dependencies as:

```sh
pip2 install requests
pip2 install sha3
```

## How to use the tool?

Clone the project from our Github repo and verify if it is working as:

```sh
cd ~/Desktop/
git clone git@github.com:prateekbhaisora/HoneyBadger-v2.0.git
cd ~/Desktop/HoneyBadger-v2.0/
python honeybadger.py --help
```

### Evaluate Ethereum smart contract honeypots

Download smart contracts or, use inbuilt datasets to analysis smart contracts as:

```sh
python honeybadger/honeybadger.py -s <path to contract filename>
```

> **<span style="color:red">**Note:**</span>** Ubuntu 22.04.4 LTS or above is preferred for using HoneyBadger-v2.0E