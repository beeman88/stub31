# -*- coding: utf-8 -*- 
from bottle import route, run, request, response


# globals
# global in_progress_count 
# global in_progress_reqs 

global debug
global log
global port_number
global TRADING_ACCOUNTS
global SALES_INVOICES
global TOKEN_MARKER
global uuids_dict
global TAGS_DICT

@route('/')
def index():
    return '''
<h3>This test will send the responses to synchronize new customers, invoices from billing boss to simply accounting.</h3>
<br/>
<ul>
<li>Instructions:</li>
<li>1. The port number global set in stub.py is the name of a folder that has xml files that contain responses</li>
<li>2. The xml files are copied to a new folder and modified for each test cases</li>
<li>3.</li>
<li>4.</li>
</ul>
'''

# 1. Authentication request. (includes username and password)
# - GET request
# - On success return 200 OK
# - On failure return 401 Not Authorized
@route('/sdata/billingboss/crmErp/-')
def index():
    log_method_start('Authentication')
    return authentication()

# 2. Get Count of linked customers, invoices
#    Return 0 linked resources
# GET request
# /sdata/billingboss/crmErp/TradingAccounts/$linked?count=0
# TODO because no tradingAccount entries are returned, the link for first, last, next page have count = 0
# compare with Sage 50 - Act! implementation
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$linked', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$linked', method='GET')
def index():
    global debug

    log_method_start('Count of linked resources')
    if authentication() != "Authenticated":
        return "Access Denied"    
                 
    try:
        count = request.GET['count']
    except Exception:
        write_to_log('count does not exist')
        return
    else:
        write_to_log("count = %s" % count, debug)
        write_to_log("return count linked resources", debug)
        response.content_type='application/atom+xml'    
        return sdata_link_count_linked()

# GET requests  
# 3a. Get count of all customers, invoices
# /sdata/billingboss/crmErp/-/tradingAccounts?count=0

# TODO /sdata/billingboss/crmErp/-/tradingAccounts?select=name,customerSupplierFlag the real request?
# /sdata/billingboss/crmErp/-/tradingAccounts
# all customers, invoices
@route('/sdata/billingboss/crmErp/-/tradingAccounts', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices', method='GET')
def index():
    global debug
    log_method_start('GET count of all resources or link feed')
    if authentication() != "Authenticated":
        return "Access Denied"

    response.content_type='application/atom+xml'

    # when count parameter exists, return count of all resources
    try:
        count = request.GET['count']
    except Exception:
        write_to_log('count does not exist', debug)
    else:
        write_to_log('count = {0}'.format(count), debug)
        write_to_log('return count of all resources', debug)
        return sdata_link_count_all()

    # return feed of resources
    # the select parameter specifies what fields to return is handled in the xml file
    return sdata_link_feed_all()

# 5. Post new links
# POST request
# response is one entry for Ashburton Reinforcing
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$linked', method='POST')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$linked', method='POST')
def index():
    global debug
    log_method_start('Post new links')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    if request.url.find(TRADING_ACCOUNTS) > 0:
        return post_link_resource(TRADING_ACCOUNTS)
    elif request.url.find(SALES_INVOICES) > 0: 
        return post_link_resource(SALES_INVOICES)
    else:
        response.status = 404
        write_to_log("Error Invalid Resource")
        return sdata_link_post_error()

# 6. Create sync request
# POST
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource', method='POST')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource', method='POST')
def index():
    global debug
    log_method_start('Create sync request')

    if authentication() != "Authenticated":
        return "Access Denied"    

    try:
        trackingId = request.GET['trackingId']
    except Exception:
        write_to_log('Error trackingId does not exist')
        return
    else:
        write_to_log('trackingId = {0}'.format(trackingId), debug)

    # TODO don't know why these parameters are not in request
##    try:
##        runName = request.GET['runName']
##    except Exception:
##        write_to_log('runName does not exist')
##        return
##    else:
##        write_to_log('runName = {0}'.format(runName))
##
##    try:
##        runStamp = request.GET['runStamp']
##    except Exception:
##        write_to_log('runStamp does not exist')
##        return
##    else:
##        write_to_log('runStamp = {0}'.format(runStamp))

    write_to_log('202 Accepted')
    response.status = 202
    response.content_type='application/xml'
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + trackingId + "')"
    return sdata_sync_accepted()

# First request return sync in progress, second request returns feed
# 7a. Request status of sync request (In progress)
# 7b. Request status of sync request (Complete)
# GET on location of previous request
# /sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('':tracking_id'')', method='GET')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource('':tracking_id'')', method='GET')
def index(tracking_id):
    global in_progress_count 
    global in_progress_reqs
    global debug
    
    log_method_start('Request status of sync')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    write_to_log('tracking id = {0}'.format(tracking_id), debug)
    write_to_log('in_progress_count = {0}'.format(in_progress_count), debug)

    if in_progress_count < in_progress_reqs:
        write_to_log('sync feed in progress', debug)
        in_progress_count = in_progress_count + 1
        response.status = 202
        response.content_type='application/xml'
        response.headers['Location'] = request.url
        return sdata_sync_in_progress()
    else:
        write_to_log('sync feed complete', debug)        
        in_progress_count = 0
        response.status = 200
        response.content_type='application/atom+xml'
        response.headers['Location'] = request.url
        return sdata_sync_feed(tracking_id)

# 8. Delete (finish) sync request
# DELETE request
# /sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/-/tradingAccounts/$syncSource('':tracking_id'')', method='DELETE')
@route('/sdata/billingboss/crmErp/-/salesInvoices/$syncSource('':tracking_id'')', method='DELETE')
def index(tracking_id):
    global debug
    log_method_start('Delete (finish) sync request')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    write_to_log('tracking id = {0}'.format(tracking_id), debug)
    response.status = 200
    return "DELETED"

##################################################

def sdata_link_count_linked():
    return read_and_log('link_count_linked.xml')

def read_and_log(filename):
    xml = read_file(filename)
    write_to_log(xml)
    return xml    

def sdata_link_count_all():
    return read_and_log('link_count_all.xml')

def sdata_link_feed_unlinked():
    return read_and_log('link_feed_unlinked.xml')

def sdata_link_feed_all():
    replace_tokens_in_feed('link_feed_all.xml')

def sdata_link_post_error():
    return read_file('link_post.xml')

def post_link_resource(resourceKind):
    global debug
    global TAGS_DICT
    import xml.dom.minidom        

    resourceName = resourceKind[:len(resourceKind) - 1]
    write_to_log(resourceName, debug)

    try:
        # body = request.body.read()
        # write_to_log("body = %s" % body)
        # body = to_unicode(body)
        # write_to_log("unicode body = %s" % body)

        # create an xml document from the request body        
        doc = xml.dom.minidom.parse(request.body)
        write_to_log(doc.toxml(), debug)

        try:
            # set response status and content
            response.status = 201
            response.content_type='application/atom+xml'

            # get url, uuid, key, name from xml doc
            payload = doc.getElementsByTagName(TAGS_DICT['payload'])[0]
            write_to_log(payload.toxml(), debug)
            xml = ''
            
            resource = payload.getElementsByTagName(TAGS_DICT[resourceName])[0]
            uuid = get_uuid_from_resource(resource)
            set_response_location(uuid)
            url = get_url_from_resource(resource)
            key = get_key_from_resource(resource)

            # decide what kind of xml to send back
            if resourceKind == TRADING_ACCOUNTS:
                xml = sdata_link_post_tradingAccount(url, key, uuid)
            elif resourceKind == SALES_INVOICES:
                xml = sdata_link_post_salesInvoice(url, key, uuid)
                
            write_to_uuids(key, resourceKind, uuid)

            doc.unlink()            
            write_to_log(xml)
            return xml        
        except Exception as e:
            # request body did not elements we were searching for
            # send back error status, xml file
            doc.unlink()
            response.status = 404
            write_to_log('Exception error is: %s' % e)
            return sdata_link_post_error()
    except Exception as e:
        # ended up here because request.body couldn't be parsed
        # likely because of chinese characters
        # send back xml file
        write_to_log('Exception error is: %s' % e)
        response.status = 201
        return sdata_link_post_error()        

def get_uuid_from_resource(resource):
    global debug
    global TAGS_DICT
    write_to_log(resource.toxml(), debug)        
    uuid = resource.attributes[TAGS_DICT['uuid']].value
    write_to_log(uuid, debug)
    return uuid

def get_url_from_resource(resource):
    url = resource.attributes[TAGS_DICT['url']].value
    write_to_log(url, debug)
    return url

def get_key_from_resource_new(resource):
    key = resource.attributes[TAGS_DICT['key']].value
    write_to_log(key, debug)    
    return key

def get_key_from_resource(resource):
    global debug
    url = resource.attributes[TAGS_DICT['url']].value
    write_to_log(url, debug)
    # get the key from the url between the ('...') TODO use regex
    key = url[url.index("('") + 2:url.index("')")]
    write_to_log(key, debug)
    return key

def set_response_location(uuid):
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + uuid + "')"                

def sdata_link_post_tradingAccount(url, key, uuid):
    return '''
    <entry xmlns:xs="http://www.w3.org/2001/XMLSchema" 
           xmlns:cf="http://www.microsoft.com/schemas/rss/core/2005" 
           xmlns="http://www.w3.org/2005/Atom" 
           xmlns:sdata="http://schemas.sage.com/sdata/2008/1" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
           xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" 
           xmlns:sme="http://schemas.sage.com/sdata/sme/2007" 
           xmlns:http="http://schemas.sage.com/sdata/http/2008/1" 
           xmlns:sc="http://schemas.sage.com/sc/2009" 
           xmlns:crm="http://schemas.sage.com/crmErp/2008">
      <id>http://www.billingboss.com/sdata/billingboss/crmErp/-/tradingAccounts/$linked('{2}')</id>
      <title>Linked account {2}</title>
      <updated>2010-05-25T13:27:19.207Z</updated>
      <sdata:payload>
        <crm:tradingAccount sdata:uuid="{2}"
          sdata:url="{0}"
          sdata:key="{1}">
        </crm:tradingAccount>
      </sdata:payload>
    </entry>
    '''.format(url, key, uuid)

def sdata_link_post_salesInvoice(url, key, uuid):
    return '''
    <entry xmlns:xs="http://www.w3.org/2001/XMLSchema" 
           xmlns:cf="http://www.microsoft.com/schemas/rss/core/2005" 
           xmlns="http://www.w3.org/2005/Atom" 
           xmlns:sdata="http://schemas.sage.com/sdata/2008/1" 
           xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
           xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/" 
           xmlns:sme="http://schemas.sage.com/sdata/sme/2007" 
           xmlns:http="http://schemas.sage.com/sdata/http/2008/1" 
           xmlns:sc="http://schemas.sage.com/sc/2009" 
           xmlns:crm="http://schemas.sage.com/crmErp/2008">
      <id>http://www.billingboss.com/sdata/billingboss/crmErp/-/salesInvoices/$linked('{2}')</id>
      <title>Linked invoice {2}</title>
      <updated>2010-05-25T13:27:19.207Z</updated>
      <sdata:payload>
        <crm:salesInvoice sdata:uuid="{2}"
          sdata:url="{0}"
          sdata:key="{1}" >
        </crm:salesInvoice>
      </sdata:payload>
    </entry>
    '''.format(url, key, uuid)    
    
def sdata_sync_accepted():
    return read_and_log('sync_accepted.xml')

def sdata_sync_in_progress():
    return read_and_log('sync_in_progress.xml')

# TODO What is the simply endpoint?
def sdata_sync_feed(tracking_id):
	replace_tokens_in_feed('sync_feed.xml', tracking_id)
	
def replace_tokens_in_feed(filename, tracking_id=''):
    global debug
    global uuids_dict
    import xml.dom.minidom
    feed = read_file(filename)

    if len(tracking_id) > 0:
        feed = feed.format(tracking_id.strip("'"))
	
    # look for token marker 
    if feed.count(TOKEN_MARKER) > 0:
        read_uuids()
        try:
            doc = xml.dom.minidom.parseString(feed)
            entries = doc.getElementsByTagName("entry")
            for entry in entries:
                if feed.count(TOKEN_MARKER) < 1:
                    break
                
                elId = entry.getElementsByTagName("id")[0]
                url = elId.firstChild.data
                key = url[url.index("('") + 2:url.index("')")]
                token = TOKEN_MARKER + key + TOKEN_MARKER
                write_to_log('token = %s' % token, debug)

                write_to_log("Length : %d" % len (uuids_dict), debug)
                for k, v in list(uuids_dict.items()):
                    write_to_log("%s=%s" % (k, v), debug)
                feed = feed.replace(token, uuids_dict[key].strip())
        except Exception as e:
            write_to_log('Exception error is: %s' % e)        
		
    write_to_log(feed)		
    return feed	

def read_file(filename):
    global debug
    import os.path

    write_to_log('read file {0}'.format(filename), debug)    
    write_to_log('port = {0}'.format(port_number), debug)
    path_filename = os.path.join(str(port_number), filename)
    if debug == "1":
        write_to_log('path and filename = {0}'.format(path_filename))
    f = open(path_filename, 'r')
    xml = f.read()
    write_to_log(xml, debug)
    f.close()
    return xml

def write_to_log(line, flag="1"):
    if flag[0] == "1":
        log.write(line + '\n')

def log_method_start(line):
    write_to_log('')
    write_to_log(line)
    write_to_log(request.url)

def authentication():
    #TODO moving to Python 3 changed request.auth
    # if not request.auth:
        # if debug == "1":
            # write_to_log('401 Not authenticated')
        # response.status = 401
        # return "Access denied."

    write_to_log('200 OK', debug)
    response.status = 200
    return "Authenticated"

def write_to_uuids(key, resourceType, uuid):
    global debug
    global uuids_dict
    read_uuids()

    if key not in uuids_dict:
        write_to_log("write_to_uuids", debug)
        uuids_filename = os.path.join('data', 'uuids.xml')
        uuids = open(uuids_filename, 'a')
        line = key+","+resourceType+","+uuid
        write_to_log(line, debug)
        uuids.write(line+"\n")
        uuids.close()

def read_uuids():
    global debug
    global uuids_dict
    uuids_dict = {}
    uuids_filename = os.path.join('data', 'uuids.xml')
    uuids = open(uuids_filename, 'r')
    for line in uuids:
        write_to_log(line, debug)
        fields = line.split(',')
        write_to_log(fields[0]+" "+fields[1]+" "+fields[2], debug)
        uuids_dict[fields[0]] = fields[2]

    for k, v in list(uuids_dict.items()):
        write_to_log("%s=%s" % (k, v), debug)

    uuids.close()

def initialize_uuids():
    uuids_filename = os.path.join('data', 'uuids.xml')
    uuids = open(uuids_filename, 'w')
    uuids.close()

def to_unicode(obj, encoding='utf-8'):
    if isinstance(obj, str):
        write_to_log("obj is basestring")
        if not isinstance(obj, str):
            write_to_log("obj is not unicode")
            obj = str(obj, encoding)
    return obj    

# bottom

# input port number
import csv
import os.path
port_number = input("Enter port number == folder where xml responses stored: ")

# open log file
log_filename = os.path.join(str(port_number), 'log.txt')
log = open(log_filename, 'w')

config_filename = os.path.join(str(port_number), 'config.csv')
config = open(config_filename, 'r')

# initialize
in_progress_count = 0
in_progress_reqs = 1
TRADING_ACCOUNTS = "tradingAccounts"
SALES_INVOICES = "salesInvoices"
TOKEN_MARKER = '##'
uuids_dict = {}
TAGS_DICT = {'payload':        'sdata:payload',
             'tradingAccount': 'crm:tradingAccount',
             'salesInvoice':   'crm:salesInvoice',
             'uuid':           'sdata:uuid',
             'url':            'sdata:url',
             'key':            'sdata:key'}

# initialize uuid file for the file test
# TODO get rid of hard coded port number
if port_number == "8080":
    initialize_uuids()

#read debug flag
debug = config.readline()
write_to_log('debug = {0}'.format(debug))
config.close()

run(host='localhost', port=port_number)

