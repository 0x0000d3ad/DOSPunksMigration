#!/usr/bin/python

###########################################################################
#
# name          : validation.py
#
# purpose       : bitmask to get token id from OS dos punks for migration
#                 validate token ids by mapping, on the blockchian and metadata
#
# usage         : python validation.py
#
# description   :
# https://medium.com/coinmonks/opensea-tokenid-explained-f420401f5109
# https://cyberdoggos.medium.com/migrating-from-opensea-cfe9aab47d3
#
###########################################################################

import json
import math
import os
import pandas
import sys

from collections import Counter
from eth_utils import keccak, to_checksum_address
from urllib.request import urlopen
from web3 import HTTPProvider, Web3


data_dir = "data"
metadata_dir = "DOS_Punks_metadata_test"

URL_PRE = "https://opensea.io/assets/0x495f947276749ce646f68ac8c248420045cb7b5e/"


def get_token_id( token_id ) :
    return int( (token_id & 0x0000000000000000000000000000000000000000ffffffffffffff0000000000) >> 40 )


def get_address( token_id ) :
    return hex(token_id >> 96)


def test1() :
    token_id = 73424079983647210902572285069973579475843508985221180214989723113099915952129
    # Convert Id to Hexadecimal
    print("Hex(id)  : ", hex(token_id))

    # First 20 bytes represent maker address
    print("Maker  \t : ",hex(token_id >> 96))

    # Next 7 bytes represent nft ID
    print("NFT id \t : ",(token_id & 0x0000000000000000000000000000000000000000ffffffffffffff0000000000) >> 40)

    # Last 5 bytes represent Quantity / Supply of this Id
    print("Quantity : ",token_id & 0x000000000000000000000000000000000000000000000000000000ffffffffff)


def validate_dos_punks_ids() :
    data = None
    with open( os.path.join( data_dir, "all_metadata.json" ), 'r' ) as f :
        data = json.load( f )

    ids = []
    addresses = []
    metadata = []
    duplicates = [ 209, 207, 208, 198, 199, 210, 387, 204, 274, 201, 202, 206, 205, 208, 203, 498, 483 ]
    total = 0
    for key in data :
        link = data[ key ][ "link" ]
        temp = {}
        if "opensea" in link :
            total += 1
            token_id = int( link.replace( URL_PRE, "" ) )
            image = data[ key ][ "image" ]
            returned_id = get_token_id( token_id )
            address = get_address( token_id )
            
            temp[ "image" ] = image
            temp[ "address" ] = address
            temp[ "os_id" ] = '"' + str( token_id ) + '"'
            temp[ "os_link" ] = link
            temp[ "mapped_id" ] = returned_id 
            temp[ "punk_id" ] = int( os.path.basename( image ).replace( ".png", "" ) )

            metadata.append( temp )

#            print( data[ key ][ "link" ] )
#            print( returned_id )
#            print( image )
             
            ids.append( returned_id )

#    print( len( ids ) )
#    print( len( list( set( ids ) ) ) )

#    for dup in sorted( list( set( duplicates ) ) ) :
#        for row in metadata :
#            if row[ "id" ] == dup :
#                print( json.dumps( row ) ) 
#            
#    print( total )
    df = pandas.DataFrame( metadata )
    df.sort_values( "mapped_id" ).to_csv( os.path.join( data_dir, "metadata.csv" ), index=False )


def validate_ids( compare_len=True, most_common=True ) :
    ids = None
    with open( os.path.join( data_dir, "ids.txt" ), 'r' ) as f :
        ids = sorted( [ int( i.strip() ) for i in f.readlines() ] )

    for i in range( len( ids ) ) : 
        if i not in ids :
            print( f"--> Missing id {i}" )

    if compare_len :
        list_len = len( ids )
        set_len = len( list( set( ids ) ) )
        print( f"--> Comparing lengths - list length: {list_len}, deduped length: {set_len}" )

    if most_common :
        print( "--> Most common ids:" )
        c = Counter( ids )
        print( c.most_common() )


def validate_get_token_id_from_blockchain() :
    mapped_ids = os.path.join( data_dir, "mapped_ids.json" )
    with open( mapped_ids, 'r' ) as f :
        mff = json.load( f )

    mdata_name = os.path.join( data_dir, "metadata.xlsx" )
    df = pandas.read_excel( mdata_name )
    dff = df.to_dict( 'records' )

    for row in dff :
        key = row[ "os_id" ].replace( "\"", "" )
        if row[ "final_token_id" ] != mff[ key ] :
            print( key, row[ "final_token_id" ], mff[ key ] )


def create_metadata() :
    mdata_name = os.path.join( data_dir, "metadata.xlsx" )
    df = pandas.read_excel( mdata_name )
    dff = df.to_dict( 'records' )

    all_metadata = None
    with open( os.path.join( data_dir, "all_metadata.json" ), 'r' ) as f :
        all_metadata = json.load( f )

    ARDRIVE = "https://gpmqvddbd6fkqvzmt4lyjpjlynxdkjc7vvohfpuolfly7i7xtkcq.arweave.net/M9kKjGEfiqhXLJ8XhL0rw241JF-tXHK-jllXj6P3moU/"
    for row in dff :
        print( row[ "punk_id" ], end="\r" )
        m = {}
        attributes = []

        rank = None
        for key in all_metadata :
            if all_metadata[ key ][ "image" ] == row[ "image" ] :
                rank = int( all_metadata[ key ][ "rank" ] )

        m[ "name" ] = "DOS Punk #%u" % row[ "punk_id" ]
        m[ "image" ] = "%s%s" % ( ARDRIVE, os.path.basename( row[ "image" ] ) )
        m[ "address" ] = row[ "address" ]
        m[ "os_id" ] = row[ "os_id" ].replace( "\"", "" )
        m[ "os_link" ] = row[ "os_link" ]
        m[ "tokenId" ] = row[ "final_token_id" ]

        attributes.append( { "trait_type" : "rank", "value" : rank } )

        m[ "attributes" ] = attributes

        mdatapath = os.path.join( metadata_dir, "%u.json" % row[ "final_token_id" ] )

        with open( mdatapath, 'w' ) as f :
            json.dump( m, f, indent=2 )

def create_metadata_using_spreadsheet() :
    trait_keys = [ "COMMUNITY PALETTE", "NUM CHARS", "CRYPTOPUNK TYPE", "CP Trait 1", "CP Trait 2", "CP Trait 3", "CP Trait 4", "CP Trait 5", "CP Trait 6", "CP Trait 7" ]
    dpid = "DOS Punk"

    mdata_name = os.path.join( data_dir, "dospunksrarityv4_1.xlsx" )
    df = pandas.read_excel( mdata_name )
    dff = df.to_dict( 'records' )

    test_dir = "DOS_Punks_metadata_test"
    m_dir = "DOS_Punks_metadata"
    files = os.listdir( test_dir )
    metadata = []
    for filename in files :
        filepath = os.path.join( test_dir, filename )
        print( "--> Reading %s" % filepath, end="\r" )
        data = None
        with open( filepath, 'r' ) as f :
            data = json.load( f )

        punk_id = int( data[ "name" ].replace( "DOS Punk #", "" ) )
        data[ "DOSPunkId" ] = punk_id

# NOTE: removing rank to be calculated by open rarity
#        attributes = data[ "attributes" ]
#        rank = attributes[ 0 ][ "value" ]
        attributes = []
#        attributes.append( { "trait_type" : "RANK", "value" : rank } )
        for datum in dff :
            if datum[ dpid ] == punk_id :
                for t in trait_keys :
                    attributes.append( { "trait_type" : t.upper(), "value" : datum[ t ] if str( datum[ t ] ) != "nan" else "NA" } )
                break
                

        data[ "attributes" ] = attributes

        metadata.append( data )

    for datum in metadata :
        print( "--> Writing %s" % filepath, end="\r" )
        token_id = datum[ "tokenId" ]
        filepath = os.path.join( m_dir, "%u.json" % token_id )
        with open( filepath, 'w' ) as f :
            json.dump( datum, f, indent=2 )


def validate_token_ids_using_web3( contract_address="0xD1619BCAbc52DADd3068d7cDBD555a7F2d0C575b", abi_filename="data/abi.json", infura_url="<infura_link>" ) :

    # arweave url
    arweave_url = "https://xdwz76itvztyklm2iorkofvebbsjsknixkbb3eums5oiqkpyje5q.arweave.net/uO2f-ROuZ4UtmkOipxakCGSZKai6gh2SjJdciCn4STs/%u.json"

    # get data from metadata excel sheet
    mdata_name = os.path.join( data_dir, "metadata.xlsx" )
    key_token_id = "final_token_id"
    key_os_id = "os_id"
    key_p_id = "punk_id"
    df = pandas.read_excel( mdata_name )
    dff = df.to_dict( 'records' )

    # configure contract object
    abi = None
    with open( abi_filename, 'r' ) as f :
        abi = json.load( f )

    contract_address_chk = to_checksum_address( contract_address )
    web3_inst = Web3( Web3.HTTPProvider( infura_url ) )
    the_contract = web3_inst.eth.contract( address=contract_address_chk, abi=json.dumps( abi ) )

    print( "--> [ 1 ] Validate Blockchain Token ID Mapping" )
    fail = False
    token_ids = []
    for datum in dff :
        dp_id = datum[ key_token_id ]
        os_id = datum[ key_os_id ]
        p_id = datum[ key_p_id ]
#        print( os_id, dp_id )
        token_id = the_contract.functions.getTokenId( int( os_id.replace( "\"", "" ) ) ).call()
        token_ids.append( { "os_id" : os_id, "dp_id" : dp_id, "blockchain_token_mapping" : token_id, "p_id" : p_id } )
        if int( dp_id ) != int( token_id ) :
            print( f"--> MISMATCH - os_id: {os_id}, dp_id: {dp_id}, token_id: {token_id}" ) 
            fail = True

    if not fail :
        print( "--> Blockchain Token ID Validation Passed!" )

    print( "--> [ 2 ] Validate ARWeave Metadata Token ID Mapping" )
    fail = False
    for datum in token_ids :
        dp_id = datum[ "dp_id" ]
        os_id = datum[ "os_id" ]
        p_id  = datum[ "p_id" ]
        token_id = datum[ "blockchain_token_mapping" ]

        response = urlopen( arweave_url % token_id )
        json_data = json.loads( response.read() )
        metadata_id = int( json_data[ "tokenId" ] )
        punk_id = int( json_data[ "name" ].replace( "DOS Punk #", "" ) )
        if metadata_id != token_id :
            print( f"--> ID MISMATCH - os_id: {os_id}, dp_id: {dp_id}, token_id: {token_id}, metadata_id: {metadata_id}" ) 
            fail = True
        if punk_id != p_id :
            print( f"--> PUNK ID MISMATCH - os_id: {os_id}, dp_id: {dp_id}, token_id: {token_id}, punk_id: {punk_id}, p_id: {p_id}" ) 
            fail = True


    if not fail :
        print( "--> Blockchain Token ID Validation Passed!" )


if __name__ == "__main__" : 
    import optparse
    parser = optparse.OptionParser()
    parser.add_option( '-1', '--test1',       dest='test1',       action='store_true', help='Test OpenSea token parsing' )
    parser.add_option( '-m', '--metadata',    dest='metadata',    action='store_true', help='Create metadata from html data' )
    parser.add_option( '-s', '--spreadsheet', dest='spreadsheet', action='store_true', help='Add spreadsheet data to metadata' )
    parser.add_option( '-v', '--validate',    dest='validate',    action='store_true', help='Validate ids' )
    ( options, args ) = parser.parse_args()

    if options.test1 :
        test1()

    if options.metadata :
        create_metadata()

    if options.spreadsheet :
        create_metadata_using_spreadsheet()

    if options.validate :    
        print( "--> " )
        validate_dos_punks_ids()
        print( "--> Validating uniqueness and ordering of ids" )
        validate_ids()
        print( "--> Validating id's from blockchain tokenId function" )
        validate_get_token_id_from_blockchain()
        print( "--> Validating token id's using web3" )
        validate_token_ids_using_web3()
