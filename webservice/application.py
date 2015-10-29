from aftrack import app as application
#import ssl

#context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
#context.load_cert_chain('aftrack.crt', 'aftrack.key')
if __name__=="__main__":
	#application.run(host='0.0.0.0',ssl_context=context)
	application.run()

