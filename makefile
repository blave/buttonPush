build:
	sudo docker build -t iotracks/catalog:buttonpushdetect$(TAG) .
push:build
	sudo docker push iotracks/catalog:buttonpushdetect$(TAG)
