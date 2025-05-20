from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    """Reset database sequences for all models in the project."""

    help = 'Reset database sequences for all tables to their max ID values'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset-content-types',
            action='store_true',
            help='Delete all records from django_content_type table with CASCADE and reset its identity'
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm destructive operations like resetting content types'
        )

    def get_tables_with_int_pk(self):
        """Get list of tables with integer primary keys."""
        tables = []
        for model in apps.get_models():
            pk_field = model._meta.pk
            # Only process tables with integer-based primary keys
            if pk_field and pk_field.get_internal_type() in ('AutoField', 'BigAutoField'):
                tables.append(model._meta.db_table)
        return tables

    def reset_content_type_table(self, **options):
        """
        Delete all records from django_content_type table with CASCADE and reset its identity.
        This will delete ALL related records in tables with foreign keys to django_content_type.
        """
        confirm = options.get('confirm', False)
        if not confirm:
            self.stdout.write(
                self.style.WARNING(
                    'WARNING: Resetting the django_content_type table will delete ALL content types '
                    'and CASCADE to related tables like permissions, admin logs, etc.\n'
                    'This is a destructive operation that should only be used in development.\n'
                    'To proceed, run the command with --confirm'
                )
            )
            return self.stdout.write(
                self.style.ERROR('Operation aborted. Use --confirm to proceed.')
            )
        

        with connection.cursor() as cursor:
            try:
                # TRUNCATE with CASCADE will delete all records and reset the identity
                cursor.execute('TRUNCATE TABLE django_content_type CASCADE;')

                self.stdout.write(
                    self.style.SUCCESS('Successfully reset django_content_type table with CASCADE')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to reset django_content_type table: {str(e)}'
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully reset django_content_type table with CASCADE'
                )
            )

            

    def handle(self, *args, **options):
        """Execute sequence reset for all tables with integer primary keys."""
        # Only reset content type table if explicitly requested
        if options.get('reset_content_types'):
            self.reset_content_type_table(**options)
        
        # Continue with regular sequence resets
        tables = self.get_tables_with_int_pk()
        success_count = 0
        error_count = 0

        with connection.cursor() as cursor:
            for table in tables:
                try:
                    # Reset sequence for each table
                    cursor.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{table}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {table}), 1),
                            false
                        );
                    """)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully reset sequence for {table}')
                    )
                    success_count += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Failed to reset sequence for {table}: {str(e)}'
                        )
                    )
                    error_count += 1

        # Print summary
        self.stdout.write('\nReset Sequences Summary:')
        self.stdout.write(f'Successfully reset: {success_count} tables')
        if error_count:
            self.stdout.write(
                self.style.WARNING(f'Failed to reset: {error_count} tables')
            )