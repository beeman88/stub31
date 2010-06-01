.echo off

IF "%1"=="" (
echo "usage: curl_stub port trackingID user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)

IF "%2"=="" (
echo "usage: curl_stub port trackingID user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)

IF "%5"=="" (
echo "usage: curl_stub port trackingID user password resource"
echo "curl_stub 8080 abc42b0d-d110-4f5c-ac79-d3aa11bd20cb user password tradingAccounts(salesInvoices)"
GOTO :EOF
)


IF "%5"=="tradingAccounts" set select="name,customerSupplierFlag"
IF "%5"=="salesInvoices" set select="tradingAccount,customerReference"

IF "%1"=="8080" GOTO LINK2
IF "%1"=="8081" GOTO NOLINK
IF "%1"=="8083" GOTO NOLINK
IF "%1"=="8084" GOTO NOLINK
IF "%1"=="8090" GOTO LINK2
IF "%1"=="8095" GOTO 8095
IF "%1"=="8097" GOTO NOLINK
IF "%1"=="8099" GOTO NOLINK
IF "%1"=="8105" GOTO LINK2
IF "%1"=="9050" GOTO 9050
IF "%1"=="9060" GOTO NOLINK
IF "%1"=="9070" GOTO NOLINK
IF "%1"=="9075" GOTO NOLINK
IF "%1"=="9080" GOTO NOLINK
IF "%1"=="9085" GOTO NOLINK
IF "%1"=="9090" GOTO NOLINK
IF "%1"=="9097" GOTO NOLINK


REM authorization fail 401
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post customer new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingID=%2&runName=%5&runStamp=2010-10-14T08:51:02"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF

:NOLINK

REM authorization fail 401
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingID=%2&runName=%5&runStamp=2010-10-14T08:51:02"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')


GOTO EOF

:LINK2

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=name,customerSupplierFlag

REM post 2 customer new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_1.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingID=%2&runName=customers&runStamp=2010-10-14T08:51:02"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF

:8095

REM authorization fail 401
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM authorization request OK
curl -v http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all customers
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post customer new links
curl -v -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -X POST http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingID=%2&runName=%5&runStamp=2010-10-14T08:51:02

REM sync request in progress
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF

:9050

REM authorization request OK
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-

REM get count linked invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked?count=0

REM get count all invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?count=0

REM get all invoices
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5?select=%select%

REM post 5 invoice new links
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_1.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_2.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_3.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked
curl -v -u%3:%4 -X POST -d @C:\Python31\%1\link_post_request_4.xml -H "Content-Type: application/atom+xml; charset=utf-8" http://localhost:%1/sdata/billingboss/crmErp/-/%5/$linked

REM create sync request
curl -v -u%3:%4 -X POST -d "<entry><id/><title/><updated/><payload><digest/></payload></entry>" -H "Content-Type: application/atom+xml; charset=utf-8" "http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource?trackingID=%2&runName=%5&runStamp=2010-10-14T08:51:02"

REM sync request in progress
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM sync feed
curl -v -u%3:%4 http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

REM delete sync request
curl -v -u%3:%4 -X DELETE http://localhost:%1/sdata/billingboss/crmErp/-/%5/$syncSource('%2')

GOTO EOF


:EOF