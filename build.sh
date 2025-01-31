dnf install -y gettext
python3 -m pip install --target . -r requirements.txt
python3 -m pip install --target . psycopg[binary,pool]~=3.2
python3 manage.py compilemessages --ignore debug_toolbar --ignore django
python3 manage.py collectstatic --noinput --clear -v 1
python3 manage.py createcachetable
python3 manage.py migrate
