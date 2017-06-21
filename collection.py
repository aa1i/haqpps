import pickle

watch_info = []
    
vhp_13_info = { "name":'Longines VHP PC "13" Cal L1.636.4 ETA 252.611 S/N 29206563',
                "inhib":480,
                "limit":2.0,
                "int_seconds":0.0
            }

watch_info.append(vhp_13_info)

vhp_14_info = { "name":'Longines VHP Ti "14" Cal 174.? S/N 22222759',
                "inhib":480,
                "limit":2.0,
                "int_seconds":0.0
            }

watch_info.append(vhp_14_info)

vhp_16_info = { "name":'Longines VHP PC "16" Cal L1.636.4 ETA 252.611? S/N 29593258',
                "inhib":480,
                "limit":2.0,
                "int_seconds":0.0
            }

watch_info.append(vhp_16_info)


# 01 Ti
#watch='Longines VHP Ti "01" Cal 174.2 ETA 255.561'
# 02
#watch='Longines VHP "02" Cal 174.2 ETA 255.561'
# 03 PC
#watch='Longines VHP PC Cal L1.627.3'
# 05
#watch='Longines VHP "05" Cal L174 ETA 255.561(malfunctioning)'
# 06 PC S/N 28727869
#watch='Longines VHP PC "06" Cal L1.627.4 S/N 28727869'
# 08 L174.2 S/N 22091820
#watch='Longines VHP "08" Cal L174.2 ETA 255.561 S/N 22091820'
# 09
#watch='Longines VHP "09" Cal L208.2'
# 10 pc
#watch='Longines VHP PC "10" Cal L1.636.4 ETA 252.611 S/N 29615811'
# 11 lost in mail
# 12 ti un-recorded
#watch='Longines VHP ti "12" Cal TBD '
# 15 PC
#watch='Longines VHP PC "15" Cal L1.636.4 ETA ?252.531? S/N 29206269'


def get_current_watch_info():
    current = pickle.load( open( "current_watch.p", "rb" ) )
    return current

def set_current_watch( name ):
    current = get_watch_info( name )
    if current is not None:
        pickle.dump( current, open( "current_watch.p", "wb" ) )
    else:
        print("Could not locate watch info!")

def set_current_watch_intsec( name, intsec ):
    current = get_watch_info( name )
    if current is not None:
        current['int_seconds']=intsec
        pickle.dump( current, open( "current_watch.p", "wb" ) )
    else:
        print("Could not locate watch info!")

def get_watch_info( name ):
    for ind in range( len( watch_info ) ):
        #print ("ind:{0:d} name:{1:s}".format( ind, watch_info[ind]['name']))
        if name == watch_info[ind]['name']:
          return watch_info[ind]
    return None
