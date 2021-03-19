import importlib
import os
import sys
import traceback
from pathlib import Path

from psycopg2 import connect
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from dj_utils.methods import get_error_message
from django.db import connections


class Command(BaseCommand):
    help = 'setting up db i.e. create db or drop db for dev purpose'

    def get_dj_utils_path(self):
        module_path = str(settings.BASE_DIR) + '/dj_utils'
        return module_path

    def drop_create_db(self, db_config, root_dir, new=0):
        db_engine = db_config['ENGINE']
        arr = db_engine.split('.')
        if len(arr):
            db_engine = arr[len(arr) - 1]

        if db_engine == 'sqlite':
            db_path = Path.as_posix(root_dir) + '/db.sqlite3'
            if os.path.exists(db_path):
                os.remove(db_path)
            return 'done'

        default_db = 'postgres'
        if db_engine == 'mysql':
            default_db = db_engine

        db_host_connection = connect(
            database=default_db,
            user=db_config['USER'],
            password=db_config['PASSWORD'],
        )
        db_host_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        if type (db_host_connection) is str:
            return db_host_connection

        db_cursor = db_host_connection.cursor()
        db_name = db_config['NAME']

        if not new:
            close_db_sessions_sql = """
            SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity
            WHERE pg_stat_activity.datname='"""+db_name+"""'
            """
            db_cursor.execute(close_db_sessions_sql)
            drop_db_sql = 'DROP DATABASE if exists {}'
            drop_db_sql = drop_db_sql.format(db_name)
            db_cursor.execute(drop_db_sql)

        create_db_sql = 'CREATE DATABASE {}'
        create_db_sql = create_db_sql.format(db_name)
        db_cursor.execute(create_db_sql)
        db_cursor.close()
        db_host_connection.close()
        print("Database " + db_config['NAME'] + " created")

    made = 0

    def re_init_migrations(self, no_make=False):
        if self.made:
            return
        importlib.import_module('del')
        cmd_str = 'makemigrations'
        if not no_make:
            call_command(cmd_str)
            self.made = 1

    reconnect_tried = 0
    def run_migrate(self, app_name='', db_key=None):
        try:
            cmd_str = 'migrate'
            if app_name and db_key:
                call_command(cmd_str, app_name, database=db_key)
                print(app_name)
            elif app_name:
                call_command(cmd_str, app_name)
            elif db_key:
                call_command(cmd_str, database=db_key)
            else:
                call_command(cmd_str)
        except:
            message = get_error_message()
            if 'does not have migrations.' in message:
                pass
            elif not self.reconnect_tried:
                if 'server closed the connection unexpectedly' in message:
                    conn = connections['default']
                    conn.connect()
                    self.reconnect_tried = 1
                    self.run_migrate(app_name, db_key)
                else:
                    raise

    def migrate_db(self, db_key, customer_apps=None):
        print('\n\nmigrating '+db_key)
        if hasattr(settings, 'SHARED_APPS'):
            shared_apps = settings.SHARED_APPS
            public_apps = settings.PUBLIC_APPS
            for app_name in shared_apps:
                app_name = app_name.replace('django.contrib.','')
                app_name = app_name.replace('rest_framework.', '')
                self.run_migrate(app_name, db_key)

            if customer_apps is not None:
                for app_name in customer_apps:
                    self.run_migrate(app_name, db_key)
                # settings.INSTALLED_APPS = shared_apps + customer_apps
            else:
                for app_name in public_apps:
                    self.run_migrate(app_name, db_key)
        else:
            self.run_migrate('', db_key)
        # call_command('migrate', database=db_key)
        # Pinter@rt5
        fixture_path = self.get_dj_utils_path()
        fixture_path += '/fixtures/data.json'
        call_command('loaddata', fixture_path, database=db_key)
        print('\ndone with '+db_key+'\n\n')

    def handle(self, *args, **kwargs):
        try:
            root_dir = settings.BASE_DIR
            no_make = False
            for db_key in settings.DATABASES:
                self.drop_create_db(settings.DATABASES[db_key], root_dir)
            self.re_init_migrations(no_make)
            if not no_make:
                for db_key in settings.DATABASES:
                    self.migrate_db(db_key)
        except:
            eg = traceback.format_exception(*sys.exc_info())
            error_message = ''
            cnt = 0
            for er in eg:
                cnt += 1
                if not 'lib/python' in er and not 'lib\site-packages' in er:
                    error_message += " " + er
            print('Error ' + error_message)
