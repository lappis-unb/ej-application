#/bin/bash
# This script checks if a domain is responding 200 before running Cypress tests.
# For 3 minutes, the script sends a request to the domain and verifies if it is online.
# This is necessary because after the EJ deployment, the Django server can take one or
# two minutes to become accessible.


domain=$1

if [[ ! $domain ]]; then
	echo "The first script argument must be a domain that Cypress will run tests against."
	echo "For example: ./run.sh https://ejplatform.pencillabs.tec.br"
	echo "exiting script"
	exit 1
fi

# wait the server shutdown
sleep 30

connection_retries=0
while [[ connection_retries -lt 6 ]]; do
	curl $domain/login/ -I | grep "HTTP/2 200"
	domain_returns_200=$(echo $?)

	# echo $? will print 0 if grep finds "HTTP/2 200" on curl command result.
	if [[ $domain_returns_200 = 0 ]]; then
		echo "Online domain. Executing e2e tests now."
		npm i
		npx cypress run --config baseUrl=$domain
		exit
	else
		echo "Unavailable domain. Trying again in 30 seconds..."
		let "connection_retries++"
		sleep 30
	fi
done

echo "Running tests in the requested domain was not possible. Exiting script."
