from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    """Reset database sequences for all models in the project."""
    
    help = 'Reset database sequences for all tables to their max ID values'

    def get_tables_with_int_pk(self):
        """Get list of tables with integer primary keys."""
        tables = []
        for model in apps.get_models():
            pk_field = model._meta.pk
            # Only process tables with integer-based primary keys
            if pk_field and pk_field.get_internal_type() in ('AutoField', 'BigAutoField'):
                tables.append(model._meta.db_table)
        return tables

    def handle(self, *args, **options):
        """Execute sequence reset for all tables with integer primary keys."""
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