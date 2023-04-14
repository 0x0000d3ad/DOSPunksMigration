# Introduction
 This repo contains Python scripts to facilitate the DOS Punks migration including token validation and metadata/image migration.

# Contents
 This repo contains the following contents:

 - `data/` - Directory for supporting metadata and ABI files.
 - `DOS_Punks_metadata/` - Final production metadata.
 - `DOS_Punks_metadata_test/` - Initial metadata directory with abbreviated test data.
 - `dospunks.py` - Downloads the images and metadata from the [DOS Punks website](https://www.dospunks.xyz/).
 - `html/` - Directory for the website HTML from which we can parse the metadata.
 - `images/`- Image directory containing all the DOS Punks Images.
 - `LICENSE` - MIT license file.
 - `README.md` - This file.
 - `requirements.txt` - Required modules.
 - `validation.py` - Validates mapping between the original token ids, the migrated token ids, and the Punk IDs.

# Notes

 - Make sure you add your infura link if you wish to run `validation.py --validate`.  Substitue your infura link in the `infura_url` variable.
 - The script `dospunks.py` handles collection of metadata and images from the website:
 -- To download metadata: `python dospunks.py --metadata`
 -- To download images: `python dospunks.py --images`
 - The script `validation.py` performs token and Punk ID validation at many levels.  For details, just invoke the help menu: `python validation.py --help`

# Installation
 After cloning the repository, you will need to install the necessary python modules:

> `pip install -r requirements.txt`

# Running Scripts
 Invoke python to run the scripts:

> `python <script>.py <args>`

 For a list of command line arguments in either script, just run:

> `python <script>.py --help` 

 or

> `python <script>.py -h` 
