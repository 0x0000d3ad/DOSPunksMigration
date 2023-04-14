#!/usr/bin/python

###########################################################################
#
# name          : dospunks.py
#
# purpose       : get does punks for migrating
#
# usage         : python dospunks.py
#
# description   :
#
###########################################################################

import json
import os
import re
import requests
import shutil

data_dir = "data"
images = "images"

url = "https://www.dospunks.xyz/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


re_rank = re.compile( r'Rank\s(\d+)', re.I )

def get_metadata() :
    data = None
    with open( "html/dospunks.html", 'r' ) as f :
        data = f.readlines()

    temp = {}
    metadata = {}
    for row in data :
        if "div" in row :
            continue

        if "href" in row :
            temp = {}
            datum = row.split( "'" )
            temp[ "link" ]  = datum[ 1 ]
            temp[ "image" ] = datum[ 5 ]

        else :
            m = re.search( re_rank, row )
            if m :
                rank = "%04u" % int( m.group( 1 ) )
                temp[ "rank" ] = rank
                metadata[ rank ] = temp

    keys = sorted( [ i for i in metadata ] )
    m2 = {}
    for key in keys :
        m2[ key ] = metadata[ key ]

    with open( os.path.join( data_dir, "all_metadata.json" ), 'w' ) as f :
        json.dump( m2, f, indent=2 )

def get_images() :
    data = None
    with open( os.path.join( data_dir, "all_metadata.json" ), 'r' ) as f :
        data = json.load( f )

    for i, row in enumerate( data ) :
        print( "%04u" % i, end="\r" )

        suffix = data[ row ][ "image" ]
        full_url = url + suffix
        
        response = requests.get( full_url, stream=True, headers=headers )
        filepath = os.path.join( images, os.path.basename( suffix ) )
        with open( filepath, 'wb' ) as f :
            shutil.copyfileobj( response.raw, f )

if __name__ == "__main__" :
    import optparse
    parser = optparse.OptionParser()
    parser.add_option( '-m', '--metadata', dest='metadata', action='store_true', help='Get metadata' )
    parser.add_option( '-i', '--images',   dest='images',   action='store_true', help='Get images' )
    ( options, args ) = parser.parse_args()

    if options.metadata :
        get_metadata() 

    if options.images :
        get_images()
