test:
	py.test -vx tests
initassets:
	git submodule update --init
assets:
	cd leaflet_storage/static/storage/ && git pull && make install && make vendors
cleanassets:
	rm -rf leaflet_storage/static/storage/node_modules
distfile:
	python setup.py sdist bdist_wheel
test_publish:
	twine upload -r testpypi dist/*
publish:
	twine upload dist/*
	make clean
clean:
	rm -f dist/*
	rm -rf build/*
tx_pull:
	tx pull
tx_push:
	tx push -s
compilemessages:
	cd leaflet_storage && django-admin.py compilemessages --settings tests.settings
makemessages:
	cd leaflet_storage && django-admin.py makemessages -a
