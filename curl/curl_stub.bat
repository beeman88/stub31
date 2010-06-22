.echo off

IF "%1"=="" (
echo "usage: curl_stub port trackingID email password username resource "
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb email password tradingAccounts(salesInvoices, receipts, taxCodes)"
GOTO :EOF
)

IF "%2"=="" (
echo "usage: curl_stub port trackingID email password username resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb email password tradingAccounts(salesInvoices, receipts, taxCodes)"
GOTO :EOF
)

IF "%6"=="" (
echo "usage: curl_stub port trackingID email password username resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb email password tradingAccounts(salesInvoices, receipts, taxCodes)"
GOTO :EOF
)

set sp="%%20"
echo %sp%

IF "%6"=="tradingAccounts" set select="select=name,customerSupplierFlag"
IF "%6"=="salesInvoices" set select="select=tradingAccount,reference2"
IF "%6"=="receipts" set select="select=tradingAccount,originatorDocument,date,netTotal"
IF "%6"=="taxCodes" set select="select=reference2"

IF "%6"=="tradingAccounts" set syncSelect="select=name,customerSupplierFlag"
IF "%6"=="salesInvoices" set syncSelect=""
IF "%6"=="receipts" set syncSelect=""
IF "%6"=="taxCodes" set syncSelect=""

IF "%1"=="8080" GOTO LINK2
IF "%1"=="8081" GOTO NOLINK
IF "%1"=="8083" GOTO NOLINK
IF "%1"=="8084" GOTO NOLINK
IF "%1"=="8090" GOTO LINK2
IF "%1"=="8095" GOTO 8095
IF "%1"=="8097" GOTO NOLINK
IF "%1"=="8099" GOTO NOLINK
IF "%1"=="8105" GOTO LINK2
IF "%1"=="8500" GOTO LINK2
IF "%1"=="9050" GOTO 9050
IF "%1"=="9060" GOTO NOLINK
IF "%1"=="9070" GOTO NOLINK
IF "%1"=="9075" GOTO NOLINK
IF "%1"=="9080" GOTO NOLINK
IF "%1"=="9085" GOTO NOLINK
IF "%1"=="9090" GOTO NOLINK
IF "%1"=="9097" GOTO NOLINK
IF "%1"=="9500" GOTO LINK2

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/bb/-/users('email%sp%eq%sp%%3')

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6?%select%

REM post customer new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\sync_digest.xml -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource?trackingID=%2&runName=%6&runStamp=2010-10-14T08:51:02&%syncSelect%"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

GOTO EOF

:NOLINK

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/bb/-/users('email%sp%eq%sp%%3')

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6?%select%

REM create sync request
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\sync_digest.xml -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource?trackingID=%2&runName=%6&runStamp=2010-10-14T08:51:02&%syncSelect%"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')


GOTO EOF

:LINK2

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/bb/-/users('email%sp%eq%sp%%3')

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6?%select%

REM post 2 customer new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_1.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\sync_digest.xml -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource?trackingID=%2&runName=customers&runStamp=2010-10-14T08:51:02&%syncSelect%"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

GOTO EOF

:8095

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/bb/-/users('email%sp%eq%sp%%3')

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6?%select%

REM post customer new links
curl -v -u%3:%4 -X POST http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked

REM create sync request
curl -v -u%3:%4 -X POST http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource?trackingID=%2&runName=%6&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

GOTO EOF

:9050

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/bb/-/users('email%sp%eq%sp%%3')

REM get all invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6?%select%

REM post 5 invoice new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_1.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_2.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_3.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_4.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\sync_digest.xml -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource?trackingID=%2&runName=%6&runStamp=2010-10-14T08:51:02&%syncSelect%"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/%5/%6/$syncSource('%2')

GOTO EOF


:EOF