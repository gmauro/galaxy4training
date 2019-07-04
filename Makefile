help:
	@echo "Please use \`make <target>\` where <target> is one of"
	@echo "  apply                   configure Galaxy server"



apply: install_roles
	ansible-playbook g4t.yml

install_roles:
	ansible-galaxy install -p roles -r requirements.yml