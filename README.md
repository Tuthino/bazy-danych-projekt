# Requirements
In order to run this application, you need to have docker-compose installed. If you are using Ubuntu can do it with this tutorial:
[Ubuntu docker-compose install](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04)


## Setup
### Instalation
Check the `docker-compose.yaml` to make sure that everything is set as you want it to be (mostly postgres database env)

Make sure that credentials in the `docker-compose.yaml` are the same as in the `DATABASES` section of the `itsm/settings.py` file
In the first run, you need to use the admin credentials, because it has full right to the database, the tables will be created and new user named `application`
#### Setting up the TLS and adding our CA to the browser (testing only, because we are using self-signed cert)
Create the TLS cert:
```bash
mkdir -p db-init/ssl
cd db-init/ssl

# Generate Root CA (if needed)
openssl req -new -x509 -days 365 -nodes -out rootCA.crt -keyout rootCA.key -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=PostgreSQL"

# Generate Server Key and Certificate
openssl req -new -nodes -out server.csr -keyout server.key -subj "/C=US/ST=State/L=City/O=Organization/OU=IT/CN=itsm-postgres"
openssl x509 -req -in server.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out server.crt -days 365

# Change the owner to 999, because this is the postgres user UID in the container
sudo chown 999:999 server.key
chmod 600 server.key
cd ../..

mkdir -p django-certs
cd django-certs

# Generate a Root CA Private Key
openssl genpkey -algorithm RSA -out rootCA.key

# Create a Root CA Certificate (Valid for 10 years)
openssl req -x509 -new -nodes -key rootCA.key -sha256 -days 3650 -out rootCA.crt -subj "/C=US/ST=State/L=City/O=MyCompany/OU=IT/CN=MyCompany Root CA"

openssl genpkey -algorithm RSA -out django.key

cat > openssl.cnf <<EOF
[req]
default_bits       = 2048
prompt             = no
default_md         = sha256
distinguished_name = dn
req_extensions     = v3_req

[dn]
C  = US
ST = State
L  = City
O  = MyCompany
OU = IT
CN = 127.0.0.1

[v3_req]
subjectAltName = @alt_names

[alt_names]
IP.1 = 127.0.0.1
DNS.1 = localhost
EOF

openssl req -new -key django.key -out django.csr -config openssl.cnf

openssl x509 -req -in django.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out django.crt -days 365 -extfile openssl.cnf -extensions v3_req

cd ..
```

Add the rootCA to your browser as the authority and enable it to authenticate websites.
If needed, run the:
`sudo update-ca-trust extract` [fedora]
`sudo update-ca-certificates` [ubuntu]

Run the application using the following command:
`docker-compose up --build`

#### Setting up Django
Inside the docker container run Django makemigrations, migrate and createsuperuser commands to create Django `auth` table and check if our applications tables has been properly created:
In order to find the container, run: `docker ps`
This will give you similar output to this one:
```
CONTAINER ID   IMAGE             COMMAND                  CREATED       STATUS       PORTS                                       NAMES
3e83c9e8ab8c   itsm-web          "python manage.py ru…"   4 hours ago   Up 4 hours   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp   itsm-web-1
b27356f6e0c4   postgres:latest   "docker-entrypoint.s…"   4 hours ago   Up 4 hours   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp   itsm-postgres
```
You can refer to either the `CONTAINER ID` or the `NAMES` as the container.

Get insinde the itsm-web-1 container:

```bash
docker exec -it itsm-web-1 /bin/bash
```

And run the following commands:
```bash
# Django makemigrations to gather all models
python manage.py makemigrations

# Django migrate, to perform the migration which will create auth table and check compatibility of our self-made tables with models
# --fake-inital will check if all tables from Django models exist and are correct, if yes, it will skip table creation
# if they are incorrect it will try to create the tables.
python manage.py migrate --fake-initial

# Create Django superuser, which will help us to see database entries via Django admin dashboard
python manage.py createsuperuser
```

Exit the container and access the admin dashboard `http://127.0.0.1:8000/admin`

#### Loading the example data

Get insinde the itsm-web-1 container:
```bash
docker exec -it itsm-web-1 /bin/bash
```
Execute the following commands to load the fixtures with example data:

```bash
python manage.py loaddata ./users/fixtures/init_users.json
python manage.py loaddata ./teams/fixtures/init_teams.json
python manage.py loaddata ./teams/fixtures/init_userteams.json
python manage.py loaddata ./tickets/fixtures/ticket_types.json
python manage.py loaddata ./tickets/fixtures/ticket_statuses.json
python manage.py loaddata ./tickets/fixtures/ticket_categories.json
python manage.py loaddata ./tickets/fixtures/ticket_comments_types.json
python manage.py loaddata ./tickets/fixtures/ticket_acknowledgment_status.json
python manage.py loaddata ./equipments/fixtures/init_equipment_types.json
python manage.py loaddata ./equipments/fixtures/init_equipment_sites.json
python manage.py loaddata ./equipments/fixtures/init_equipment.json
python manage.py loaddata ./tickets/fixtures/ticket_tickets.json
```

After migration and adding fixtures, grant permissions to application for tables created by Django ecosystem:
```sql
-- Grant permissions to Django's default tables
GRANT SELECT, INSERT, UPDATE, DELETE ON 
    django_migrations, django_session, django_content_type, 
    auth_permission, auth_group, auth_group_permissions, 
    auth_user, auth_user_groups, auth_user_user_permissions, 
    django_admin_log
TO application;

-- Grant permissions on sequences related to these tables
GRANT USAGE, SELECT ON SEQUENCE 
    django_migrations_id_seq, django_content_type_id_seq, auth_permission_id_seq, 
    auth_group_id_seq, auth_group_permissions_id_seq, 
    auth_user_id_seq, auth_user_groups_id_seq, 
    auth_user_user_permissions_id_seq, django_admin_log_id_seq
TO application;

```
Once everything is initialized, close the containers using `docker-compose down`  or just Ctrl-c and change credentials in the `DATABASES` section of the `itsm/settings.py` file
to use the `application` user.
Run the application once again using `docker-compose up`
