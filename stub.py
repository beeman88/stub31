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
global RECEIPTS
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
@route('/sdata/billingboss/bb/-/users('':emailEQ'')', method='GET')
def index(emailEQ):
    import base64
    log_method_start('Authentication')

    try:
        header = request.environ.get('HTTP_AUTHORIZATION','')
        method, data = header.split(None, 1)
        if method.lower() == 'basic':
            by = data.encode('ascii')
            write_to_log("encoded basic auth = %s" % by.decode('ascii'), debug)
            str2 = base64.b64decode(by)
            write_to_log("decoded basic auth = %s" % str2)
            str3 = str2.decode('ascii')
            name, pwd = str3.split(':', 1)
            write_to_log("username = %s" % name, debug)
            write_to_log("pwd = %s" % pwd, debug)

            # a user named unauthenticated would return 401, unauthorized would return 403, unsubscribed would return 402
            if name == 'unauthenticated':
                response.status = 401
                return
            elif name == 'unauthorized':
                response.status = 403
                return
            elif name == 'unsubscribed':
                response.status = 402
                return
            
    except Exception as e:
        write_to_log('Exception error is: %s' % e)
    
    response.status = 200
    response.content_type='application/atom+xml'    

    try:
        include = request.GET['include']
    except Exception:
        write_to_log('include does not exist')
    else:
        write_to_log("include = %s" % include, debug)
        write_to_log("returning bookkeeping clients", debug)

    return login_feed()

# 2. Get Count of linked customers, invoices
#    Return 0 linked resources
# GET request
# /sdata/billingboss/crmErp/TradingAccounts/$linked?count=0
# TODO because no tradingAccount entries are returned, the link for first, last, next page have count = 0
# compare with Sage 50 - Act! implementation
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts/$linked', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices/$linked', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/receipts/$linked', method='GET')
def index(dataset):
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
# /sdata/billingboss/crmErp/dataset/tradingAccounts?count=0

# TODO /sdata/billingboss/crmErp/dataset/tradingAccounts?select=name,customerSupplierFlag the real request?
# /sdata/billingboss/crmErp/dataset/tradingAccounts
# all customers, invoices
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/receipts', method='GET')
def index(dataset):
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
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts/$linked', method='POST')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices/$linked', method='POST')
@route('/sdata/billingboss/crmErp/:dataset/receipts/$linked', method='POST')
def index(dataset):
    global debug
    log_method_start('Post new links')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    if request.url.find(TRADING_ACCOUNTS) > 0:
        return post_link_resource(TRADING_ACCOUNTS)
    elif request.url.find(SALES_INVOICES) > 0: 
        return post_link_resource(SALES_INVOICES)
    elif request.url.find(RECEIPTS) > 0:
        return post_link_resource(RECEIPTS)
    else:
        response.status = 404
        write_to_log("Error Invalid Resource")
        return sdata_link_post_error()

# 6. Create sync request
# POST
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts/$syncSource', method='POST')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices/$syncSource', method='POST')
@route('/sdata/billingboss/crmErp/:dataset/receipts/$syncSource', method='POST')
def index(dataset):
    global debug
    log_method_start('Create sync request')

    if authentication() != "Authenticated":
        return "Access Denied"    

    try:
        trackingID = request.GET['trackingID']
    except Exception:
        write_to_log('Error trackingID does not exist')
        return
    else:
        write_to_log('trackingID = {0}'.format(trackingID), debug)

    try:
        runName = request.GET['runName']
    except Exception:
        write_to_log('runName does not exist')
        return
    else:
        write_to_log('runName = {0}'.format(runName))

    try:
        runStamp = request.GET['runStamp']
    except Exception:
        write_to_log('runStamp does not exist')
        return
    else:
        write_to_log('runStamp = {0}'.format(runStamp))

    write_to_log('202 Accepted')
    response.status = 202
    response.content_type='application/xml'
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + trackingID + "')"
    return sdata_sync_accepted()

# First request return sync in progress, second request returns feed
# 7a. Request status of sync request (In progress)
# 7b. Request status of sync request (Complete)
# GET on location of previous request
# /sdata/billingboss/crmErp/dataset/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts/$syncSource('':trackingID'')', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices/$syncSource('':trackingID'')', method='GET')
@route('/sdata/billingboss/crmErp/:dataset/receipts/$syncSource('':trackingID'')', method='GET')
def index(dataset, trackingID):
    global in_progress_count 
    global in_progress_reqs
    global debug
    
    log_method_start('Request status of sync')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    write_to_log('tracking id = {0}'.format(trackingID), debug)
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
        return sdata_sync_feed(trackingID)

# 8. Delete (finish) sync request
# DELETE request
# /sdata/billingboss/crmErp/dataset/tradingAccounts/$syncSource('abc42b0d-d110-4f5c-ac79-d3aa11bd20cb')
@route('/sdata/billingboss/crmErp/:dataset/tradingAccounts/$syncSource('':trackingID'')', method='DELETE')
@route('/sdata/billingboss/crmErp/:dataset/salesInvoices/$syncSource('':trackingID'')', method='DELETE')
@route('/sdata/billingboss/crmErp/:dataset/receipts/$syncSource('':trackingID'')', method='DELETE')
def index(dataset, trackingID):
    global debug
    log_method_start('Delete (finish) sync request')

    if authentication() != "Authenticated":
        return "Access Denied"
    
    write_to_log('tracking id = {0}'.format(trackingID), debug)
    response.status = 200
    return "DELETED"

##################################################

def login_feed():
    return read_and_log('login_feed.xml')

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
    return replace_tokens_in_feed('link_feed_all.xml')

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

            # add exception because framework sends entry tag instead of resourceName tag
            try:
                resource = payload.getElementsByTagName(TAGS_DICT[resourceName])[0]
            except Exception as e:
                write_to_log('Exception error is: %s' % e)
                resource = payload.getElementsByTagName(TAGS_DICT['entry'])[0]
            
            uuid = get_uuid_from_resource(resource)
            set_response_location(uuid)
            url = get_url_from_resource(resource)
            key = get_key_from_resource(resource)

            # create response body
            xml = sdata_link_post(resourceKind, resourceName, url, key, uuid)
                
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

def get_key_from_resource(resource):
    key = resource.attributes[TAGS_DICT['key']].value
    write_to_log(key, debug)    
    return key

def set_response_location(uuid):
    response.headers['Location'] = 'http://localhost:{0}'.format(port_number) + request.path + "('" + uuid + "')"                

# generic response to link request
def sdata_link_post(resourceKind, resourceName, url, key, uuid):
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
      <id>http://www.billingboss.com/sdata/billingboss/crmErp/-/{0}/$linked('{4}')</id>
      <title>Linked {1} {4}</title>
      <updated>2010-05-25T13:27:19.207Z</updated>
      <sdata:payload>
        <crm:{1} sdata:uuid="{4}"
          sdata:url="{2}"
          sdata:key="{3}">
        </crm:{1}>
      </sdata:payload>
    </entry>
    '''.format(resourceKind, resourceName, url, key, uuid)
    
def sdata_sync_accepted():
    write_to_log("")    
    write_to_log("request body = %s" % request.body.read())
    write_to_log("")
    return read_and_log('sync_accepted.xml')

def sdata_sync_in_progress():
    return read_and_log('sync_in_progress.xml')

# TODO What is the simply endpoint?
def sdata_sync_feed(trackingID):
    return replace_tokens_in_feed('sync_feed.xml', trackingID)
	
def replace_tokens_in_feed(filename, trackingID=''):
    global debug
    global uuids_dict
    import re
    
    feed = read_file(filename)

    # strip quotes off of tracking id parameter
    if len(trackingID) > 0:
        feed = feed.format(trackingID.strip("'"))
	
    # look for token marker 
    if feed.count(TOKEN_MARKER) > 0:
        read_uuids()
        try:
            for k, v in list(uuids_dict.items()):
                write_to_log("%s=%s" % (k, v), debug)            
                p = re.compile(r'##'+k.strip()+'##')
                feed = p.sub(v.strip(), feed)
                write_to_log(feed, debug)
                if feed.count(TOKEN_MARKER) < 1:
                    break
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
RECEIPTS = "receipts"
TOKEN_MARKER = '##'
uuids_dict = {}
TAGS_DICT = {'payload':        'sdata:payload',
             'tradingAccount': 'crm:tradingAccount',
             'salesInvoice':   'crm:salesInvoice',
             'receipt':        'crm:receipt',
             'uuid':           'sdata:uuid',
             'url':            'sdata:url',
             'key':            'sdata:key',
             'entry':          'entry'}

# initialize uuid file for the file test
# TODO get rid of hard coded port number
if port_number == "8080":
    initialize_uuids()

#read debug flag
debug = config.readline()
write_to_log('debug = {0}'.format(debug))
config.close()

run(host='localhost', port=port_number)


