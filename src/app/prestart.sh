shift "$(( OPTIND -1 ))"

if $LOCAL; then
	echo "You're running Supportive Shade locally."

	echo "Sourcing virtual env"
	source ../../.venv/bin/activate

	echo "Sourcing deployment environment"
	source ../../deploy/.env

	echo "Linking config to /etc/supportive_shade/config.toml"
	mkdir -p /etc/supportive_shade
	ln -s $(readlink -f ../../deploy/config.toml) /etc/supportive_shade/config.toml

	echo "Making data directory at /var/lib/supportive_shade"
	mkdir -p /var/lib/supportive_shade

	echo "Setup complete!"
else
	echo "Sourcing virtual env"
	source /venv/bin/activate

fi

